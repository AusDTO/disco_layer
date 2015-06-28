from django.db import models

class SubService(models.Model):
    cat_id = models.CharField(max_length=512)
    desc = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=512, null=True, blank=True)
    info_url = models.CharField(max_length=512, null=True, blank=True)
    primary_audience = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return self.name

class ServiceTag(models.Model):
    label = models.CharField(max_length=512)
    def __unicode__(self):
        return self.label

class LifeEvent(models.Model):
    label = models.TextField()
    def __unicode__(self):
        return self.label

class ServiceType(models.Model):
    label = models.TextField()
    def __unicode__(self):
        return self.label
