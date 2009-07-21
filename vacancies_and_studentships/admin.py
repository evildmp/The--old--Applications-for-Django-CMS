import models
from django.contrib import admin

class VacancyAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'host_entity', 'closing_date',)
    filter_horizontal = (
        'also_advertise_on', 
    )
    prepopulated_fields = {
        'slug': ('short_title',)
            }
    fieldsets = (
        (None, {
            'fields': ('short_title', 'title', 'closing_date', 'salary', 'job_number', 'description',),
        }),
        ('Institutional details', {
            'fields': ('host_entity',)
        }), 
        ('For further information', {
            'fields': ('please_contact', 'also_advertise_on', 'please_see',)
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )
admin.site.register(models.Vacancy,VacancyAdmin)

class StudentshipAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'host_entity', 'closing_date',)
    filter_horizontal = (
        'also_advertise_on', 
        'supervisors', 
    )
    prepopulated_fields = {
        'slug': ('short_title',)
            }
    fieldsets = (
        (None, {
            'fields': ('short_title', 'title', 'closing_date', 'description',),
        }),
        ('Supervision', {
            'fields': ('supervisors','host_entity',)
        }), 
        ('For further information', {
            'fields': ('please_contact', 'also_advertise_on', 'please_see',)
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )
admin.site.register(models.Studentship,StudentshipAdmin)