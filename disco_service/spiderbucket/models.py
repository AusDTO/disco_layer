from django.db import models


class Page(models.Model):
    protocol = models.CharField(max_length=6)
    domain = models.CharField(max_length=256)
    url = models.CharField(max_length=256, null=True, blank=True)
    param_string = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    excerpt = models.TextField()
    
    def __unicode__(self):
        uri = "%s://%s/" % (self.protocol, self.domain)
        if self.url:
            uri = "%s%s" % (uri, self.url)
        if self.param_string:
            uri = "%s?%s" % (uri, self.param_string)
        return uri
