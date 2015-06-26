from django.db import models

class SubService(models.Model):
    cat_id = models.CharField(max_length=512)
    desc = models.TextField()
    name = models.CharField(max_length=512)

    info_url = models.CharField(max_length=512, null=True, blank=True)
    primary_audience = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return self.name

