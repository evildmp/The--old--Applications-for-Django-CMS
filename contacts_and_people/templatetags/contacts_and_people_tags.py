from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *
from contacts_and_people.functions import *
from cms.models import Page


from contacts_and_people.models import *

register = template.Library()    

@register.inclusion_tag('entitytree.html', takes_context=True)
def make_membership_tree(context, person, node):
    """This function recurses, by using the template entitytree.html which in turn calls this function """
    if node in person.gather_entities():
        return {
            'node': node,
            'person': person,
            }
            
@register.inclusion_tag('listofmembers.html', takes_context=True)
def list_members_for_entity(context, page):
    entity = find_entity_for_page(page)
    if entity:
        people = entity.gather_members()
        return {
            'people': people,
            }  
    else:
        return {
            'people': ["no","members",]
            }
            
