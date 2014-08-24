# Imports {{{
from __future__ import print_function, unicode_literals, division

from pprint import pprint
from difflib import Differ
from django.http import HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import forms
from django.core.mail import send_mail
from django.template.defaultfilters import date
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from django.forms.formsets import formset_factory, BaseFormSet, all_valid
from django.forms.models import modelformset_factory
from django.db.models import Q

from shared.utils import *
from issues.models import *
from issues.forms import *

from mcbv.edit import CreateView, UpdateView, FormSetView, ModelFormSetView
from mcbv.base import TemplateView
from mcbv.detail import DetailView
from mcbv.list_custom import DetailListCreateView, ListView
# }}}

def context_processor(request):
    return dict(app_name="MangoTrac")

# add_issue delete_issue
@staff_member_required
def update_issue(request, pk, mode=None, action=None):
    """ AJAX view, toggle Closed on/off, set progress or delete an issue.

        closed toggle logic:
            done/won't fix => open
            any other value => done
    """
    issue     = Issue.obj.get(pk=pk)
    open_code = settings.SPECIAL_STATUS_CODES["open"]
    done_code = settings.SPECIAL_STATUS_CODES["done"]
    s_open    = Status.obj.filter(status=open_code).first()
    s_done    = Status.obj.filter(status=done_code).first()

    if mode == "delete":
        issue.delete()
        return redir("admin:issues_issue_changelist")
    else:
        if mode == "progress":
            val = int(action)
            setattr(issue, mode, val)
        elif mode == "closed":
            mode = "status"
            if action == "on":
                val = s_done
                status = "closed"
            else:
                val = s_open
                status = "opened"

            # title   = "Issue %s %s" % (issue, status)
            msg_tpl = "Issue '%s' was " + status + " <%s%s>\n\n%s"

            NotificationMixin().send_notification(issue, msg_tpl, make_diff=False, show_descr=False, request=request)
            setattr(issue, mode, val)
        issue.save()
        return HttpResponse('')

@staff_member_required
def delete_comment(request, pk):
    Comment.obj.get(pk=pk).delete()
    return redir(referer(request))

class NotificationMixin:
    def diff(self, oldobj, obj):
        """Create a diff of `obj` vs. `oldobj`; description is handled using difflib module."""
        difflist = []
        skip     = "description_html".split()
        nl       = '\n'

        for fld in obj._meta.fields:
            name = fld.name
            if name not in skip:
                oldval = getattr(oldobj, fld.name)
                val    = getattr(obj, fld.name)

                if name == "description":
                    olddesc = oldobj.description.splitlines(1)
                    desc    = obj.description.splitlines(1)
                    if olddesc:
                        olddesc[-1] = olddesc[-1].strip() + '\r\n'
                    if desc:
                        desc[-1] = desc[-1].strip() + '\r\n'
                    d      = Differ()
                    result = list(d.compare(olddesc, desc))

                    # note: Differ returns full(?) content when there are no changes!!!?
                    if olddesc != desc:
                        difflist.extend( [nl + "Description diff:" + nl] + result + [nl] )
                else:
                    if oldval != val:
                        difflist.append("%s: changed from '%s' to '%s'" % (fld.name, oldval, val) + nl)

        diff = ''.join(difflist)
        return diff

    def send_notification(self, obj, msg_tpl, comment_body='', show_descr=True, make_diff=True, request=None):
        """ Send notification to creator / new|old owner on issue change.
            For description, show a diff; for other fields, show what it changed from / to.
        """
        request = request or self.request
        oldobj = Issue.obj.get(pk=obj.pk) if make_diff else None
        if comment_body:
            body = comment_body
        elif oldobj:
            body = self.diff(oldobj, obj)
        elif show_descr:
            body = obj.description
        else:
            body = ''

        # from_     = "oldays@web122.webfaction.com"
        old_owner = Issue.obj.get(pk=obj.pk).owner    # if owner changed, we need to notify him
        from_     = settings.DEFAULT_FROM_EMAIL
        serv_root = request.META["HTTP_ORIGIN"]
        url       = reverse2("issue", dpk=obj.pk)
        values    = [obj.title, serv_root, url, body]
        msg       = msg_tpl % tuple(values)
        send_to   = set()
        title     = "%s (%s) #%s: %s" % (old_owner, obj.status, obj.pk, obj.title)

        send_to.add(old_owner)
        send_to.add(obj.owner)
        send_to.add(obj.creator)
        if settings.TEST_NOTIFY:
            send_to = [u.email for u in send_to if u]     # use for testing
        else:
            send_to = [u.email for u in send_to if u and u!=request.user]
        if obj.cc:
            send_to.extend(obj.cc.split())
        send_mail(title, msg, from_, send_to, fail_silently=False)


class ReportList(ListView):
    list_model = Report
    template_name = "reports.html"

