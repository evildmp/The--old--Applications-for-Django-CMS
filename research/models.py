from django.db import models
from contacts_and_people.models import Entity, Person
from cms.models import Page
from datetime import datetime

class Studentship(models.Model):
    class Meta:
        ordering = ['-start_date']
    short_title = models.CharField(max_length = 50)
    title = models.CharField(max_length = 250)
    start_date = models.DateField()
    description = models.TextField()
    supervisors = models.ManyToManyField(Person, 
        related_name="%(class)s_people", 
        help_text = u"People <em>named</em> in this item", 
        null = True, blank = True
        )
    host_entities = models.ManyToManyField(Entity,
        related_name = "%(class)s_hosts",
        help_text = u"The research groups or departments responsible for this studentship")
    please_contact = models.ForeignKey(Person, 
        related_name = '%(class)s_person', 
        help_text = u'The person to whom enquiries about this should be directed ', 
        null = True, blank = True
        )
    advertise_on = models.ManyToManyField(Entity, 
        related_name = "%(class)s_advertise_on",
        help_text = u"Other research groups or departs where this should be advertised", 
        null = True, blank = True
        )
    please_see = models.ForeignKey(Page, 
        related_name="%(class)s_page", 
        help_text = u"A page with further information", 
        null = True, blank = True
        )
    slug=models.SlugField()  
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/studentship/%s/" % self.slug
