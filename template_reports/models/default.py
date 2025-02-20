import swapper

from .base import BaseReportDefinition, BaseReportRun


class ReportDefinition(BaseReportDefinition):
    class Meta:
        # This makes it swappable, similar to Django’s AUTH_USER_MODEL
        swappable = swapper.swappable_setting("template_reports", "ReportDefinition")


class ReportRun(BaseReportRun):
    class Meta:
        # This makes it swappable, similar to Django’s AUTH_USER_MODEL
        swappable = swapper.swappable_setting("template_reports", "ReportRun")
