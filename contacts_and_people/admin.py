import models
from django.db.models import F
from django.db.models import Q

from django.conf import settings

from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from django.forms import ValidationError

from django.utils.safestring import mark_safe 

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

class DisplayUsernameWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        user = User.objects.get(pk=value)
        return mark_safe(u"<span>Assigned user: <strong>%s</stron></span>" % user)

class PersonForm(forms.ModelForm):
    model = models.Person
    
    def __init__(self, *args, **kwargs):
        # disable the user combo if a user aleady has been assigned
        super(PersonForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id and not instance.user==None:
            self.fields['user'].widget = DisplayUsernameWidget()
            self.fields['user'].help_text = "Once a user has been assigned, it cannot be changed"
        
    
    def clean_please_contact(self):
        data = self.cleaned_data['please_contact']
        # only do the check when in "change" mode. there can't be a loop if in "new" mode
        # because nobody can link to us if we did not exist yet before.
        if hasattr(self, 'instance') and type(self.instance) == type(data):
            self.instance.please_contact = data
            has_loop_error, person_list = self.instance.check_please_contact_has_loop(self.instance)
            if has_loop_error:
                r = []
                for p in person_list:
                    r.append(u'"%s"' % p)
                r = u' &rarr; '.join(r)    
                raise forms.ValidationError(mark_safe(u"Please prevent loops: %s" % r))
        return data
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





# admin hacks
if getattr(settings,"ENABLE_CONTACTS_AND_PEOPLE_AUTH_ADMIN_INTEGRATION", False):
    admin.site.unregister(User)
    
    from django import template
    from django.conf import settings
    from django.contrib import admin
    from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
    from django.contrib.auth.models import User, Group
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponseRedirect, Http404
    from django.shortcuts import render_to_response, get_object_or_404
    from django.template import RequestContext
    from django.utils.html import escape
    from django.utils.translation import ugettext, ugettext_lazy as _
    
    from django.contrib.auth.admin import UserAdmin
    from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
    from django import forms
    
    class MyPersonInline(admin.StackedInline):
        model = models.Person
        fieldsets = PersonAdmin.fieldsets
        prepopulated_fields = PersonAdmin.prepopulated_fields
        extra = 1
        verbose_name = ""
        verbose_name_plural = "Person"
    
    
    
    class MyNoPasswordCapableUserCreationForm(UserCreationForm):
        has_password = forms.BooleanField(required=False, initial=True)
        def clean(self):
            data = self.cleaned_data
            if self.cleaned_data['has_password'] in (False, None,):
                if 'password1' in self.errors.keys():
                    del self.errors['password1']
                if 'password2' in self.errors.keys():
                    del self.errors['password2']
                # save() will remove this temp password again.
                self.cleaned_data['password1'] = self.cleaned_data['password2'] = 'xxxxxxxxxxxxxxx'
            return data
        def save(self, commit=True):
            instance = super(MyNoPasswordCapableUserCreationForm, self).save(commit=False)
            if self.cleaned_data['has_password'] in (False, None,):
                instance.set_unusable_password()
            if commit:
                instance.save()
                if hasattr(instance, 'save_m2m'):
                    instance.save_m2m()
                return instance
            else:
                return instance
        
    class MyNoPasswordCapableUserChangeForm(UserChangeForm):
        has_password = forms.BooleanField(label="has password", help_text="LDAP users don't need a password", required=False, initial=True)
        def __init__(self, *args, **kwargs):
            r = super(MyNoPasswordCapableUserChangeForm,self).__init__(*args, **kwargs)
            instance = kwargs.get('instance',None)
            if instance and instance.id:
                if instance.has_usable_password():
                    self.initial['has_password'] = True
                else:
                    self.initial['has_password'] = False     
            return r
        def save(self, commit=True):
            instance = super(MyNoPasswordCapableUserChangeForm, self).save(commit=False)
            if self.cleaned_data['has_password'] in (False, None,):
                instance.set_unusable_password()
            if commit:
                instance.save()
                if hasattr(instance, 'save_m2m'):
                    instance.save_m2m()
                return instance
            else:
                return instance
    
    user_admin_fieldsets = list(UserAdmin.fieldsets)
    user_admin_fieldsets[0] = (None, {'fields': ('username', ('password', 'has_password',),)})
    class MyUserAdmin(UserAdmin):
        fieldsets = user_admin_fieldsets
        form = MyNoPasswordCapableUserChangeForm
        add_form = MyNoPasswordCapableUserCreationForm
        list_display = ('username', 'email', 'is_staff')
        inlines = (MyPersonInline,)
        
        def add_view(self, request):
            # IT REALLY SUCKS THAT I NEED TO COPY THIS ENTIRE METHOD... it's the same as 
            # django.contrib.auth.admin.UserAdmin.add_view, just with a other template
            
            # It's an error for a user to have add permission but NOT change
            # permission for users. If we allowed such users to add users, they
            # could create superusers, which would mean they would essentially have
            # the permission to change users. To avoid the problem entirely, we
            # disallow users from adding users if they don't have change
            # permission.
            if not self.has_change_permission(request):
                if self.has_add_permission(request) and settings.DEBUG:
                    # Raise Http404 in debug mode so that the user gets a helpful
                    # error message.
                    raise Http404('Your user does not have the "Change user" permission. In order to add users, Django requires that your user account have both the "Add user" and "Change user" permissions set.')
                raise PermissionDenied
            if request.method == 'POST':
                form = self.add_form(request.POST)
                if form.is_valid():
                    new_user = form.save()
                    msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': 'user', 'obj': new_user}
                    self.log_addition(request, new_user)
                    if "_addanother" in request.POST:
                        request.user.message_set.create(message=msg)
                        return HttpResponseRedirect(request.path)
                    elif '_popup' in request.REQUEST:
                        return self.response_add(request, new_user)
                    else:
                        request.user.message_set.create(message=msg + ' ' + ugettext("You may edit it again below."))
                        return HttpResponseRedirect('../%s/' % new_user.id)
            else:
                form = self.add_form()
            return render_to_response('contacts_and_people/admin/auth/user/add_form.html', {
                'title': _('Add user'),
                'form': form,
                'is_popup': '_popup' in request.REQUEST,
                'add': True,
                'change': False,
                'has_add_permission': True,
                'has_delete_permission': False,
                'has_change_permission': True,
                'has_file_field': False,
                'has_absolute_url': False,
                'auto_populated_fields': (),
                'opts': self.model._meta,
                'save_as': False,
                'username_help_text': self.model._meta.get_field('username').help_text,
                'root_path': self.admin_site.root_path,
                'app_label': self.model._meta.app_label,            
            }, context_instance=template.RequestContext(request))
    admin.site.register(User, MyUserAdmin)

