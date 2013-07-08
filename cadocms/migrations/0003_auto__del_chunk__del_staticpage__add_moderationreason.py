# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Chunk'
        db.delete_table(u'cadocms_chunk')

        # Deleting model 'StaticPage'
        db.delete_table(u'cadocms_staticpage')

        # Adding model 'ModerationReason'
        db.create_table(u'cadocms_moderationreason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email_body', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'cadocms', ['ModerationReason'])


    def backwards(self, orm):
        # Adding model 'Chunk'
        db.create_table(u'cadocms_chunk', (
            ('body', self.gf('cadocms.fields.HTMLField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'cadocms', ['Chunk'])

        # Adding model 'StaticPage'
        db.create_table(u'cadocms_staticpage', (
            ('content', self.gf('cadocms.fields.HTMLField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('seo_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('seo_keywords', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('seo_title', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
        ))
        db.send_create_signal(u'cadocms', ['StaticPage'])

        # Deleting model 'ModerationReason'
        db.delete_table(u'cadocms_moderationreason')


    models = {
        u'cadocms.moderationreason': {
            'Meta': {'object_name': 'ModerationReason'},
            'email_body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'cadocms.setting': {
            'Meta': {'object_name': 'Setting'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['cadocms']