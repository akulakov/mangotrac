from django import forms as f
from django.forms import widgets
from django.forms.widgets import *
from django.utils.safestring import mark_safe

from issues.models import *
from shared.utils import *


class SelectAndTextInput(widgets.MultiWidget):
    """A Widget with select and text input field."""
    is_required = False
    input_fields = 1

    def __init__(self, choices=(), initial=None, attrs=None, radio=False):
        widgets = self.get_widgets(choices, initial, attrs, radio)
        super(SelectAndTextInput, self).__init__(widgets, attrs)

    def get_widgets(self, c, i, attrs, radio):
        widget = RadioSelect if radio else Select
        return [widget(attrs=attrs, choices=c), TextInput(attrs=attrs)]

    def decompress(self, value):
        return value or [None]*(self.input_fields+1)

    def format_output(self, rendered_widgets):
        return u' '.join(rendered_widgets)


class MultiSelectCreate(SelectAndTextInput):
    """Widget with multiple select and multiple input fields."""
    input_fields = 5

    def get_widgets(self, c, i, attrs, radio):
        return [SelectMultiple(attrs=attrs, choices=c)] + [TextInput(attrs=attrs) for _ in range(self.input_fields)]

    def format_output(self, lst):
        lst.insert(0, "<table border='0'><tr><td>")
        lst.insert(2, "</td><td>")
        lst.append("</td></tr></table>")
        return u''.join(lst)


#### Fields

class SelectOrCreateField(f.MultiValueField):
    """SelectAndTextField - select from a dropdown or add new using text inputs."""
    widgetcls    = SelectAndTextInput
    extra_inputs = 1

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices", ())
        initial = kwargs.pop("initial", {})
        radio = kwargs.pop("radio", False)
        fields = self.get_fields(choices, initial)
        super(SelectOrCreateField, self).__init__(fields, *args, **kwargs)
        self.widget = self.widgetcls(choices, initial, radio=radio)
        self.initial = [initial] + [u'']*self.extra_inputs
        self.required = False

    def get_fields(self, choices, initial):
        return [f.ChoiceField(choices=choices, initial=initial), f.CharField()]

    def to_python(self, value):
        return value

    def set_choices(self, choices):
        self.fields[0].choices = self.widget.widgets[0].choices = choices
        initial = choices[0][0]
        self.fields[0].initial = choices[0][0]
        self.widget.widgets[0].initial = choices[0][0]

    def compress(self, lst):
        choice, new = lst[0], lst[1].strip()
        return (new, True) if new else (choice, False)

class TagsSelectCreateField(SelectOrCreateField):
    widgetcls    = MultiSelectCreate
    extra_inputs = 6

    def get_fields(self, c, i):
        return [f.MultipleChoiceField(choices=c, initial=i)] + \
                [f.CharField() for _ in range(self.extra_inputs)]

    def compress(self, lst):
        return [lst[0]] + [x.strip() for x in lst[1:] if x.strip()] if lst else None


# FORMS

class CommentForm(BaseModelForm):
    class Meta:
        model   = Comment
        exclude = "creator issue created description_html".split()

    textarea    = f.Textarea( attrs=dict(cols=65, rows=18) )
    description = f.CharField(widget=textarea, required=False)


class IssueForm(BaseModelForm):
    class Meta:
        model   = Issue
        # exclude = "creator project tags closed description_html progress milestone component".split()
        exclude = "creator project tags description_html milestone component".split()

        # we need to set the title size here because this form is used in 'add issues' formset, and it would
        # be difficult to set size with CSS
        widgets = {
            "title"         : f.TextInput( attrs=dict(size=100) ),
            "owner"         : f.RadioSelect(),
            "status"        : f.RadioSelect(),
            "type"          : f.RadioSelect(),
            "version"       : f.RadioSelect(),
            "priority_code" : f.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """ Set choices filtered by current user, set initial values.

            TODO: change SelectOrCreateField to auto-load foreign key choices and select current one.
        """
        kwargs = copy.copy(kwargs)
        user = self.user = kwargs.pop("user", None)
        super(IssueForm, self).__init__(*args, **kwargs)

        self.fields["status"].initial            = 1
        self.fields["priority_code"].initial     = 2
        self.fields["status"].empty_label        = "none"
        self.fields["owner"].empty_label         = "none"
        self.fields["type"].empty_label          = "none"
        self.fields["version"].empty_label       = "none"
        self.fields["priority_code"].empty_label = "none"

        values = Project.obj.all().values_list("pk", "project")
        values = [(0, "none")] + list(values)
        self.fields["project_"] = SelectOrCreateField(choices=values, initial=0, radio=True)

        values = Tag.obj.all().values_list("pk", "tag")
        if values:
            self.fields["tags_"].set_choices(values)

        # set initial values
        inst = self.instance
        if inst.pk:
            if inst.project:
                self.initial["project_"] = [inst.project.pk]
            self.initial["tags_"] = [ [t.pk for t in inst.tags.all()] ]

    def clean(self):
        """ Change instance based on selections, optionally create new records from text inputs.

            TODO: change SelectOrCreateField to be properly handled by ModelForm to create db entries.
        """
        data      = self.cleaned_data
        inst      = self.instance
        proj, new = data["project_"]

        if "preview" in self.data:
            # when doing preview of description, don't create any related records and avoid saving instance
            # by raising validation error
            raise f.ValidationError("preview")

        if new:
            inst.project = Project.obj.get_or_create(project=proj)[0]
        elif int(proj):
            inst.project = Project.obj.get(pk=proj)

        # NOTE: we should only save instance when creating a new issue because many-to-many tags can only
        # be added to a saved instance; but when updating an issue, it should not be saved here because we
        # need to keep the old record in order to do a diff notification email at a later point (in
        # form_valid)
        if not inst.pk:
            inst.save()
        tags = data["tags_"]
        if tags:
            selected, new = tags[0], tags[1:]
            inst.tags = [Tag.obj.get(pk=pk) for pk in selected]  # need this in case tags were deselected
            for tag in new:
                inst.tags.add( Tag.obj.get_or_create(tag=tag)[0] )

        return data

    # fldorder = "title description status owner cc project_ priority_code progress difficulty type version tags_".split()
    fldorder = "title description progress difficulty tags_".split()
    s3widget = f.TextInput(attrs=dict(size=3))

    difficulty  = f.IntegerField(widget=s3widget, required=False, initial=0)
    project_    = SelectOrCreateField()
    tags_       = TagsSelectCreateField()
    description = f.CharField( widget=f.Textarea( attrs=dict(cols=80, rows=18) ), required=False )
    progress    = f.IntegerField(widget=s3widget, required=False, initial=0)


class OwnerStatusForm(BaseModelForm):
    """Small issue update form to be submitted along with a new comment."""
    def __init__(self, *args, **kwargs):
        super(OwnerStatusForm, self).__init__(*args, **kwargs)
        self.fields["status"].empty_label = "none"
        self.fields["owner"].empty_label  = "none"

    class Meta:
        model   = Issue
        fields  = "owner status".split()
        widgets = IssueForm.Meta.widgets


class AttachmentForm(BaseModelForm):
    class Meta:
        model = Attachment
        fields = ["file"]

    file = f.FileField(required=True)


class ReportForm(BaseModelForm):
    class Meta:
        model   = Report
        exclude = ["order", "creator"]
