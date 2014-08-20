# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'issues_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='projects', null=True, to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal(u'issues', ['Project'])

        # Adding model 'Version'
        db.create_table(u'issues_version', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'issues', ['Version'])

        # Adding model 'Milestone'
        db.create_table(u'issues_milestone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('milestone', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'issues', ['Milestone'])

        # Adding model 'Type'
        db.create_table(u'issues_type', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'issues', ['Type'])

        # Adding model 'Component'
        db.create_table(u'issues_component', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('component', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'issues', ['Component'])

        # Adding model 'Tag'
        db.create_table(u'issues_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tags', null=True, to=orm['auth.User'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'issues', ['Tag'])

        # Adding model 'Issue'
        db.create_table(u'issues_issue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_issues', null=True, to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(default='', max_length=3000, blank=True)),
            ('description_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issues', null=True, to=orm['auth.User'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('difficulty', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('progress', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issues', null=True, to=orm['issues.Project'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issues', null=True, to=orm['issues.Version'])),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issues', null=True, to=orm['issues.Milestone'])),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issues', null=True, to=orm['issues.Component'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issues', null=True, to=orm['issues.Type'])),
        ))
        db.send_create_signal(u'issues', ['Issue'])

        # Adding M2M table for field tags on 'Issue'
        m2m_table_name = db.shorten_name(u'issues_issue_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm[u'issues.issue'], null=False)),
            ('tag', models.ForeignKey(orm[u'issues.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issue_id', 'tag_id'])

        # Adding model 'Comment'
        db.create_table(u'issues_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['auth.User'])),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['issues.Issue'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=3000)),
            ('description_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'issues', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'issues_project')

        # Deleting model 'Version'
        db.delete_table(u'issues_version')

        # Deleting model 'Milestone'
        db.delete_table(u'issues_milestone')

        # Deleting model 'Type'
        db.delete_table(u'issues_type')

        # Deleting model 'Component'
        db.delete_table(u'issues_component')

        # Deleting model 'Tag'
        db.delete_table(u'issues_tag')

        # Deleting model 'Issue'
        db.delete_table(u'issues_issue')

        # Removing M2M table for field tags on 'Issue'
        db.delete_table(db.shorten_name(u'issues_issue_tags'))

        # Deleting model 'Comment'
        db.delete_table(u'issues_comment')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'issues.comment': {
            'Meta': {'object_name': 'Comment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'description_html': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': u"orm['issues.Issue']"})
        },
        u'issues.component': {
            'Meta': {'object_name': 'Component'},
            'component': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'issues.issue': {
            'Meta': {'object_name': 'Issue'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'to': u"orm['issues.Component']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_issues'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '3000', 'blank': 'True'}),
            'description_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'to': u"orm['issues.Milestone']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'progress': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'to': u"orm['issues.Project']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['issues.Tag']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'to': u"orm['issues.Type']"}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issues'", 'null': 'True', 'to': u"orm['issues.Version']"})
        },
        u'issues.milestone': {
            'Meta': {'object_name': 'Milestone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'issues.project': {
            'Meta': {'object_name': 'Project'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'projects'", 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'issues.tag': {
            'Meta': {'object_name': 'Tag'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tags'", 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'issues.type': {
            'Meta': {'object_name': 'Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'issues.version': {
            'Meta': {'object_name': 'Version'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['issues']