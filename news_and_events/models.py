from django.db import models
from contacts_and_people.models import Entity, Person
from cms.models import Page
from datetime import datetime

class NewsAndEvents(models.Model):
    class Meta:
        abstract = True
    title = models.CharField(
        max_length=255,
        help_text= u"The full title  of the item",
        )
    short_title = models.CharField(
        max_length=50, 
        help_text= u"A very short title for use in navigation menus"
        )
    summary = models.TextField()
    content = models.TextField()
    publishing_destinations = models.ManyToManyField(
        Entity, 
        help_text = u"Use these sensibly - don't send minor items to the home page, for example", 
        null = True, blank = True
        )
    please_contact = models.ForeignKey(
        Person, 
        related_name = '%(class)s_person', 
        help_text = u'The person to whom enquiries about this should be directed ', 
        null = True, blank = True
        )
    please_see = models.ForeignKey(
        Page, 
        related_name="%(class)s_page", 
        help_text = u"A page with further information", 
        null = True, blank = True
        )
    related_articles = models.ManyToManyField(
        'self', 
        null = True, blank = True
        )
    related_pages = models.ManyToManyField(
        Page, related_name="%(class)s_pages", 
        help_text = u"Other pages with <em>particular</em> relevance to this item", 
        null = True, blank = True
        )
    related_people = models.ManyToManyField(
        Person, related_name="%(class)s_people", 
        help_text = u"People <em>named</em> in this item", 
        null = True, blank = True
        )
    slug=models.SlugField()  
        
class NewsArticle(NewsAndEvents):
    class Meta:
        ordering = ['-date']
    date = models.DateTimeField(default=datetime.now)    
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/news/article/%s/" % self.slug
        
class Event(NewsAndEvents):
    class Meta:
        ordering = ['-date']
    date = models.DateTimeField()    
    date_end = models.DateTimeField(null = True, blank = True)    
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/events/event/%s/" % self.slug        