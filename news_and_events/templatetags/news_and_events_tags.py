from django import template
from django.shortcuts import render_to_response
from news_and_events.models import *
from contacts_and_people.models import *
from cms.models import *

register = template.Library()

def test(entity):
    pass

def news(entity):
    newslist = []
    for item in entity.newsarticle_set.all():
        news_list.append(item.title)
    return newslist
register.simple_tag(news)

@register.inclusion_tag('test.html', takes_context=True)
def test(context):
    return {
       'stuff': context
       }

@register.inclusion_tag('newslist.html', takes_context=True)
def news_for_this_page(context, max_items):    
    request=context['request']
    page = request.current_page
    entity = find_entity_for_page(page)
    if entity:
        print entity
        return {
            'news': entity.newsarticle_set.all()[0: max_items],
            }
    else:    
        return { 'news': "No news is good news",}
        
@register.inclusion_tag('eventslist.html', takes_context=True)
def events_for_this_page(context, max_items):    
    request=context['request']
    page = request.current_page
    entity = find_entity_for_page(page)
    if entity:
       return {
           'events': entity.event_set.all()[0: max_items],
           }
    else:    
        return { 'news': "No events",}        


def find_entity_for_page(page):
   try:
       return page.entity.get()
   except:
       return find_entity_for_page(page.parent)




