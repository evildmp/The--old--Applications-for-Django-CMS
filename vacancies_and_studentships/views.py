import django.http as http
import django.shortcuts as shortcuts
from vacancies_and_studentships.models import *
        
def vacancy(request, slug):
    vacancy = Vacancy.objects.get(slug=slug)
    return shortcuts.render_to_response(
        "vacancies_and_studentships/vacancy.html",
        {"vacancy":vacancy}
        )

def studentship(request, slug):
    studentship = Studentship.objects.get(slug=slug)
    return shortcuts.render_to_response(
        "vacancies_and_studentships/studentship.html",
        {"studentship":studentship}
        )