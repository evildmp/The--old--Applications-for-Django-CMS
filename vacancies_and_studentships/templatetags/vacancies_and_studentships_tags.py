from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *
from contacts_and_people.functions import *
from cms.models import *

register = template.Library()

@register.inclusion_tag('listofvacancies.html', takes_context=True)
def list_vacancies_for_entity(context, page):
    entity = find_entity_for_page(page)
    if entity:
        vacancies = gather_vacancies(entity)
        return {
            'vacancies': vacancies,
            }  
    else:
        return {
            'vacancies': ["no","vacancies",]
            }
            
@register.inclusion_tag('listofstudentships.html', takes_context=True)
def list_studentships_for_entity(context, page):
   entity = find_entity_for_page(page)
   if entity:
       studentships = gather_studentships(entity)
       return {
           'studentships': studentships,
           }  
   else:
       return {
           'studentships': ["no","studentships",]
           }

def gather_vacancies(entity):
   vacancylist = set()
   for entity in entity.get_descendants(include_self = True):
       vacancylist.update(entity.vacancy_host.all())
       vacancylist.update(entity.vacancy_advertise_on.all())
   return vacancylist

def gather_studentships(entity):
  studentshiplist = set()
  for entity in entity.get_descendants(include_self = True):
      studentshiplist.update(entity.studentship_host.all())
      studentshiplist.update(entity.studentship_advertise_on.all())
  return studentshiplist
