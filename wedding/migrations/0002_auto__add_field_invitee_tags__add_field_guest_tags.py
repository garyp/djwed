# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Invitee.tags'
        db.add_column('wedding_invitee', 'tags',
                      self.gf('tagging.fields.TagField')(default=''),
                      keep_default=False)

        # Adding field 'Guest.tags'
        db.add_column('wedding_guest', 'tags',
                      self.gf('tagging.fields.TagField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Invitee.tags'
        db.delete_column('wedding_invitee', 'tags')

        # Deleting field 'Guest.tags'
        db.delete_column('wedding_guest', 'tags')


    models = {
        'wedding.comment': {
            'Meta': {'object_name': 'Comment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Invitee']", 'null': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rsvp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.RSVP']", 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'wedding.foodoption': {
            'Meta': {'unique_together': "(('short_desc', 'venue'),)", 'object_name': 'FoodOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_desc': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'short_desc': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Venue']"})
        },
        'wedding.gift': {
            'Meta': {'object_name': 'Gift'},
            'assignment': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'received': ('django.db.models.fields.DateField', [], {}),
            'registry': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Invitee']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'thank_you_sent': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'wedding.guest': {
            'Meta': {'object_name': 'Guest'},
            'cell_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Invitee']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"})
        },
        'wedding.invitee': {
            'Meta': {'object_name': 'Invitee'},
            'association': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'full_address': ('django.db.models.fields.TextField', [], {}),
            'full_name_override': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_visited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'limited_venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Venue']", 'null': 'True', 'blank': 'True'}),
            'private_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'side': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"})
        },
        'wedding.inviteenotes': {
            'Meta': {'object_name': 'InviteeNotes'},
            'adults': ('django.db.models.fields.DecimalField', [], {'max_digits': '2', 'decimal_places': '1'}),
            'batch': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'children': ('django.db.models.fields.DecimalField', [], {'max_digits': '2', 'decimal_places': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Invitee']"}),
            'likely_site': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'or_likelihood': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'savedate': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        'wedding.pagesnippet': {
            'Meta': {'object_name': 'PageSnippet'},
            'html': ('django.db.models.fields.TextField', [], {}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'wedding.rsvp': {
            'Meta': {'unique_together': "(('guest', 'venue'),)", 'object_name': 'RSVP'},
            'food_selection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.FoodOption']", 'null': 'True', 'blank': 'True'}),
            'guest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Guest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update_source': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'prelim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.RSVPOption']", 'null': 'True'}),
            'table_assign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Table']", 'null': 'True', 'blank': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Venue']"})
        },
        'wedding.rsvpoption': {
            'Meta': {'object_name': 'RSVPOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likelihood': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'long_desc': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'short_desc': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'wedding.table': {
            'Meta': {'object_name': 'Table'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wedding.Venue']"})
        },
        'wedding.venue': {
            'Meta': {'object_name': 'Venue'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'when_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['wedding']