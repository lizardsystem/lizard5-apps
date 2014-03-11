# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ColorMapLine.description'
        db.add_column('lizard_datasource_colormapline', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ColorMap.defaultdescription'
        db.add_column('lizard_datasource_colormap', 'defaultdescription',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ColorMapLine.description'
        db.delete_column('lizard_datasource_colormapline', 'description')

        # Deleting field 'ColorMap.defaultdescription'
        db.delete_column('lizard_datasource_colormap', 'defaultdescription')


    models = {
        'lizard_datasource.augmenteddatasource': {
            'Meta': {'object_name': 'AugmentedDataSource'},
            'augmented_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.DatasourceModel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_datasource.colorfromlatestvalue': {
            'Meta': {'object_name': 'ColorFromLatestValue'},
            'augmented_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.AugmentedDataSource']"}),
            'colormap': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.ColorMap']"}),
            'hide_from_layer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_to_add_color_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'colors_from'", 'to': "orm['lizard_datasource.DatasourceLayer']"}),
            'layer_to_get_color_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'colors_used_by'", 'null': 'True', 'to': "orm['lizard_datasource.DatasourceLayer']"})
        },
        'lizard_datasource.colormap': {
            'Meta': {'object_name': 'ColorMap'},
            'defaultcolor': ('colorful.fields.RGBColorField', [], {'max_length': '7', 'null': 'True'}),
            'defaultdescription': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_datasource.colormapline': {
            'Meta': {'ordering': "[u'minvalue', u'maxvalue']", 'object_name': 'ColorMapLine'},
            'color': ('colorful.fields.RGBColorField', [], {'max_length': '7'}),
            'colormap': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.ColorMap']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maxinclusive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'maxvalue': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mininclusive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minvalue': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'lizard_datasource.datasourcecache': {
            'Meta': {'object_name': 'DatasourceCache'},
            'datasource_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.DatasourceLayer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locationid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'lizard_datasource.datasourcelayer': {
            'Meta': {'object_name': 'DatasourceLayer'},
            'choices_made': ('django.db.models.fields.TextField', [], {}),
            'datasource_model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.DatasourceModel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'lizard_datasource.datasourcemodel': {
            'Meta': {'object_name': 'DatasourceModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'originating_app': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'lizard_datasource.percentilelayer': {
            'Meta': {'object_name': 'PercentileLayer'},
            'augmented_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_datasource.AugmentedDataSource']"}),
            'hide_from_layer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_to_add_percentile_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'percentiles_from'", 'to': "orm['lizard_datasource.DatasourceLayer']"}),
            'layer_to_get_percentile_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'percentiles_used_by'", 'to': "orm['lizard_datasource.DatasourceLayer']"}),
            'percentile': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        }
    }

    complete_apps = ['lizard_datasource']