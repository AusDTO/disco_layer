"""
metadata.models
===============

.. autoclass:: metadata.models.Resource
   :members:
   :private-members: _article _decode


"""

from django.db import models
from goose import Goose
#import base64
from crawler.models import WebDocument

class Resource(models.Model):
    """ORM class wrapping persistent data of the web resource
    
    Contains hooks into the code for resource processing
    """
    url = models.CharField(max_length=256)
    _hash = models.CharField(
        db_column='hash', max_length=255,
        blank=True, null=True)
    protocol = models.CharField(max_length=6, null=True, blank=True)
    contenttype = models.CharField(max_length=256, null=True, blank=True)
    host = models.CharField(max_length=256, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    path = models.TextField(null=True, blank=True) 
    depth =  models.IntegerField(null=True, blank=True)
    #fetched =  models.NullBooleanField(blank=True)
    #status = models.CharField(max_length=256, null=True, blank=True)
    lastFetchDateTime = models.DateTimeField(null=True, blank=True)
    #nextFetchDateTime =  models.DateTimeField(null=True, blank=True)
    #document = models.TextField(null=True, blank=True)

    ### implement as derived data / @property decorator
    #param_string = models.TextField(null=True, blank=True) # data available?
    # derived data
    #document_decoded = models.TextField(null=True, blank=True)
    #excerpt = models.TextField(null=True, blank=True)
    #title = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.url

    def _decode(self):
        """Lookup content of the coresponding WebDocument.document"""
        # cache this method
        wd = WebDocument.objects.filter(url=self.url).get()
        return wd.document 

    def _article(self):
        """Analyse resource content, return Goose interface"""
        # switch method depending on content_type
        # for pdf, fall back to teseract if pdf2text yields not much
        # (then use the larger, or maybe composit)
        g = Goose()
        return g.extract(raw_html=self._decode())

    def title(self):
        """Attempt to produce a single line description of the resource"""
        # assumes Goose interface
        try:
            return self._article().title
        except:
            return "(no title)"

    def excerpt(self):
        """Attempt to produce a plain text version of resource content"""
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
        Search result summary.

        This is a rude hack, it doesn't even break on word boundaries.
        There should be much smarter ways of doing this.
        '''
        long_excerpt = self.excerpt()
        if len(long_excerpt) < 300:
            return long_excerpt
        else:
            return long_excerpt[:300]

