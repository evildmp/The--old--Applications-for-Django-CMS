from django.db import models
from cms.models import Page, CMSPlugin
from django.contrib.auth.models import User

import mptt
import operator

class Site(models.Model):
    """Maintains a list of an institution's geographical sites"""
    class Meta:
        ordering = ('country', 'post_town', 'site_name',)
    site_name = models.CharField(max_length=50, unique=True)
    post_town = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
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
    def __unicode__(self):
        if self.name:
            building_identifier = str(self.site) + ": " + self.name
        elif self.street:
            building_identifier = str(self.site) + ": " + self.number + " " + self.street
        else:
            building_identifier = str(self.site) + ": " + self.postcode
        return building_identifier

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
    """	Each office, department, committee, centre within an institution is an Entity.
	Entities are organised into a hierarchy, for example:
	The University
	    Faculty of Humanities
	        Department of Philosophy
	            Philosophy Examination Board
	The ancestry_for_adddress function allows us to eliminate unnecessary or undesired lines from the ancestry for the purpose of constructing address. For example, "Cardiff University School of Medicine" does not need to show its parent ("Cardiff University") in its address."""
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
    def build_address(self):
        ancestors = []
        showparent = self.display_parent
        for item in self.get_ancestors(ascending = True):
            if showparent and (not item.abstract_entity):
                ancestors.append(item)
            showparent = item.display_parent
        return ancestors
    def gather_members(self):
        memberlist = set()
        for entity in self.get_descendants(include_self = True):
            memberlist.update(entity.people_home.all())
            memberlist.update(entity.people.all())
        return memberlist
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/entity/%s/" % self.slug

class Person(ContactInformation):
    user = models.ForeignKey(User, related_name = 'person_user', unique=True, )
    title = models.CharField(max_length=6)
    given_name = models.CharField(max_length=50)
    middle_names = models.CharField(max_length=100, blank = True, null = True)
    surname = models.CharField(max_length=50)
    slug = models.SlugField(help_text=u"Do not meddle with this unless you know exactly what you're doing!")
    entities = models.ManyToManyField(Entity, related_name = 'people', blank = True, null = True)
    home_entity = models.ForeignKey(Entity, related_name = 'people_home')
    override_entity = models.ForeignKey(Entity, verbose_name = 'Override address', help_text= u"Get the person's address from an alternative entity", related_name = 'people_override', blank = True, null = True)
    please_contact = models.ForeignKey('self', help_text=u"Publish alternative contact details for this person", related_name='contact_for', blank = True, null = True)
    def gather_entities(self):
        entitylist = set()
        entitylist.add(self.home_entity)
        entitylist.update(self.home_entity.get_ancestors())
        for entity in self.entities.all():
            entitylist.add(entity)
            entitylist.update(entity.get_ancestors())
        return entitylist
    def __unicode__(self):
        return str(self.title + " " + self.given_name + " " + self.middle_names + " " + self.surname)
    def get_absolute_url(self):
        return "/person/%s/" % self.slug



try:
    mptt.register(Entity)
except mptt.AlreadyRegistered:
    pass