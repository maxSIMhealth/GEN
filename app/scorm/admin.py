from modeltranslation.admin import TabbedTranslationAdmin

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from .models import ScormPackage, ScormRegistration


def refresh(modeladmin, request, queryset):
    for item in queryset:
        item.save()


refresh.short_description = "Refresh selected items (update content type)"


def duplicate_with_file(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate(suffix="(copy)", published=False, file=True)


duplicate_with_file.short_description = "Duplicate selected items"


def sync_with_scorm_cloud(modeladmin, request, queryset):
    for item in queryset:
        item.update_details()
        messages.add_message(
            request,
            messages.SUCCESS,
            _("Successfully updated registration(s) with data from ScormCloud."),
        )


sync_with_scorm_cloud.short_description = "Sync with ScormCloud"


class ScormObjectAdmin(TabbedTranslationAdmin):
    list_filter = (
        "published",
        "section__course",
        "section",
        "author",
    )
    list_display = ("name", "item_type", "id", "section", "file", "published")
    readonly_fields = ["created", "modified", "package_id"]
    # actions = [duplicate_with_file, refresh]
    change_form_template = "admin/scorm_package_change_form.html"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "author",
                    "file",
                    "section",
                    "published",
                    "description",
                )
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    "created",
                    "modified",
                )
            },
        ),
        (
            "ScormCloud Data",
            {"fields": ("package_id",)},
        ),
    )

    def save_model(self, request, obj, form, change):
        messages.warning(
            request,
            "Please don't forget to use the 'Export into ScormCloud' action before setting item as 'Published'.",
        )
        super(ScormObjectAdmin, self).save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if "_enroll_learners" in request.POST:
            obj.enroll_learners(request)
            self.message_user(request, "Participant(s) enrolled successfully.")
            return HttpResponseRedirect(".")

        if "_export_to_scorm_cloud" in request.POST:
            obj.export_to_scorm_cloud(request)
            self.message_user(request, "Successfully exported package into ScormCloud.")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)


class ScormRegistrationAdmin(admin.ModelAdmin):
    list_filter = (
        "package_object__section",
        "learner",
    )
    list_display = ("registration_id", "package_object", "learner")
    readonly_fields = [
        "created",
        "modified",
        "activity_completion",
        "activity_success",
        "attempts",
        "completion_amount",
        "score",
        "time_tracked",
        "title",
    ]
    change_form_template = "admin/scorm_registration_change_form.html"
    actions = [sync_with_scorm_cloud]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "registration_id",
                    "learner",
                    "package_object",
                )
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    "created",
                    "modified",
                )
            },
        ),
        (
            "ScormCloud Data",
            {
                "fields": (
                    "activity_completion",
                    "activity_success",
                    "attempts",
                    "completion_amount",
                    "score",
                    "time_tracked",
                    "title",
                )
            },
        ),
    )

    def response_change(self, request, obj):
        if "_sync_with_storm_cloud" in request.POST:
            obj.update_details()
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Successfully updated registration(s) with data from ScormCloud."),
            )
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)


admin.site.register(ScormPackage, ScormObjectAdmin)
admin.site.register(ScormRegistration, ScormRegistrationAdmin)
