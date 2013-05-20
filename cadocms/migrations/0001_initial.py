# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StaticPage'
        db.create_table(u'cadocms_staticpage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('content', self.gf('cadocms.fields.HTMLField')()),
            ('seo_title', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('seo_keywords', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('seo_description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'cadocms', ['StaticPage'])

        # Adding model 'Setting'
        db.create_table(u'cadocms_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'cadocms', ['Setting'])


    def backwards(self, orm):
        # Deleting model 'StaticPage'
        db.delete_table(u'cadocms_staticpage')

        # Deleting model 'Setting'
        db.delete_table(u'cadocms_setting')


    models = {
        u'cadocms.setting': {
            'Meta': {'object_name': 'Setting'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'cadocms.staticpage': {
            'Meta': {'ordering': "('url',)", 'object_name': 'StaticPage'},
            'content': ('cadocms.fields.HTMLField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seo_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'seo_keywords': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'seo_title': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['cadocms']