from django.contrib import admin
from .models import City, Attraction, Bookmark, AttractionRating

admin.site.register(City)
admin.site.register(Attraction)
admin.site.register(AttractionRating)
admin.site.register(Bookmark)

admin.site.site_header = 'Scottish Tourism Recommendation System Management Backend'
admin.site.site_title = 'Scottish Tourism Recommendation System'
admin.site.index_title = 'Welcome to the Scottish Travel Recommendation System Management Backend'