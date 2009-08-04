import models
from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from django.forms import ValidationError

class MembershipAdminForm(forms.ModelForm):
    class Meta:
        model = models.Membership
    def clean(self):
        if self.cleaned_data["key_member"] and not self.cleaned_data["role"]:
            raise forms.ValidationError('Please enter a Role for anyone who is a Key member.')
        return self.cleaned_data

class BuildingAdminForm(forms.ModelForm):
    class Meta:
        model = models.Building
    def clean(self):
        if self.cleaned_data["number"] and not self.cleaned_data["street"]:
            raise forms.ValidationError("Silly. You can't have a street number but no street, can you?")
        if self.cleaned_data["additional_street_address"] and not self.cleaned_data["street"]:
            self.cleaned_data["street"] = self.cleaned_data["additional_street_address"]
            self.cleaned_data["additional_street_address"] = None
        if not (self.cleaned_data["postcode"] or self.cleaned_data["name"] or self.cleaned_data["street"]):
            raise forms.ValidationError("That's not much of an address, is it?")
        return self.cleaned_data

class BuildingInline(admin.StackedInline):
    model = models.Building
    extra = 1

class MembershipInline(admin.TabularInline):
    form = MembershipAdminForm    
    model = models.Membership
    extra = 1

class EntityAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)
    list_display = ('name', 'parent', 'building', 'abstract_entity','website', )
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

class MembershipAdmin(admin.ModelAdmin):
    form = MembershipAdminForm

class PersonAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)
    list_display = ( 'surname', 'given_name', 'user', 'slug')
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
#    ('Institutional details', {
#        'fields': ('home_entity', 'job_title',)
#    }),    
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
    form = BuildingAdminForm

admin.site.register(models.Person,PersonAdmin)
admin.site.register(models.Building,BuildingAdmin)
admin.site.register(models.Entity,EntityAdmin)
admin.site.register(models.Site,SiteAdmin)
admin.site.register(models.Membership,MembershipAdmin)
