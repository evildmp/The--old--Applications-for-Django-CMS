from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *
from cms.models import *

register = template.Library()

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


def find_entity_for_page(page):
   try:
       return page.entity.get()
   except:
       return find_entity_for_page(page.parent)

def gather_studentships(entity):
   studentshiplist = set()
   for entity in entity.get_descendants(include_self = True):
       studentshiplist.update(entity.studentship_hosts.all())
   return studentshiplist

