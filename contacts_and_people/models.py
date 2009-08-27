from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from cms.models import Page, CMSPlugin
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django import forms

import mptt

class Site(models.Model):
    """Maintains a list of an institution's geographical sites"""
    class Meta:
        ordering = ('country', 'post_town', 'site_name',)
    site_name = models.CharField(max_length=50, unique=True)
    post_town = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    description = models.TextField(max_length = 500, null = True, blank=True)
    def __unicode__(self):
        return self.site_name

class Building(models.Model):
    """Each Building is on a Site."""
    class Meta:
        ordering = ('street', 'number', 'name',)
    name = models.CharField(max_length=100, null = True, blank=True)
    number = models.CharField(max_length=10, null = True, blank=True)
    street = models.CharField("Street name", max_length=100, null = True, blank=True)
    additional_street_address = models.CharField(help_text=u"If required", max_length=100, null = True, blank=True)
    postcode = models.CharField(max_length=9, null = True, blank=True)
    site = models.ForeignKey(Site)
    slug = models.SlugField(null = True, blank=True)
    longitude = models.FloatField()
    latitude = models.FloatField()    
    def __unicode__(self):
        if self.name:
            building_identifier = str(self.site) + ": " + self.name
        elif self.street:
            building_identifier = str(self.site) + ": " + self.number + " " + self.street
        else:
            building_identifier = str(self.site) + ": " + self.postcode
        return building_identifier
    def save(self):
        self.slug = slugify(self.__unicode__())
        super(Building, self).save()
    def get_absolute_url(self):
        return "/places/%s/" % self.slug

class PhoneContactLabel(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u"%s" % self.name

class PhoneContact(models.Model):
    PHONE_TYPE_CHOICES = (('landline', 'landline'),
                          ('mobile','mobile'),
                          ('fax','fax'),
                          )
    label = models.ForeignKey(PhoneContactLabel, null=True, blank=True)
    type = models.CharField(max_length=24, choices=PHONE_TYPE_CHOICES, default=PHONE_TYPE_CHOICES[0][0])
    number = models.CharField(max_length=15)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(db_index=True)
    content_object = generic.GenericForeignKey()
    def __unicode__(self):
        return u"%s %s (%s)" % (self.label, self.number, self.type) 

class ContactInformation(models.Model):
    class Meta:
        abstract = True
    building = models.ForeignKey(Building, null = True, blank=True)
    precise_location = models.CharField(help_text=u"Precise location within building, for visitors",
        max_length=50, null = True, blank=True
        )
    access_note = models.CharField(help_text = u"Notes on access/visiting hours/etc",
        max_length=255, null = True, blank=True
        )
    email = models.EmailField(verbose_name="Email address", null = True, blank=True)
    phone_number = models.CharField(max_length=15, null = True, blank=True)
    fax_number = models.CharField(max_length=15, null = True, blank=True)

class Entity(ContactInformation):
    class Meta:
        verbose_name_plural = "Entities"
        ordering = ['lft']
    name = models.CharField(max_length= 100)
    slug=models.SlugField(help_text=u"Do not meddle with this unless you know exactly what you're doing!")
    abstract_entity = models.BooleanField(
        "Group",
        help_text =u"If this is a <em>group</em> of entities, not an entity itself",
        default=False)
    parent = models.ForeignKey('self', blank=True, null = True, related_name='children')
    display_parent = models.BooleanField(default=True, help_text=u'If the parent should appear in the address')
    website = models.ForeignKey(Page, related_name = 'entity', unique = True, null = True, blank=True)
#    roles = models.ManyToManyField('Role', null = True, blank=True)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/entity/%s/" % self.slug

class Title(models.Model):
    title = models.CharField (max_length = 50, unique = True)
    abbreviation = models.CharField (max_length = 20)
    def __unicode__(self):
        return str(self.title)

class Person(ContactInformation):
    class Meta:
        ordering = ['surname', 'given_name', 'user',]
        verbose_name_plural = "People"
    user = models.ForeignKey(User, related_name = 'person_user', unique=True, blank = True, null = True)
    title = models.ForeignKey(Title, related_name = 'people', blank = True, null = True)
    given_name = models.CharField(max_length=50, blank = True, null = True)
    middle_names = models.CharField(max_length=100, blank = True, null = True)
    surname = models.CharField(max_length=50)
    slug = models.SlugField(help_text=u"Do not meddle with this unless you know exactly what you're doing!")
    entities = models.ManyToManyField(Entity, related_name = 'people', through ='Membership', blank = True, null = True)
#    home_entity = models.ForeignKey(Entity, related_name = 'people_home', blank = True, null = True)
#    job_title = models.CharField(max_length=50, blank = True, null = True)
    override_entity = models.ForeignKey(Entity, verbose_name = 'Override address', help_text= u"Get the person's address from an alternative entity", related_name = 'people_override', blank = True, null = True)
    please_contact = models.ForeignKey('self', help_text=u"Publish alternative contact details for this person", related_name='contact_for', blank = True, null = True)
    def gather_entities(self):
        entitylist = set()
#        entitylist.add(self.home_entity)
#        entitylist.update(self.home_entity.get_ancestors())
        for entity in self.entities.all():
            entitylist.add(entity)
            entitylist.update(entity.get_ancestors())
        return entitylist
    def __unicode__(self):
        return str(self.given_name + " " + self.middle_names + " " + self.surname)
    def get_absolute_url(self):
        return "/person/%s/" % self.slug
    
    def check_please_contact_has_loop(self, compare_to, person_list=None):
        if person_list==None:
            person_list=[compare_to]
        if not self==compare_to:
            person_list.append(self)
        if self.please_contact:
            if compare_to==self.please_contact:
                person_list.append(compare_to)
                return True, person_list
            else:
                return self.please_contact.check_please_contact_has_loop(compare_to, person_list)
        else:
            return False, person_list
    
    def save(self, *args, **kwargs):
        do_check_please_contact_loop = kwargs.pop('do_check_please_contact_loop', True)
        if do_check_please_contact_loop and self.check_please_contact_has_loop(compare_to=self)==True:
            raise Exception # TODO: raise a more appropriate exception
        return super(Person, self).save(*args, **kwargs)

class Membership(models.Model):
    class Meta:
        ordering = ('membership_order',)
    person = models.ForeignKey(Person, related_name = 'member_of')
    entity = models.ForeignKey(Entity, related_name='members', limit_choices_to  = {'abstract_entity': False})
    display_role = models.ForeignKey('self', related_name = "display_roles", null = True, blank = True)
    home = models.BooleanField(default=False)
#    role = models.ForeignKey(Role, related_name = "bob", null = True, blank = True)
    role = models.CharField(max_length = 50, null = True, blank = True)
    role_plural = models.CharField(max_length = 50, null = True, blank = True, help_text = "e.g. 'Director of Research' becomes 'Directors of Research'")
    key_member = models.BooleanField(default=False)
    key_contact = models.BooleanField(default=False)
    order = models.IntegerField(blank = True, null = True)
    membership_order = models.IntegerField(blank = True, null = True)
    def save(self):
        if self.home:
            for item in Membership.objects.filter(person = self.person): 
                item.home = False
                super(Membership, item).save()
            self.home = True  
        super(Membership, self).save()
    def __unicode__(self):
        return str(self.person) + "-" + str(self.entity) + "-" + str(self.role)

try:
    mptt.register(Entity)
except mptt.AlreadyRegistered:
    pass