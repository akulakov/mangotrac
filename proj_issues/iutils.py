#!/usr/bin/env python
# Imports {{{
import os, time
import sys
import logging
from os.path import join as pjoin
from datetime import date as dt_date
from datetime import datetime, timedelta
from string import ascii_lowercase
from itertools import product
from operator import attrgetter
from random import choice, randint
from collections import defaultdict
from pprint import pprint
from textwrap import dedent
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj_issues.settings")
from django.conf import settings
from django.db.models import Q
from issues.models import *
# from issues.views import 
from shared.utils import *

logger    = logging.getLogger("django")
photo_dir = os.path.join(os.path.dirname(__file__), "proj_issues", "test-photos")
# }}}

columns_table = dict(
     summary    = "name",
     product    = "project",
     time       = "created",
     changetime = "updated",
     reporter   = "creator",
     )

priorities = dict(
    minor = 2,
    major = 7,
    )

headers = "id,summary,owner,type,status,priority,product,milestone,component,version,resolution,time,changetime,reporter,keywords,cc".split(',')


def load():
    from django.core.files import File  # may need for attachments
    from django.contrib.auth.models import User, Group

    with open(arg, 'rU') as fp:
        reader = csv.reader(fp)

        for line in list(reader)[1:]:
            line = Container(**dict(zip(headers, line)))
            print("adding '%s'" % line.summary)
            if line.owner == "somebody":
                owner = None
            else:
                owner = User.objects.get(username=line.owner)
            creator = User.objects.get(username=line.reporter)

            type     = Type.obj.get_or_create(type=line.type)[0]
            closed   = line.status == "closed"
            priority = priorities.get(line.priority, 1)
            project  = Project.obj.get_or_create(project=line.product)[0]
            tags     = []
            for kw in line.keywords.split(','):
                tags.append( Tag.obj.get_or_create(tag=kw)[0] )

            created = time.strptime(line.time, "%Y-%m-%d %H:%M:%S")
            updated = time.strptime(line.changetime, "%Y-%m-%d %H:%M:%S")

            if not Issue.obj.filter(name=line.summary):
                i = Issue.obj.create(owner=owner, type=type, closed=closed, priority=priority, project=project,
                                     name=line.summary, created=created, updated=updated, creator=creator)
                i.tags = tags



if __name__ == "__main__":
    argv = sys.argv
    del argv[0]
    if argv:
        arg = argv[0]
        if arg == '-h':
            print dedent("""
                usage: iutils.py
                    """)
        else:
            load()
