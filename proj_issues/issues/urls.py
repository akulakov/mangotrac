from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from issues.views import *

urlpatterns = patterns("issues.views",
    (r"^delete-comment/(\d+)/$", "delete_comment", {}, "delete_comment"),

    (r"^update-issue/(\d+)/(delete)/$", "update_issue", {}, "update_issue"),

    (r"^update-issue/(\d+)/(closed|progress)/(on|off|\d+)/$", "update_issue", {}, "update_issue"),

    (r"^update-issue-detail/(?P<mfpk>\d+)/$", staff_member_required(UpdateIssue.as_view()), {}, "update_issue_detail"),

    (r"^reports/$", staff_member_required(ReportList.as_view()), {}, "reports"),

    (r"^create-issue/$", staff_member_required(CreateIssue.as_view()), {}, "create_issue"),

    (r"^create-report/$", staff_member_required(CreateReport.as_view()), {}, "create_report"),

    (r"^update-report/(?P<mfpk>\d+)/$", staff_member_required(UpdateReport.as_view()), {}, "update_report"),

    (r"^duplicate-report/(?P<dpk>\d+)/$", staff_member_required(DuplicateReport.as_view()), {}, "duplicate_report"),

    (r"^issue/(?P<dpk>\d+)/$", staff_member_required(ViewIssue.as_view()), {}, "issue"),

    (r"^attachments/(?P<dpk>\d+)/$", staff_member_required(AttachmentsView.as_view()), {}, "attachments"),

    # (r"^attachments/(?P<dpk>\d+)/$", staff_member_required(attachments_view), {}, "attachments"),

    (r"^update-comment/(?P<mfpk>\d+)/$", staff_member_required(UpdateComment.as_view()), {}, "update_comment"),

    (r"^add-issues/$", staff_member_required(AddIssues.as_view()), {}, "add_issues"),

    (r"^report/(?P<dpk>\d+)/$", staff_member_required(ReportView.as_view()), {}, "report"),
)
