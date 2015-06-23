from __future__ import absolute_import, unicode_literals
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^search/$', views.about_search, name="about_search"),
    url(r'^api/$', views.about_api, name="about_api"),
    url(r'^for_gov/$', views.about_for_gov, name="about_for_gov"),
    url(r'^hacking/$', views.about_hacking, name="about_hacking"),
)
