from django.db import models

class Agency(models.Model):
    acronym = models.CharField(max_length=128)

    def __unicode__(self):
        return self.acronym


class SubService(models.Model):
    cat_id = models.CharField(max_length=512)
    desc = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=512, null=True, blank=True)
    info_url = models.CharField(max_length=512, null=True, blank=True)
    primary_audience = models.CharField(max_length=512, null=True, blank=True)
    agency = models.ForeignKey(Agency, default=1)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ['agency','cat_id']


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


class Service(models.Model):
    # composite key
    src_id  = models.CharField(max_length=256)
    agency = models.ForeignKey(Agency, default=1)
    # M:N
    service_types = models.ManyToManyField(ServiceType)
    service_tags =  models.ManyToManyField(ServiceTag)
    life_events =  models.ManyToManyField(LifeEvent)
    # optional properties
    old_src_id = models.IntegerField(null=True, blank=True)
    json_filename  = models.CharField(max_length=512, null=True, blank=True)
    info_url = models.CharField(max_length=512, null=True, blank=True)
    name = models.CharField(max_length=512, null=True, blank=True)
    acronym = models.CharField(max_length=512, null=True, blank=True)
    tagline = models.CharField(max_length=512, null=True, blank=True)
    primary_audience = models.CharField(max_length=512, null=True, blank=True)
    analytics_available = models.CharField(max_length=512, null=True, blank=True)
    incidental = models.CharField(max_length=512, null=True, blank=True)
    secondary = models.CharField(max_length=512, null=True, blank=True)
    src_type = models.CharField(max_length=512, null=True, blank=True)
    description  = models.TextField(null=True, blank=True)
    comment  = models.TextField(null=True, blank=True)
    current = models.CharField(max_length=512, null=True, blank=True)
    org_acronym  = models.CharField(max_length=64, null=True, blank=True) # TODO, remove

    class Meta:
        unique_together = ['agency','src_id']

    def __unicode__(self):
        return "%s: %s: %s" % (self.agency.acronym, self.src_id, self.name)


class Dimension(models.Model):
    # dim_id + agency are unique
    dim_id = models.CharField(max_length=512)
    agency = models.ForeignKey(Agency)
    name = models.CharField(max_length=512, null=True, blank=True)
    dist = models.IntegerField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    info_url = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        unique_together = ['agency','dim_id']

