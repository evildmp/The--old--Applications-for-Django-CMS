import django.http as http
import django.shortcuts as shortcuts
from news_and_events.models import *
        
def newsarticle(request, slug):
    newsarticle = NewsArticle.objects.get(slug=slug)
    return shortcuts.render_to_response(
        "news_and_events/newsarticle.html",
        {"newsarticle":newsarticle}
        )

def event(request, slug):
    event = Event.objects.get(slug=slug)
    return shortcuts.render_to_response(
        "news_and_events/event.html",
        {"event": event}
        )
  