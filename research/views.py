import django.http as http
import django.shortcuts as shortcuts
from research.models import *
        
def studentship(request, slug):
    studentship = Studentship.objects.get(slug=slug)
    return shortcuts.render_to_response(
        "research/studentship.html",
        {"studentship":studentship}
        )
