import datetime
from io import BytesIO
from typing import Any

from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
import swapper

from template_reports.office_renderer import render_pptx, extract_context_keys

from .utils import get_storage


class BaseReportDefinition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    file = models.FileField(upload_to="template_reports/templates/", storage=get_storage)

    config = models.JSONField(
        default=dict, blank=True, help_text="Configuration JSON, including allowed models"
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @classmethod
    def filter_for_allowed_models(cls, model):
        """
        Return a queryset of ReportDefinitions that are allowed to run for the given model.
        If no model is provided, return all ReportDefinitions.
        """
        if model:
            full_model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            return cls.objects.filter(
                Q(config__allowed_models__contains=[full_model_name])
                | Q(config__allowed_models__isnull=True)
            )
        return cls.objects.all()

    def get_file_stream(self):
        self.file.seek(0)
        file_data = self.file.read()
        return BytesIO(file_data)

    def extract_context_requirements(self):
        """
        Analyze the template file and extract the context keys required to render it.
        Return a dict with:
        - simple_fields: sorted list of unique simple keys
        - object_fields: sorted list of unique object keys
        """
        file_stream = self.get_file_stream()
        return extract_context_keys(file_stream)

    def run_report(self, context, perm_user):
        """
        Run the report with the provided context.
        Save the generated report file as ReportRun.
        """

        # Get the file as a usable stream
        file_stream = self.get_file_stream()

        # Prepare an output stream to save to
        output = BytesIO()

        # Render the file
        _, errors = render_pptx(
            template=file_stream,
            output=output,
            context=context,
            perm_user=perm_user,
        )

        # Errors
        if errors:
            return errors

        # Create a Django ContentFile from the bytes
        # (create a timestamp string)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"report-{timestamp}.pptx"
        output_content = ContentFile(output.getvalue(), name=filename)

        # Save the generated report
        ReportRun = swapper.load_model("template_reports", "ReportRun")
        ReportRun.objects.create(
            report_definition=self,
            file=output_content,
            **self.get_extra_creation_kwargs(context, perm_user),
        )

        # Success
        return None

    def get_extra_creation_kwargs(self, context: dict, perm_user) -> dict[str, Any]:
        """
        Return the extra kwargs for a report run with the given context and user.
        Override this method to add more data or metadata.
        """
        return {
            "data": {
                "context": {k: str(v) for k, v in context.items()},
                "perm_user": {
                    "pk": perm_user.pk,
                    "str": str(perm_user),
                },
            }
        }


class BaseReportRun(models.Model):
    report_definition = models.ForeignKey(
        swapper.get_model_name("template_reports", "ReportDefinition"),
        on_delete=models.SET_NULL,
        null=True,
    )

    # We store the run's context and any other metadata in a JSON field.
    data = models.JSONField()

    # The generated PPTX file
    file = models.FileField(
        upload_to="template_reports/generated_reports/", storage=get_storage
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.report_definition.name} run at {self.created}"
