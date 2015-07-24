from django.conf.urls import include, url
from django.contrib import admin
import spiderbucket.views 
import haystack.views

urlpatterns = [
    url(r'^$', spiderbucket.views.index, name='home'),
    url(r'^search/$', haystack.views.SearchView(), name='search'),
    url(r'^api/$', spiderbucket.views.api, name='api'),
    url(r'^for_gov/$', spiderbucket.views.for_gov, name='for_gov'),
    #url(r'^intro/', include('spiderbucket.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^search/', include('haystack.urls')),
]
