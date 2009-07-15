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
    this_page = request.current_page
    if this_page.entity:
       e = this_page.entity.get() 
       return {
           'news': e.newsarticle_set.all()[0: max_items],
           }
    else:    
        return { 'news': "No news is good news",}
        
@register.inclusion_tag('eventslist.html', takes_context=True)
def events_for_this_page(context, max_items):    
    request=context['request']
    this_page = request.current_page
    if this_page.entity:
       e = this_page.entity.get() 
       return {
           'events': e.event_set.all()[0: max_items],
           }
    else:    
        return { 'news': "No events",}        












@register.inclusion_tag('newslist.html', takes_context=True)
def oldnews_for_this_page(context):    
    request=context['request']
    c = request.current_page
    if hasattr(c, "origin"):
       if c.origin.entity_set.all(): # check page belongs to an entity first
           e = c.origin.entity_set.all()[0] # the first entity will be the only one
           news = []
           for item in e.newsitem_set.all(): # get entity's news items
               news.append(item) # add them to the list
           return {
               'news': news,
               }
    else:    
        return { 'news': "No news is good news",}
