import models
from django.contrib import admin
from django.contrib.auth.models import User

    
class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'building', 'abstract_entity','website',)
    list_editable = ('building', 'parent', 'abstract_entity','website',)
    prepopulated_fields = {
            'slug': ('name',)
            }
    fieldsets = (
    (None, {
        'fields': ('name', 'abstract_entity', 'parent', 'display_parent',),
    }),
    ('Contact information', {
        'fields': ('website', 'email', 'phone_number', 'fax_number',  'building', 'precise_location', 'access_note', )
    }), 
    ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('slug',),
    }),
    )

admin.site.register(models.Entity,EntityAdmin)

class PersonAdmin(admin.ModelAdmin):
    list_display = ('given_name', 'surname', 'user',)
    list_editable = ('user',)
    filter_horizontal = ('entities',)
    prepopulated_fields = {
            'slug': ('title', 'given_name', 'middle_names', 'surname',)
    }
    fieldsets = (
    ('Personal details', {
        'fields': ('title', 'given_name', 'middle_names', 'surname', 'user'),
    }),
    ('Contact information', {
        'fields': ('email', 'phone_number', 'fax_number',  'building', 'precise_location', 'access_note', )
    }), 
    ('Override contact information details', {
        'classes': ('collapse',),
        'fields': ('please_contact', 'override_entity',)
    }),
    ('Institutional details', {
        'fields': ('home_entity', 'entities',)
    }),    
    ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('slug',),
    }),
    )
admin.site.register(models.Person,PersonAdmin)

class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'post_town', 'country',)
    #list_editable = ('post_town', 'country',)
admin.site.register(models.Site,SiteAdmin)
    
class BuildingAdmin(admin.ModelAdmin):
    #list_display = ('name', 'site',)
    pass
admin.site.register(models.Building,BuildingAdmin)

