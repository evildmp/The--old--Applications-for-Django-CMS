import models
from django.contrib import admin
from django.contrib.auth.models import User

class BuildingInline(admin.StackedInline):
    model = models.Building
    extra = 1

class MembershipInline(admin.TabularInline):
    model = models.Membership
    extra = 1

class EntityAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)
    list_display = ('name', 'parent', 'building', 'abstract_entity','website',)
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

class PersonAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)
    list_display = ( 'surname', 'given_name', 'user',)
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
        'fields': ('home_entity', 'job_title',)
    }),    
    ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('slug',),
    }),
    )

class SiteAdmin(admin.ModelAdmin):
    inlines = (BuildingInline,)
    list_display = ('site_name', 'post_town', 'country',)
    #list_editable = ('post_town', 'country',)

class BuildingAdmin(admin.ModelAdmin):
    #list_display = ('name', 'site',)
    pass

admin.site.register(models.Person,PersonAdmin)
admin.site.register(models.Building,BuildingAdmin)
admin.site.register(models.Entity,EntityAdmin)
admin.site.register(models.Site,SiteAdmin)
