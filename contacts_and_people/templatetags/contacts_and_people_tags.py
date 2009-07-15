from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *

from contacts_and_people.models import *

register = template.Library()    

@register.inclusion_tag('entitytree.html', takes_context=True)
def make_membership_tree(context, node):
    person=context['person']
    if node in person.gather_entities():
        return {
            'node': node,
            'person': person,
            }                       