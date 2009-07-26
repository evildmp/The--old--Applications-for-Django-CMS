from contacts_and_people.models import Entity
from cms.models import Page

def find_entity_for_page(page):
    try:
        return page.entity.get()
    except:
        return find_entity_for_page(page.parent)
