from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _, get_language

from news_and_events.models import NewsArticle
from contacts_and_people.models import Entity

class LatestNewsArticles(Feed):
    title = "cardiff news"
    description = "all the cardiff news in one place"
    link = '/'
    
    title_template = 'news_and_events/feeds/entry_title.html'
    description_template = 'news_and_events/feeds/entry_description.html'
    
    def items(self):
        return NewsArticle.objects.order_by('-date')

class LatestEntityNewsArticles(LatestNewsArticles):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Entity.objects.get(slug__exact=bits[0])
    def items(self, obj):
        return NewsArticle.objects.filter(publishing_destinations=obj).order_by('-date')
    
    def title(self, obj):
        return u'%s' % obj
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
    def description(self, obj):
        return 'News relevant for the entity "%s"' % obj


        

