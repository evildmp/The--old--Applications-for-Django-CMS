import models
from django.db.models import F
from django.db.models import Q

from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from django.forms import ValidationError

class MembershipForm(forms.ModelForm): # cleans up membership & role information
    pass
"""
    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
#        print dir(self.instance)
#        try:
#            #Try and set the selected_cat field from instance if it exists
#            self.fields['selected_person'].initial = self.instance.subcategory.category.id
#        except:
#            pass
    #The membership model is defined with out the category, so add one in for display
    category = forms.ModelChoiceField(queryset = models.Membership.objects.all().order_by('name'), widget=forms.Select(attrs={'id':'category'}), required=False)
    #This field is used exclusively for the javascript so that I can select the 
    #correct category when editing an existing product
    selected_cat = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = models.Membership
    def clean(self):
        if self.cleaned_data["key_member"] and not self.cleaned_data["role"]:
            raise forms.ValidationError('Please enter a Role for anyone who is a Key member.')
        if self.cleaned_data["home"] and not self.cleaned_data["role"]:
            raise forms.ValidationError('People need a Role for their Home entity.')
        if not self.cleaned_data["key_member"]:
            self.cleaned_data["membership_order"] = 99999
        if not self.cleaned_data["role_plural"]:
            print "fixing plural roles"
            self.cleaned_data["role_plural"] = self.cleaned_data["role"]
        return self.cleaned_data
    class Media:
        #Alter these paths depending on where you put your media 
        js = (
            'js/mootools-1.2.3-core-yc.js',
            'js/display_roles.js',
        )
"""

class MembershipInline(admin.TabularInline): # for all membership inline admin
    form = MembershipForm    
    model = models.Membership
    extra = 1

class MembershipForEntityInline(MembershipInline): # for Entity admin
    exclude = ('order',)

class MembershipForPersonInline(MembershipInline): # for Person admin
    exclude = ('membership_order',)

class PersonForm(forms.ModelForm):
    model = models.Person
    print "sorting person order!"
    class Media:
        js = (
            '/media/jquery/development-bundle/jquery-1.3.2.js',
            '/media/jquery/development-bundle/ui/ui.core.js',
            '/media/jquery/development-bundle/ui/ui.sortable.js',
            '/media/jquery/menu-sort-people.js',)

class EntityForm(forms.ModelForm):
    model = models.Entity
    print "sorting entity order!"
    class Media:
        js = (
            '/media/jquery/development-bundle/jquery-1.3.2.js',
            '/media/jquery/development-bundle/ui/ui.core.js',
            '/media/jquery/development-bundle/ui/ui.sortable.js',
            '/media/jquery/menu-sort-entity.js',
        )

class PersonAdmin(admin.ModelAdmin):
    inlines = (MembershipForPersonInline,)
    form = PersonForm
    list_display = ( 'surname', 'given_name', 'user', 'slug')
    list_editable = ('user',)
    filter_horizontal = ('entities',)
    prepopulated_fields = {'slug': ('title', 'given_name', 'middle_names', 'surname',)}
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
    ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('slug',),
    }),
    )

class EntityAdmin(admin.ModelAdmin):
    inlines = (MembershipForEntityInline,)
    form = EntityForm
    list_display = ('name', 'parent', 'building', 'abstract_entity','website', )
    prepopulated_fields = {
            'slug': ('name',)
            }
    fieldsets = (
    (None, {
        'fields': ('name', 'abstract_entity', 'parent', 'display_parent', ),
    }),
    ('Contact information', {
        'classes': ('collapse',),
        'fields': ('website', 'email', 'phone_number', 'fax_number',  'building', 'precise_location', 'access_note', )
    }),
    ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('slug',)
    }),
        )

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

class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'post_town', 'country',)
        
class BuildingAdmin(admin.ModelAdmin):
    #list_display = ('name', 'site',)
    form = BuildingAdminForm

class TitleAdmin(admin.ModelAdmin):
    pass

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'entity', 'order', 'membership_order',)
    ordering = ['person',]
    form = MembershipForm
    


admin.site.register(models.Person,PersonAdmin)
admin.site.register(models.Building,BuildingAdmin)
admin.site.register(models.Entity,EntityAdmin)
admin.site.register(models.Site,SiteAdmin)
admin.site.register(models.Title,TitleAdmin)
admin.site.register(models.Membership,MembershipAdmin)