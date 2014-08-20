"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from issues.models import *

urls = "/admin/issues/issue/ /issues/create-issue/ /issues/add-issues/ /issues/reports/ /issues/create-report/".split()

class Issues(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="ak", password='k', email="a@a.com")
        self.c = Client(enforce_csrf_checks=False)
        self.c.login(username="ak", password='k')

        Project.obj.create(project="proj1")
        Type.obj.create(type="type1")
        Status.obj.create(status="open")
        Priority.obj.create(priority=1, label='')
        Tag.obj.create(tag="tag1")

    def test_urls(self):
        for url in urls:
            resp = self.c.get(url)
            self.assertIn(resp.status_code, (200, ))

    def post(self, url, **kwargs):
        return self.c.post(url, kwargs, HTTP_ORIGIN="localhost")

    def test_create_issue(self):
        resp = self.post("/issues/create-issue/", owner=1, title="iss1", project=1, priority_code=1, difficulty=3, type=1,
                         progress   = 0,
                         project__0 = 1,
                         project__1 = '',
                         tags__1    = '1',
                         tags__2    = '',
                         tags__3    = '',
                         tags__4    = '',
                         tags__5    = '',
                         tags__6    = '',
                         )
        iss = Issue.obj.get(pk=1)
        resp = self.c.get("/issues/issue/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("iss1", resp.content)

    def test_create_report(self):
        columns = """
        title
        status"""
        filters = """
        priority_code__priority__gt = 0
        """
        group_by = """
        priority_code
        project
        """
        resp = self.post("/issues/create-report/", name="rep1", columns=columns, filters=filters, group_by=group_by)
        rep = Report.obj.get(pk=1)
        resp = self.c.get("/issues/report/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("priority", resp.content)
        self.assertIn("project", resp.content)
