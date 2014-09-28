from markdown import markdown

from django.template import loader
from django.db.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

from shared.utils import *

btn_tpl  = "<div class='%s' id='%s_%s'><img class='btn' src='%simg/admin/icon-%s.gif' /></div>"
namelink = "<a href='%s'>%s</a> <a style='float:right; font-size:0.6em;' href='%s'>edit</a>"
dellink  = "<a href='%s'>Delete</a>"



class Project(BaseModel):
    creator = ForeignKey(User, related_name="projects", blank=True, null=True)
    project = CharField(max_length=60)
    def __unicode__(self):
        return self.project
    class Meta:
        ordering = ["project"]

class Version(BaseModel):
    version = CharField(max_length=10)

    def __unicode__(self):
        return self.version
    class Meta:
        ordering = ["version"]

class Status(BaseModel):
    """Status code e.g. open / done, etc."""
    status = CharField(max_length=50)
    class Meta:
        verbose_name_plural = "Status codes"
        ordering = ("status",)

    def __unicode__(self):
        return self.status

class Priority(BaseModel):
    """Priority code e.g. 1 - highest, etc."""
    priority = IntegerField(default=0)
    label    = CharField(max_length=35, default='', blank=True)

    class Meta:
        verbose_name_plural = "Priority codes"
        ordering = ("priority",)

    def __unicode__(self):
        return u"%s - %s" % (self.priority, self.label)

class Milestone(BaseModel):
    milestone = CharField(max_length=50)
    def __unicode__(self):
        return self.milestone

class Type(BaseModel):
    type = CharField(max_length=30)

    def __unicode__(self):
        return self.type

class Component(BaseModel):
    component = CharField(max_length=30)
    def __unicode__(self):
        return self.type

class Tag(BaseModel):
    creator = ForeignKey(User, related_name="tags", blank=True, null=True)
    tag     = CharField(max_length=30)

    def __unicode__(self):
        return self.tag

    class Meta:
        ordering = ["tag"]

class Report(BaseModel):
    # url     = URLField(max_length=200)
    name     = CharField(max_length=60)
    category = CharField(max_length=40, default='', blank=True)
    comment  = CharField(max_length=200, default='', blank=True)
    creator  = ForeignKey(User, related_name="reports", blank=True, null=True)
    created  = DateTimeField(auto_now_add=True)
    updated  = DateTimeField(auto_now=True)
    group_by = TextField(max_length=5000, default='', blank=True)
    columns  = TextField(max_length=5000, default='', blank=True)
    filters  = TextField(max_length=5000, default='', blank=True)
    sort_by  = TextField(max_length=5000, default='', blank=True)

    order    = IntegerField(default=0)

    class Meta:
        ordering = ("category", "order", "name")

    def get_absolute_url(self):
        return reverse2("report", self.pk)

    def filter_list(self):
        return ', '.join( [f.strip() for f in self.filters.splitlines() if f.strip()] )

    def sort_list(self):
        return ', '.join( [f.strip() for f in self.sort_by.splitlines() if f.strip()] )

    def __unicode__(self):
        return self.name


class Issue(BaseModel):
    title            = CharField(max_length=120)
    creator          = ForeignKey(User, related_name="created_issues", blank=True, null=True)
    description      = TextField(max_length=3000, default='', blank=True)
    description_html = TextField(blank=True, null=True)

    owner            = ForeignKey(User, related_name="issues", blank=True, null=True)
    # owner            = ForeignKey(User, verbose_name="assigned to", related_name="issues", blank=True, null=True)
    # priority         = IntegerField(default=0, blank=True, null=True)
    difficulty       = IntegerField(default=0, blank=True, null=True, help_text="(integer; higher value for higher difficulty)")
    progress         = IntegerField(default=0, help_text="(percent complete, enter as a whole number without the % sign)")
    cc               = CharField(max_length=300, blank=True, null=True)

    closed           = BooleanField(default=False)
    created          = DateTimeField(auto_now_add=True)
    updated          = DateTimeField(auto_now=True)
    project          = ForeignKey(Project, related_name="issues", blank=True, null=True)
    version          = ForeignKey(Version, related_name="issues", blank=True, null=True)
    milestone        = ForeignKey(Milestone, related_name="issues", blank=True, null=True)
    status           = ForeignKey(Status, related_name="issues", blank=True, null=True)
    priority_code    = ForeignKey(Priority, verbose_name="priority", related_name="issues", blank=True, null=True)
    component        = ForeignKey(Component, related_name="issues", blank=True, null=True)
    type             = ForeignKey(Type, related_name="issues", blank=True, null=True)
    tags             = ManyToManyField(Tag, related_name="issues", blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse2("issue", dpk=self.pk)

    def save(self, *args, **kwargs):
        self.description_html = markdown(self.description)
        super(Issue, self).save(*args, **kwargs)

    def title_(self):
        """Link to view issue + link to edit."""
        link    = reverse2("issue", dpk=self.pk)
        editlnk = reverse2("update_issue_detail", mfpk=self.pk)
        return namelink % (link, self.title, editlnk)
    title_.allow_tags = True
    title_.admin_order_field = "title"

    def type_(self):
        return self.type or ''
    type_.admin_order_field = "type"

    def version_(self):
        return self.version or ''
    version_.admin_order_field = "version"

    def progress_(self):
        return loader.render_to_string("progress.html", dict(pk=self.pk))
    progress_.allow_tags = True
    progress_.admin_order_field = "progress"

    def closed_(self):
        """Closed toggle button."""
        scodes = settings.SPECIAL_STATUS_CODES
        if self.status and self.status.status in (scodes["done"], scodes["wontfix"]):
            val = "on"
        else:
            val = "off"
        return btn_tpl % ("toggle closed", 'd', self.pk, settings.STATIC_URL, val)
    closed_.allow_tags = True
    closed_.admin_order_field = "closed"

    def created_(self):
        return self.created.strftime("%b %d %Y")
    created_.admin_order_field = "created"

    def owner_(self):
        return self.owner or ''
    owner_.admin_order_field = "owner"
    owner_.short_description = "Assigned to"

    def project_(self):
        return self.project or ''
    project_.admin_order_field = "project"

    def delete_(self):
        return dellink % reverse2("update_issue", self.pk, "delete")
    delete_.allow_tags = True


class Comment(BaseModel):
    creator          = ForeignKey(User, related_name="comments", blank=True, null=True)
    issue            = ForeignKey(Issue, related_name="comments", blank=True, null=True)
    created          = DateTimeField(auto_now_add=True)
    description      = TextField(max_length=3000)
    description_html = TextField()

    class Meta:
        ordering = ["created"]

    def save(self):
        self.description_html = markdown(self.description)
        super(Comment, self).save()

    def __unicode__(self):
        return unicode(self.issue.title if self.issue else '') + " : " + self.description[:20]


class Attachment(BaseModel):
    creator = ForeignKey(User, related_name="files", blank=True, null=True)
    issue   = ForeignKey(Issue, related_name="files", blank=True, null=True)
    file    = FileField(upload_to="attachments", max_length=100, blank=True)

    def __unicode__(self):
        return unicode(self.file)
