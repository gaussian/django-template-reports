from django.db import models
from django.contrib.contenttypes.models import ContentType


class ReportDefinition(models.Model):
    name = models.CharField(max_length=255)
    pptx_template = models.FileField(upload_to="pptx_templates/")
    # A set of allowed models (via ContentType) for which this report may run.
    allowed_models = models.ManyToManyField(ContentType, blank=True)
    # A JSON structure describing the required context keys.
    # For example: {"record": "model", "teams": "queryset", "extra_info": "string"}
    required_keys = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class ReportRun(models.Model):
    report_definition = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE)

    # We store the run’s context and any other metadata in a JSON field.
    data = models.JSONField()

    # The generated PPTX file
    generated_report = models.FileField(upload_to="generated_reports/")

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_definition.name} run at {self.created}"
