from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import *
from cms.models import Page

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
            
@register.inclusion_tag('list_of_members.html', takes_context=True)
def list_members_for_entity(context):
    """
    Lists the members of an entity.
    
    Drop {% all_staff_for_entity %} into a template.
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    members = members_for_entity(entity)
    members =list(members)
    members.sort()
    people = {}
    stuff = []
    for member in members:
        ms = Membership.objects.filter(
            person = member)
        # maybe person's home is *this* entity
        result = ms.filter(entity = entity, home = True)
        if result:
            print str(member) + "'s home is here"
            print member.surname
            stuff.append({member: result})
            people.setdefault(member,[]).extend(result)
        # perhaps the person has one or more roles here
        else:
            result = ms.filter(entity = entity).exclude(role ="")            
            if result:
                print str(member) + "has a role here"
                people.setdefault(member,[]).extend(result)
            # perhaps the person has a home in some other entity
            else:   
                result = ms.filter(home = True)
                if result:
                    print str(member) + "'s home is somewhere else"
                    people.setdefault(member,[]).extend(result)
                else:    
                    people.setdefault(member,[]).extend(result)
                    print str(member) + " is a member, but we don't have much information to display"
    print people
    return {
        'entity' : entity,
        'people': people,
        'stuff': stuff
            }  

@register.inclusion_tag('entity_contact_details.html', takes_context=True)
def contact_details_for_entity(context):
    """
    Drop {% contact_details_for_entity %} into a template.
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    contacts = Membership.objects.filter(
        entity = entity,
        key_contact = True)
    address = address_for_entity(entity)
    return {
            'entity' : entity,
            'address': address,
            'contacts': contacts
        }

@register.inclusion_tag('entity_key_staff.html', takes_context=True)
def key_staff_for_entity(context):
    """
    Drop {% key_staff_for_entity %} into a template.
    """
    request = context['request']
    entity = entity_for_page(request.current_page)
    key_roles = (Membership.objects.filter(
        entity = entity,
        key_member = True))
    key_people = {}
    for role in key_roles:
        key_people.setdefault(role.person,[]).append(role.role)  
    return {
            'entity' : entity,
            'key_people': key_people,
            'address': address_for_entity(entity),
        }



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


