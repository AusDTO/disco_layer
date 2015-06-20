from django.db import models


class Page(models.Model):

    orient_rid = models.CharField(max_length=256)
    orient_version = models.CharField(max_length=256)
    orient_class = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    
    protocol = models.CharField(max_length=6, null=True, blank=True)
    host = models.CharField(max_length=256, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    path = models.TextField(null=True, blank=True) 
    depth =  models.IntegerField(null=True, blank=True)
    fetched =  models.NullBooleanField(blank=True)
    status = models.CharField(max_length=256, null=True, blank=True)
    lastFetchDateTime = models.DateTimeField(null=True, blank=True)
    nextFetchDateTime =  models.DateTimeField(null=True, blank=True)
    document = models.TextField(null=True, blank=True)

    param_string = models.TextField(null=True, blank=True) # data available?

    # derived data
    document_decoded = models.TextField(null=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.url