class CreateReport(CreateView):
    form_model      = Report
    modelform_class = ReportForm
    template_name   = "report_form.html"

    def modelform_valid(self, modelform):
        resp = super(CreateReport, self).modelform_valid(modelform)
        self.modelform_object.update(creator=self.request.user)
        return resp


class UpdateReport(UpdateView):
    form_model      = Report
    modelform_class = ReportForm
    template_name   = "report_form.html"


class DuplicateReport(DetailView):
    detail_model = Report

    def get(self, request, *args, **kwargs):
        report = self.get_detail_object()
        report.pk = None
        report.name += " copy"
        report.save()
        return redir("update_report", report.pk)


class IssuesMixin(object):
    def add_context(self):
        return dict(bold_labels=settings.BOLD_LABELS)

    def get_success_url(self):
        """Return to view issue page on success."""
        # return reverse("admin:issues_issue_changelist") + "?status__id__exact=1&o=5.-3"
        return reverse2("issue", self.modelform_object.pk)


class UpdateIssue(IssuesMixin, UpdateView, NotificationMixin):
    form_model      = Issue
    modelform_class = IssueForm
    msg_tpl         = "Issue '%s' was updated <%s%s>\n\n%s"
    template_name   = "issue_form.html"

    def modelform_invalid(self, modelform):
        preview = None
        post = self.request.POST
        if "preview" in post:
            preview = markdown(post["description"])
        return self.get_context_data(modelform=modelform, preview=preview)

    def modelform_valid(self, modelform):
        """ If form was changed, send notification email the (new) issue owner.
            Note: at the start of the function, FK relationships are already updated in `self.object`.
        """
        if modelform.has_changed():
            self.send_notification(self.modelform_object, self.msg_tpl)
        return super(UpdateIssue, self).modelform_valid(modelform)


class CreateIssue(IssuesMixin, CreateView, NotificationMixin):
    form_model      = Issue
    modelform_class = IssueForm
    msg_tpl         = "Issue '%s' was created <%s%s>\n\n%s"
    template_name   = "issue_form.html"

    def modelform_invalid(self, modelform):
        preview = None
        post = self.request.POST
        if "preview" in post:
            preview = markdown(post["description"])
        return self.get_context_data(modelform=modelform, preview=preview)

    def modelform_valid(self, modelform):
        resp = super(CreateIssue, self).modelform_valid(modelform)
        self.modelform_object.update(creator=self.request.user)
        self.send_notification(self.modelform_object, self.msg_tpl, make_diff=False)
        return resp


class UpdateComment(UpdateView):
    form_model      = Comment
    modelform_class = CommentForm
    template_name   = "issues/comment_form.html"

    def get_success_url(self):
        return self.modelform_object.issue.get_absolute_url()


class ViewIssue(DetailListCreateView, NotificationMixin):
    """ View issue, comments and new comment form.
        When new comment is submitted, issue status / owner may also be updated.
    """
    detail_model    = Issue
    list_model      = Comment
    modelform_class = CommentForm
    related_name    = "comments"
    fk_attr         = "issue"
    msg_tpl         = "Comment was added to the Issue '%s' <%s%s>\n\n%s"
    template_name   = "issue.html"

    def modelform_get(self, request, *args, **kwargs):
        """Get issue modelform with two fields: owner and status; return both comment & issue modelforms."""
        modelform2 = OwnerStatusForm(instance=self.detail_object)

        return self.get_modelform_context_data( modelform=self.get_modelform(), modelform2=modelform2 )

    def add_context(self):
        """List of fields to display at the top of issue."""
        fields = "status owner cc project priority_code difficulty type version tags creator created updated".split()
        return dict(fields=fields)

    def modelform2_valid(self, modelform):
        """Update issue based on the small form with 2 fields."""
        if modelform.has_changed():
            issue = modelform.save(commit=False)
            self.send_notification(issue, UpdateIssue.msg_tpl)
            issue.save()

    def modelform_valid(self, modelform):
        """Add a comment; send notification email to the issue owner."""
        if modelform.has_changed():
            resp = super(ViewIssue, self).modelform_valid(modelform)
            obj  = self.modelform_object
            obj.update(creator=self.user)
            self.send_notification(obj.issue, self.msg_tpl, comment_body=obj.description)
        self.modelform2_valid( OwnerStatusForm(instance=self.detail_object, data=self.request.POST) )
        return redir(self.detail_object.get_absolute_url())


class AddIssues(IssuesMixin, FormSetView, NotificationMixin):
    """Create new issues."""
    formset_model      = Issue
    formset_form_class = IssueForm
    msg_tpl            = "New Issue '%s' was created <%s%s>\n\n%s"
    extra              = 5
    template_name      = "add_issues.html"

    def get_success_url(self):
        # can't redir to issue page because -- multiple issues
        return reverse("admin:issues_issue_changelist") + "?status__id__exact=1&o=5.-3"

    def process_form(self, form):
        issue = form.save(commit=False)
        issue.update(creator=self.request.user)
        self.send_notification(issue, self.msg_tpl, make_diff=False)


