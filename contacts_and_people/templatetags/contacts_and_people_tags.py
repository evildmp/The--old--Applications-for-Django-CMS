from django import template
from django.db.models import Q
from django.shortcuts import render_to_response
# is this indiscriminate import a good idea?
from contacts_and_people.models import *
from cms.models import Page

import operator

register = template.Library()    

@register.inclusion_tag('entitytree.html', takes_context=True)
def make_membership_tree(context, person, node):
    """
    Builds a tree representation of the entities that the person belongs to.
    
    This function recurses, by using the template entitytree.html which in turn calls this function 
    """
    if node in person.gather_entities():
        return {
            'node': node,
            'person': person,
            }

    request = context['request']
    entity = entity_for_page(request.current_page)


            
@register.inclusion_tag('entity_list_members.html', takes_context=True)
def entity_list_members(context):
    """
   For an Entity, returns a list of members who have roles. 
    
    The entity is determined by looking up which Entity has been attached to the Page. If there is no such Entity, the closest one in its ancestors will be used.
    
    {% entity_info 'roles'} will list all members of the entity with defined roles. For each member, one role will be chosen, in the following order of preference:
    
    1.   roles for this entity - if multiple roles exist, the home role (if it exists) is selected; failing that the order given to roles in the Person Admin is used (Membership.order).
    2.   the person's home role elsewhere, if it exists
    3.   other roles people have elsewhere, if they exist, ordered by their Membership.order
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    members = list(members_for_entity(entity))
    members.sort(key=operator.attrgetter('surname', 'given_name', 'middle_names'))
    member_list = []
    for member in members:
        memberships = []
        ms = Membership.objects.filter(
            person = member)
        memberships = list(ms.filter(entity=entity).exclude(role ="").order_by('-home', 'order')) # persons's role(s) for this entity
        memberships.extend(ms.filter(home = True).exclude(entity=entity)) # person's home somewhere else
        memberships.extend(ms.filter(home = False).exclude(entity = entity).exclude(role ="").order_by('order')) # person's role(s) are somewhere else
        if memberships:
            member.membership = memberships[0]
            member_list.append(member)  

    return {
        'entity' : entity,
        'member_list': member_list
            }  

@register.inclusion_tag('entity_contact_details.html', takes_context=True)
def contact_details_for_entity(context):
    """
    Drop {% contact_details_for_entity %} into a template.
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    contacts = Membership.objects.filter(entity = entity, key_contact = True).order_by('membership_order')
    address = address_for_entity(entity)
    return {
            'entity' : entity,
            'address': address,
            'contacts': contacts
        }

@register.inclusion_tag('entity_key_staff.html', takes_context=True)
def key_staff_for_entity(context):
    """
    Drop {% key_staff_for_entity %} into a template - returns an ordered list of memberships, grouped by people
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    memberships = Membership.objects.filter(entity = entity,key_member = True).order_by('membership_order',)    
    duplicates = set()
    membership_list = []
    for membership in memberships:
        if membership not in duplicates:
            duplicates.add(membership)
            membership_list.append(membership)
    # returns a list of memberships, in the right order - we use a regroup tag to group them by person in the template    
    return {'membership_list': membership_list}
    
@register.inclusion_tag('entity_key_roles.html', takes_context=True)
def key_roles_for_entity(context):   
    """
    Drop {% key_roles_for_entity %} into a template - returns an ordered list of people grouped by their most significant roles in the entity
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    memberships = Membership.objects.filter(entity = entity).exclude(role="").order_by('membership_order',) 
    duplicates = set()
    membership_list = []
    for membership in memberships:
        if membership.role_plural not in duplicates:
            duplicates.add(membership.role_plural)
            membership_list.extend(memberships.filter(role_plural = membership.role_plural))
    # returns a list of memberships, in the right order - we use a regroup tag to group them by person in the template    
    return {'membership_list': membership_list}

@register.simple_tag
# think we need some error checking here, in case we get to the last ancestor page without having found an entity
def entity_for_page(page):
    """
    Give a page, returns the entity that has selected the page as its website.
    If the page doesn't have an entity attached to it, will try for the page's parent, and so on.
    """
    try:
        return page.entity.get()
    except:
        return entity_for_page(page.parent)

def address_for_entity(entity):
    if entity.abstract_entity:
        entity = real_ancestor(entity)
    address = institutional_address_for_entity(entity)
    building = building_for_entity(entity)
    address.extend(postal_address_for_building(building))
    return address

def institutional_address_for_entity(entity):
    ancestors = []
    showparent = entity.display_parent
    for item in entity.get_ancestors(ascending = True):
        if showparent and (not item.abstract_entity):
            ancestors.append(item)
        showparent = item.display_parent
    return ancestors

def building_for_entity(entity): # may need some error checking when for we get to the last ancestor
    if entity.building:
        return entity.building
    else:
        return building_for_entity(entity.parent)

@register.simple_tag
def postal_address_for_building(building):
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
            
def members_for_entity(entity):
    memberlist = set()
    for descendant_entity in entity.get_descendants(include_self = True):
        memberlist.update(descendant_entity.people.all())
    return memberlist

def real_ancestor(entity):
    for ancestor in entity.get_ancestors(ascending = True):
        if not ancestor.abstract_entity:
            entity = ancestor
            break    
    return entity


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


