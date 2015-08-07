"""
metadata.search_indexes
=======================

.. autoclass:: metadata.search_indexes.ResourceIndex

.. autoclass:: metadata.search_indexes.ServiceIndex

"""

import datetime
from celery_haystack.indexes import CelerySearchIndex
from haystack import indexes
from metadata.models import Resource
from govservices.models import Service

class ResourceIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="title")
    url = indexes.CharField(model_attr="url")
    protocol = indexes.CharField(model_attr="protocol")
    host = indexes.CharField(model_attr="host")
    port = indexes.IntegerField(model_attr="port")
    #path = indexes.CharField(model_attr="path")
    #depth =  indexes.IntegerField(model_attr="depth")
    #lastFetchDateTime = indexes.DateTimeField(model_attr="lastFetchDateTime")
    #nextFetchDateTime =  indexes.DateTimeField(model_attr="nextFetchDateTime")

    def get_model(self):
        return Resource

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects

    def prepare_title(self, obj):
        return "%s" % obj.title()


class ServiceIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    #url = indexes.CharField(model_attr="info_url")
    #acronym = indexes.CharField(model_attr="acronym")
    #tagline = indexes.CharField(model_attr="tagline")
    #agency = indexes.CharField(model_attr="agency")

    def get_model(self):
        return Service

    def index_queryset(self, using=None):
        return self.get_model().objects

    def prepare_agency(self, obj):
        return "%s" % obj.acronym()

    #def prepare_url(self, obj):
    #    return "foo"