class AttachmentsView(ModelFormSetView, DetailView):
    """Create new issues."""
    detail_model       = Issue
    formset_model      = Attachment
    formset_form_class = AttachmentForm
    msg_tpl            = "New attachments '%s' were added <%s%s>\n\n%s"
    can_delete         = True
    extra              = 15
    template_name      = "attachments.html"

    def get_success_url(self):
        return self.detail_object.get_absolute_url()

    def process_form(self, form):
        file         = form.save(commit=False)
        file.creator = self.request.user
        file.issue   = self.detail_object
        file.save()

    def formset_valid(self, formset):
        """Handle deletion of attachments."""
        for form in formset:
            if form.cleaned_data.get("file"):
                if form.cleaned_data.get("DELETE"):
                    form.instance.delete()
                else:
                    self.process_form(form)
        return HttpResponseRedirect(self.get_success_url())


class ReportView(DetailView):
    detail_model  = Report
    template_name = "report.html"

    def resolve_filter_relations(self, arg_filters, kw_filters):
        """ Resolve 1to1 or MtoM filter relations (also add __in and split list of values)

            Example:
                priority_code = 1, 2 ==>
                    priority_code__priority__in=(1,2)
        """
        relation_filters = dict(
            owner         = (User, "username"),
            status        = (Status, "status"),
            priority_code = (Priority, "priority"),
            project       = (Project, "project"),
            type          = (Type, "type"),
            version       = (Version, "version"),
            tags          = (Tag, "tag"),
        )

        for flt, vals in kw_filters.items():
            vals = [v.strip() for v in vals.split(',')]
            if flt in relation_filters:
                cls, fldname = relation_filters[flt]
                kw_filters["%s__%s__in" % (flt, fldname)] = vals
                del kw_filters[flt]
            else:
                if len(vals) > 1:
                    kw_filters["%s__in" % flt] = vals
                    del kw_filters[flt]
                else:
                    kw_filters[flt] = vals[0]


    def add_context(self):
        """ Create grouped and filtered rows of issues based on GET args.
            Grouped columns are moved to the left side.

            e.g. ?group=owner.project & closed=0 & priority__gt=0
                    => group by owner, project; filter out closed and 0 priority issues
        """
        group_by = ()
        filters  = {}
        report   = self.detail_object

        # by default, use all cols
        cols = "title owner status priority_code difficulty project type version created progress tags".split()

        # get groups and filters
        group_by    = [l.strip() for l in report.group_by.splitlines() if l.strip()]
        sort_by     = [l.strip() for l in report.sort_by.splitlines() if l.strip()]
        columns     = [l.strip() for l in report.columns.splitlines() if l.strip()]
        columns     = columns or cols
        arg_filters = []
        kw_filters  = dict(
                    [(k.strip(), v.strip()) for k, v in
                        [l.split('=', 1) for l in report.filters.splitlines()
                         if '=' in l]
                   ])
        self.resolve_filter_relations(arg_filters, kw_filters)

        # move to front (or insert) group by columns
        issues         = Issue.obj.all().filter(*arg_filters, **kw_filters)
        group_by_names = [x.strip('-') for x in group_by]   # remove order reversal char

        for n in reversed(group_by_names):
            if n in columns:
                columns.remove(n)
            columns.insert(0, n)

        # make table rows
        issues   = issues.order_by( *(group_by + sort_by) )
        rows     = []
        last_row = None

        for issue in issues:
            row         = []
            ref_row     = []       # reference row, includes omitted values

            # when new group starts, subsequent columns need to show the value even if it hasn't changed
            reset_group = False

            # make row
            for n, col in enumerate(columns):
                border = col not in group_by_names      # no border for groups to make them stand out visually
                val = use_val = getattr(issue, col)
                if hasattr(val, "all"):
                    val = use_val = sjoin(val.all(), ', ')

                if last_row and col in group_by_names:
                    last = last_row[n]

                    # see note above about reset_group
                    if val != last:
                        use_val = val
                        reset_group = True
                    elif not reset_group:
                        use_val = ''

                if col in ("type", "version") and use_val is None:
                    use_val = ''
                if col == "title":
                    use_val = "<a href='%s'>%s</a>" % (reverse2("issue", issue.pk), use_val)
                if col=="created" or col=="updated":
                    use_val = date(use_val, "DATETIME_FORMAT")
                if col == "description":
                    use_val = issue.description_html

                row.append((use_val, border))
                ref_row.append(val)
            last_row = ref_row
            rows.append(row)

        headers = [Issue._meta.get_field(c).verbose_name for c in columns]
        return dict(headers=headers, rows=rows)
