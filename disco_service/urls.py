from django.conf.urls import include, url
from django.contrib import admin
import metadata.views 
import haystack.views

urlpatterns = [
    url(r'^$', metadata.views.index, name='home'),
    url(r'^search/$', haystack.views.SearchView(), name='search'),
    url(r'^api/$', metadata.views.api, name='api'),
    url(r'^for_gov/$', metadata.views.for_gov, name='for_gov'),
]
