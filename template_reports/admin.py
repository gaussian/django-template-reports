import os
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render, redirect
import swapper

from .pptx_renderer import render_pptx

ReportDefinition = swapper.load_model("template_reports", "ReportDefinition")
ReportRun = swapper.load_model("template_reports", "ReportRun")


class ReportDefinitionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = (
        "name",
        "created",
        "modified",
    )


if not settings.TEMPLATE_REPORTS_REPORTDEFINITION_MODEL:
    admin.site.register(ReportDefinition, ReportDefinitionAdmin)


class ReportRunAdmin(admin.ModelAdmin):
    autocomplete_fields = ("report_definition",)


if not settings.TEMPLATE_REPORTS_REPORTRUN_MODEL:
    admin.site.register(ReportRun, ReportRunAdmin)


class ReportGenerationForm(forms.Form):
    report_definition = forms.ModelChoiceField(
        queryset=ReportRun.objects.all(),
        label="Report Template",
        widget=admin.widgets.AutocompleteSelect(
            ReportRun._meta.get_field("report_definition"), admin.site
        ),
    )
    context1 = forms.ChoiceField(label="Context 1", required=False)
    context2 = forms.ChoiceField(label="Context 2", required=False)
    context3 = forms.ChoiceField(label="Context 3", required=False)

    def __init__(self, *args, **kwargs):
        available_context_options = kwargs.pop("available_context_options", [])
        disable_context1 = kwargs.pop("disable_context1", False)
        super().__init__(*args, **kwargs)
        choices = [("", "---------")] + [
            (opt.pk, str(opt)) for opt in available_context_options
        ]
        self.fields["context1"].choices = choices
        self.fields["context2"].choices = choices
        self.fields["context3"].choices = choices
        if disable_context1:
            self.fields["context1"].widget.attrs["disabled"] = "disabled"


class ReportGenerationAdminMixin(admin.ModelAdmin):
    actions = ("generate_reports",)

    @admin.action(description="Generate reports for selected records")
    def generate_reports(self, request, queryset):
        selected = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(
            f"generate_reports/?ids={','.join(map(str, selected))}"
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate_reports/",
                self.admin_site.admin_view(self.generate_reports_view),
                name="generate_reports",
            ),
        ]
        return custom_urls + urls

    @staticmethod
    def get_permissible_qs(model_class, request):
        return model_class.objects.all()

    def generate_reports_view(self, request):
        ids = request.GET.get("ids")
        if not ids:
            self.message_user(request, "No records selected.", level=messages.ERROR)
            return redirect("..")
        id_list = ids.split(",")
        queryset = self.model.objects.filter(pk__in=id_list)
        available_context_options = self.get_permissible_qs(self.model, request)
        disable_context1 = queryset.exists()

        if request.method == "POST":
            form = ReportGenerationForm(
                request.POST,
                available_context_options=available_context_options,
                disable_context1=disable_context1,
            )
            if form.is_valid():
                report_def = form.cleaned_data["report_definition"]
                additional_context = {}
                if not disable_context1:
                    context1_id = form.cleaned_data.get("context1")
                    if context1_id:
                        additional_context["context1"] = available_context_options.get(
                            pk=context1_id
                        )
                context2_id = form.cleaned_data.get("context2")
                if context2_id:
                    additional_context["context2"] = available_context_options.get(
                        pk=context2_id
                    )
                context3_id = form.cleaned_data.get("context3")
                if context3_id:
                    additional_context["context3"] = available_context_options.get(
                        pk=context3_id
                    )

                for record in queryset:
                    # Build the context for the report. 'record' is always included.
                    context = {"record": record}
                    context.update(additional_context)

                    # Determine an output file path (this example uses the record's pk).
                    output_filename = f"report_{record.pk}.pptx"
                    output_path = os.path.join("generated_reports", output_filename)

                    # Render the PPTX template.
                    rendered_file = render_pptx(
                        report_def.pptx_template.path,
                        context,
                        output_path,
                    )

                    # Capture the run data in JSON (for example, store context info).
                    run_data = {
                        "context": {key: str(val) for key, val in context.items()}
                    }

                    ReportRun.objects.create(
                        report_definition=report_def,
                        run_data=run_data,
                        generated_report=rendered_file,
                    )
                self.message_user(request, "Reports generated successfully.")
                return redirect("..")
        else:
            form = ReportGenerationForm(
                available_context_options=available_context_options,
                disable_context1=disable_context1,
            )
        context = {
            "form": form,
            "title": "Generate Reports",
        }
        return render(request, "admin/generate_reports.html", context)
