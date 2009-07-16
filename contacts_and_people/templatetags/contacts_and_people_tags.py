from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *

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
            
@register.inclusion_tag('entitytree.html', takes_context=True)
def list_members_of_entity(context, node):
    person=context['person']
    if node in person.gather_entities():
        return {
            'node': node,
            'person': person,
            }    