import models
from django.contrib import admin

class StudentshipAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'start_date',)
    filter_horizontal = (
        'advertise_on', 
        'host_entities', 
        'supervisors', 
    )
    prepopulated_fields = {
        'slug': ('short_title',)
            }
    fieldsets = (
        (None, {
            'fields': ('short_title', 'title', 'start_date', 'description',),
        }),
        ('Supervision', {
            'fields': ('supervisors','host_entities',)
        }), 
        ('For further information', {
            'fields': ('please_contact', 'advertise_on', 'please_see',)
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )
admin.site.register(models.Studentship,StudentshipAdmin)