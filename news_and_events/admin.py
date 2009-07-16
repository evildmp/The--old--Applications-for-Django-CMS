import models
from django.contrib import admin

class NewsAndEventsAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True
    list_display = ('short_title', 'date',)
    filter_horizontal = (
        'publishing_destinations', 
        'related_newsarticles', 
        'related_pages', 
        'related_people',
        )
    prepopulated_fields = {
        'slug': ('title',)
            }

class NewsArticleAdmin(NewsAndEventsAdmin):
    fieldsets = (
        (None, {
            'fields': ('short_title', 'title', 'summary', 'content',),
        }),
        ('Where to publish', {
            'fields': ('publishing_destinations',)
        }), 
        ('For further information', {
            'fields': ('please_contact', 'please_see',)
        }),
        ('Related articles, pages and people', {
            'classes': ('collapse',),
            'fields': ('related_newsarticles', 'related_events','related_pages', 'related_people',),
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('date', 'slug',),
        }),
    )
admin.site.register(models.NewsArticle,NewsArticleAdmin)

class EventAdmin(NewsAndEventsAdmin):
    fieldsets = (
        (None, {
            'fields': ('short_title', 'title', 'summary', 'content', 'date', 'date_end',),
        }),
        ('Where to publish', {
            'fields': ('publishing_destinations',)
        }), 
        ('For further information', {
            'fields': ('please_contact', 'please_see',)
        }),
        ('Related articles, pages and people', {
            'classes': ('collapse',),
            'fields': ('related_newsarticles', 'related_events','related_pages', 'related_people',),
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )
admin.site.register(models.Event,EventAdmin)