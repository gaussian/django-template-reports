from django.dispatch import Signal

# Signal sent when a report is generated and a ReportRun is created.
# Provides: report_run (the ReportRun instance), context (dict), perm_user (user who triggered generation)
report_generated = Signal()
