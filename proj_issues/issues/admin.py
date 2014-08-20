from django.contrib import admin
from django.conf import settings
from issues.models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ["project"]

class TagsAdmin(admin.ModelAdmin):
    list_display = ["tag"]

class TypeAdmin(admin.ModelAdmin):
    list_display = ["type"]

class StatusAdmin(admin.ModelAdmin):
    list_display = ["status"]

class PriorityAdmin(admin.ModelAdmin):
    list_display = ["priority", "label"]

class VersionAdmin(admin.ModelAdmin):
    list_display = ["version"]

class CommentAdmin(admin.ModelAdmin):
    pass
    # list_display = ["tag"]

class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["id"]

class ReportAdmin(admin.ModelAdmin):
    list_display = ["name"]

class IssueAdmin(admin.ModelAdmin):
    list_display = "id title_ owner_ status priority_code difficulty project_ type_ version_ created_ creator closed_".split()

    if settings.SHOW_PROGRESS_BAR:
        list_display.insert(-1, "progress_")
    list_filter    = "priority_code difficulty project type version tags status owner".split()
    date_hierarchy = "created"
    if settings.SEARCH_ON:
        search_fields  = "title description".split()


admin.site.register(Priority, PriorityAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag, TagsAdmin)
