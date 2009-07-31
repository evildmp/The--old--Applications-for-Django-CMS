from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *
from cms.models import Page

register = template.Library()    

@register.inclusion_tag('entitytree.html', takes_context=True)
def make_membership_tree(context, person, node):
    """
    This function recurses, by using the template entitytree.html which in turn calls this function 
    """
    if node in person.gather_entities():
        return {
            'node': node,
            'person': person,
            }
            
@register.inclusion_tag('listofmembers.html', takes_context=True)
def list_members_for_entity(context, page):
    """
    Lists the members of an entity, based on the page
    """
    entity = find_entity_for_page(page)
    if entity:
        people = gather_members_for_entity(entity)
        return {
            'people': people,
            }  
    else:
        # this else needs to be improved
        return {
            'people': ["no","members",]
            }

@register.inclusion_tag('entity_contact_details.html', takes_context=True)
def contact_details_for_entity(context):
    """
    Drop {% contact_details_for_entity %} into a template.
    """
    request = context['request']
    entity = find_entity_for_page(request.current_page)
    if entity.abstract_entity:
        for ancestor in entity.get_ancestors(ascending = True):
            if not ancestor.abstract_entity:
                entity = ancestor
                break    
    address = build_institutional_address_for_entity(entity)
    building = find_building_for_entity(entity)
    address.extend(build_postal_address_for_building(building))
    members = gather_members_for_entity(entity)
    return {
        'entity' : entity,
        'address': address,
        'members': members,
    }

def build_institutional_address_for_entity(entity):
    ancestors = []
    showparent = entity.display_parent
    for item in entity.get_ancestors(ascending = True):
        if showparent and (not item.abstract_entity):
            ancestors.append(item)
        showparent = item.display_parent
    return ancestors

def find_building_for_entity(entity): # may need some error checking when for we get to the last ancestor
    if entity.building:
        return entity.building
    else:
        return find_building_for_entity(entity.parent)

def build_postal_address_for_building(building):
    """
    assembles the postal (external) parts of an address - assumes that the entity really does have a building
    """
    address = []
    if building.name:
        address.append(building.name)
    if building.number: 
        address.append(building.number + " " + building.street) # because building numbers and street names go on the same line
    elif building.street:
        address.append(building.street)
    if building.additional_street_address:
        address.append(building.additional_street_address)
    if building.site.post_town:
        address.append(building.site.post_town + " " + building.postcode)
    elif building.postcode:
        address.append(building.postcode)
    return address

# think we need some error checking here for we get to the last ancestor
def find_entity_for_page(page):
    """
    Give a page, returns the entity that has selected the page as its website.
    If the page doesn't have an entity attached to it, will try for the page's parent, and so on.
    """
    try:
        return page.entity.get()
    except:
        return find_entity_for_page(page.parent)

  
@register.tag # injects the address as {{ address }} into the context
def get_entity_info(parser, token):
    return EntityInfo()

class EntityInfo(template.Node):
    # we need some error checking in here
    def render(self, context):
        request = context['request']
        context['address'] = build_address_for_page(request.current_page)
        context['entity'] = find_entity_for_page(request.current_page)
        return ''
                    
def gather_members_for_entity(entity):
    memberlist = set()
    for descendant_entity in entity.get_descendants(include_self = True):
        memberlist.update(descendant_entity.people_home.all())
        memberlist.update(descendant_entity.people.all())
    return memberlist

            

    
    