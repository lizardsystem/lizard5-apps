# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'StickyTweet'
        db.create_table('lizard_sticky_twitterized_stickytweet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('twitter_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('status_id', self.gf('django.db.models.fields.BigIntegerField')(max_length=255, null=True, blank=True)),
            ('tweet', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('media_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_sticky_twitterized', ['StickyTweet'])


    def backwards(self, orm):
        
        # Deleting model 'StickyTweet'
        db.delete_table('lizard_sticky_twitterized_stickytweet')


    models = {
        'lizard_sticky_twitterized.stickytweet': {
            'Meta': {'object_name': 'StickyTweet'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'status_id': ('django.db.models.fields.BigIntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tweet': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['lizard_sticky_twitterized']
