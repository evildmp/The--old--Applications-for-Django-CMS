import django.http as http
import django.shortcuts as shortcuts
from models import Person
from news_and_events.models import *
        
def entity(request, slug):
    entity = Entity.objects.get(slug=slug)
    news = entity.newsarticle_set.all()
    events = entity.event_set.all()
    vacancies = entity.vacancy_set.all()
    studentships = entity.studentship_set.all()
    return shortcuts.render_to_response(
        "contacts_and_people/entitydetails.html",
        {"entity":entity, 
        "news": news,
        "events": events,
        "vacancies": vacancies,
        "studentships": studentships,
        }
        )

def person(request, slug):
    person = Person.objects.get(slug=slug)
    home_entity = person.home_entity
    return shortcuts.render_to_response(
        "contacts_and_people/persondetails.html",
        {"person":person, 
        "home_entity": home_entity
        }
        )