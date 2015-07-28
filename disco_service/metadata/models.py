from django.db import models
from goose import Goose
import base64

class Page(models.Model):

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

    ### implement as derived data / @property decorator
    #param_string = models.TextField(null=True, blank=True) # data available?
    # derived data
    #document_decoded = models.TextField(null=True, blank=True)
    #excerpt = models.TextField(null=True, blank=True)
    #title = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.url

    def _decode(self):
        return base64.standard_b64decode(self.document)

    def _article(self):
        # faster if cached?
        g = Goose()
        return g.extract(raw_html=self._decode())

    def title(self):
        # assumes type=HTML
        # more to do for other types...
        try:
            return self._article().title
        except:
            return "(no title)"

    def excerpt(self):
        # memcache this,
        # would require working evict-on-save (use signals, test it)
        try:
            return self._article().cleaned_text
        except:
            return "(no text)"

    def get_absolute_url(self):
        return "%s" % self.url

    def sr_summary(self):
        '''
        Doesn't even break on word boundaries... This is a rude hack. 

        There should be a much, much smarter thing that populates a 
        short display excerpt in the index.
        '''
        long_excerpt = self.excerpt()
        if len(long_excerpt) < 300:
            return long_excerpt
        else:
            return long_excerpt[:300]
