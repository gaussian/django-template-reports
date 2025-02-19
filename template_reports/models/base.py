from django.db import models
import swapper

from .utils import get_storage


class BaseReportDefinition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    file = models.FileField(upload_to="template_reports/templates/", storage=get_storage)

    # A set of allowed models (via ContentType) for which this report may run
    # allowed_models = models.ManyToManyField(ContentType, blank=True)

    # A JSON structure describing the required context keys
    # For example: {"record": "model", "teams": "queryset", "extra_info": "string"}
    # required_keys = models.JSONField(default=dict, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


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
