from io import BytesIO
import zipfile

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
import swapper

ReportDefinition = swapper.load_model("template_reports", "ReportDefinition")
ReportRun = swapper.load_model("template_reports", "ReportRun")


class AdminWithFileUrl(admin.ModelAdmin):
    @admin.display(description="File name")
    def file_name(self, obj):
        return obj.file.name.split("/")[-1]

    @admin.display(description="File link")
    def file_link(self, obj):
        return format_html(
            "<a href=' {url}' target='_blank'>{text}</a>",  # SPACE IS NEEDED!
            url=obj.file.url,
            text="Download ⬇️",
        )


class ReportDefinitionAdmin(AdminWithFileUrl):
    search_fields = ("name",)
    list_display = (
        "name",
        "created",
        "modified",
    )


if not settings.TEMPLATE_REPORTS_REPORTDEFINITION_MODEL:
    admin.site.register(ReportDefinition, ReportDefinitionAdmin)


class ReportRunAdmin(AdminWithFileUrl):
    autocomplete_fields = ("report_definition",)
    search_fields = ("report_definition__name",)

    readonly_fields = (
        "file_name",
        "report_definition",
        "created",
        "modified",
        "data",
    )

    list_display = (
        "file_name",
        "file_link",
        "report_definition",
        "created",
        "is_active",
    )

    ordering = ("-created",)

    @admin.action(description="Download selected files as ZIP")
    def download_files_as_zip(self, request, queryset):
        # Create an in-memory buffer to hold the zip archive
        buffer = BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
            for record in queryset:
                # Ensure the record has an associated file
                if record.file:
                    try:
                        # Open the file
                        record.file.open()
                        # Read the file's contents
                        file_content = record.file.read()
                        # Using record.file.name might include the full storage path.
                        zip_filename = record.file.name.split("/")[-1]
                        # Write the file into the archive
                        zip_archive.writestr(zip_filename, file_content)
                    except Exception as e:
                        # Log the error or handle it as needed
                        self.message_user(
                            request,
                            f"Failed to process file {record.file.name}: {e}",
                            level="error",
                        )
                    finally:
                        # Ensure the file is closed
                        record.file.close()

        # Rewind the buffer so it can be read from the beginning
        buffer.seek(0)

        # Create the HTTP response with the zip archive
        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
        filename = f"reports-{timestamp}.zip"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    actions = (download_files_as_zip,)


if not settings.TEMPLATE_REPORTS_REPORTRUN_MODEL:
    admin.site.register(ReportRun, ReportRunAdmin)
