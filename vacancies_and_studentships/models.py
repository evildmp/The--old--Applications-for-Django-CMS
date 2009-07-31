from django.db import models
from contacts_and_people.models import Entity, Person
from cms.models import Page
from datetime import datetime

class CommonVacancyAndStudentshipInformation(models.Model):
    class Meta:
        abstract = True
        ordering = ['-closing_date']
    short_title = models.CharField(max_length = 50)
    title = models.CharField(max_length = 250)
    closing_date = models.DateField()
    description = models.TextField()
    host_entity = models.ForeignKey(Entity,
        help_text = u"The research group or department responsible for this vacancy")
    please_contact = models.ForeignKey(Person, 
        related_name = '%(class)s_person', 
        help_text = u'The person to whom enquiries about this should be directed ', 
        null = True, blank = True
        )
    also_advertise_on = models.ManyToManyField(Entity, 
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

class Vacancy(CommonVacancyAndStudentshipInformation):
    class Meta:
        verbose_name_plural = "Vacancies"
    job_number = models.CharField(max_length = 9)
    salary = models.SmallIntegerField()
    def get_absolute_url(self):
        return "/vacancy/%s/" % self.slug

class Studentship(CommonVacancyAndStudentshipInformation):
    supervisors = models.ManyToManyField(Person, 
        related_name="%(class)s_people", 
        null = True, blank = True
        )
    def get_absolute_url(self):
        return "/studentship/%s/" % self.slug
