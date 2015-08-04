Design
======

The discovery layer is designed using the "pipeline" pattern. It processes public data (including all Commonwealth web sites) to produce a search indexes of enriched content metadata. These search indexes provide a public, low-level (native) search API, which is used by the discovery service to power user interface and high-level API features.

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];

      crawl [label="1.\ncrawl" shape=ellipse];
      pub [label="all the\nCommonwealth\nweb" fillcolor=green shape=folder];
      crawl -> pub;

      content_db [label="database of all\nthe content"];
      stage_db [label="content\nmetadata"];
      crawl -> content_db;

      od [label="public\ndata" shape=folder fillcolor=green];

      extract [label="2.\nextract\ninformation" shape=ellipse];
      enrich [label="3.\nenrich\nmetadata" shape=ellipse];
      maintain [label="4.\nmaintain\nindexes" shape=ellipse];
      
      indexes [label="search\nindexes"];
      raw_api [label="low-level\nsearch API" fillcolor=green shape=ellipse];
      
      extract -> content_db;
      extract -> stage_db;
      enrich -> stage_db;
      od -> enrich [dir=back];
      maintain -> stage_db;
      maintain -> indexes;
      raw_api -> indexes;

      disco [label="discovery\nservices"];
      api [label="high-level\nAPI" shape=ellipse fillcolor=green];
      ui [label="user\ninterface" shape=ellipse fillcolor=green];
      
      disco -> raw_api;
      api -> disco;
      ui -> disco;
      
   }


Pipeline:
 1. Crawl a database of content from the Commonwealth web.
 2. Extract information into a metadata repository, from the content database.
 3. Enrich content metadata using public data.
 4. Maintain search indexes from content metadata.


Activities
----------

In the above diagram, white ellipses represent activities performed by discovery layer components.


Crawling content
^^^^^^^^^^^^^^^^

The crawler component is a stand-alone product located in it's own GitHub repository (https://github.com/AusDTO/disco_crawler). It suits our needs OK right now, but at some point we may replace it with a more sophistocated turnkey system such as apache nutch.

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];
      crawl [label="crawl" shape=ellipse];
      pub [label="all the\nCommonwealth\nweb" fillcolor=green shape=folder];
      crawl -> pub;
      content_db [label="database of all\nthe content"];
      crawl -> content_db;      
   }


The crawler only visits Commonwealth resources (.gov.au domains, excluding state subdomains). The result of all that is that the database fills up with "all the Commonwealth resources", those resources are checked on a regulalar schedule and the database is updated when they change.


Information Extraction
^^^^^^^^^^^^^^^^^^^^^^

The information extraction step is currently very simple. It ignores everything except html resources, and performs a simple "article extraction" using the python Goose library (https://pypi.python.org/pypi/goose-extractor). 

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];
      content_db [label="database of all\nthe content"];
      stage_db [label="content\nmetadata"];
      extract [label="extract\ninformation" shape=ellipse];
      extract -> content_db;
      extract -> stage_db;      
   }


PDF article extraction is yet to be implemented, but shelling-out to the pdftotxt tool from Xpdf (http://www.foolabs.com/xpdf/download.html) might work OK. Encourageing results have been obtained from scanned PDF documents using Teseract (https://github.com/tesseract-ocr/tesseract),

The DBPedia open source project  has some much more sophistocated information extraction features (http://dbpedia.org/services-resources/documentation/extractor) which may be relevent as new requirements emerge in this step. Specifically, their distributed extraction framework (https://github.com/dbpedia/distributed-extraction-framework) using Apache Spark seems pretty cool. This might be relevant to us if we wanted to try and migrate or syncicate Commonwealth web content(however, this might not be fesible doe to the  diversity of page structures that would need to be modelled).


Metadata enrichment
^^^^^^^^^^^^^^^^^^^

The metadata enrichment step combines the extracted information with aditional data from public sources. Currently this is limited to "information about government services" sourced from the service catalogue component.

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];
      stage_db [label="content\nmetadata"];
      od [label="public\ndata" shape=folder fillcolor=green];
      enrich [label="enrich\nmetadata" shape=ellipse];
      enrich -> stage_db;
      od -> enrich [dir=back];      
   }


The design intent is that this enrichment step would draw on rich sources of knowledge about government services - essentially, releaving users of the burden of having to understand how the government is structured to access it's content.

Technically this would be when faceting data is incorporated; user journeys (scenarios), information architecture models, web site/page tagging and classification schemes, etc. This metadata might be manually curated/maintained (e.g. web site classification), automatically produced (e.g. natural language processing, automated clustering, web traffic analysis, semantic analysis, etc) or even folksonomically managed. AGLS metadata (enriched with synonyms?) might also be used to produce potentialy useful facets.

Given a feedback loops from passive behavior analysis (web traffic) or navigation choice-decision experiments (A-B split testing, ANOVA/MANOVA designs etc), information extraction could be treated as a behavior laboritory for creating value in search-oriented architecture at other layers. Different information extraction schemes (treatments) could be operated to produce/maintain parallel indexes, and discovery-layer nodes could be randomly assigned to indexes.  


maintain indexes
^^^^^^^^^^^^^^^^

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];
      stage_db [label="content\nmetadata"];
      maintain [label="maintain\nindexes" shape=ellipse];
      indexes [label="search\nindexes"];
      maintain -> stage_db;
      maintain -> indexes;
   }


The search indexes are maintained using the excellent django-haystack library (http://haystacksearch.org/). Specifically, using the asynchronous celery_haystack module (https://github.com/django-haystack/celery-haystack).

Using this module, index-management tasks are triggered by "save" signals on the ORM model that the index is based on. Because the crawler is NOT using the ORM, inserts/updates/deleted by the crawler do not automatically trigger these tasks. Instead, scheduled jobs compare content hash fields in the drawler's database and the metadata to detect differences and dispatch metadata updates apropriately.

.. note::

   The US Digital GovSearch service is trying out a search index management feture called i14y (Beta) to push CMS content changes to their search layer for reindexing. http://search.digitalgov.gov/developer/


Interfaces
----------

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];

      indexes [label="search\nindexes"];
      raw_api [label="low-level\nsearch API" fillcolor=green shape=ellipse];
      disco [label="discovery\nservices"];
      api [label="high-level\nAPI" shape=ellipse fillcolor=green];
      ui [label="user\ninterface" shape=ellipse fillcolor=green];
      raw_api -> indexes;
      disco -> raw_api;
      api -> disco;
      ui -> disco;
   }


In the above diagram, green ellipses represent interfaces. The colour green is used to indicate that the items are open for public access.


user interface
^^^^^^^^^^^^^^

The discovery service **high-level API** is a REST integration surface, designed to support/enable discoverability features in other applications (such as Commonwealth web sites). They are essentially wrappers that exploit the power of the low-level search API in a way that is convenient to users. The DEV team considers it highly-likely that signifacant value could be added at this layer.

The discovery service **user interface** is a mobile-friendly web application. It is a place to impliment "consierge service" type features, that assist people locate government resources. The DEV team consideres it least likely to be important over the long term, but likely to be useful for demonstrations and proofs of concept.

These are imagined to be user-friendly features for finding (searching and/or browsing) Australian Government online resources. The current pre-ALPHA product does not have significant features here yet, because we are just entering "discovery phase" on that project (we are in the process of gathering evidence and analysing user needs).

In adition to conventional search features, the "search oriented architecture" paradigm contains a number of patterns (such as faceted browsing) that are likely to be worthy of experiment during ALPHA and BETA stages of development.  


high-level API
^^^^^^^^^^^^^^

Two kinds of high-level API features are considered likely to prove useful.

 * Machine-consumable equivalents of the user-interface features
 * Framework for content analysis 

The first type of high-level API is simply a REST endpoint supporting json or xml format, 1:1 exact mapping of functionality. It should be useful for integrating 3rd party software with the discovery layer infrastructure.

The second type of high-level API is the python language interface provided by django-haystack, the framework used to interface and manage the search indexes. This API is used internally to make the first kind of API and the user interfaces. It's also potentially useful for extending the service with new functionality, and analytic use-cases (as evidenced by ipython notebook content analysis, TODO).
 

low-level search API
^^^^^^^^^^^^^^^^^^^^

The **low-level search API** is simply the read-only part of the native elasticsearch interface. It's our post-processed data, derived from public web pages and open data, using our open source code. We don't know if or how other people might use this interface, but would be delighted if that happened.

The search index backing service has a REST interface for GETing, POSTing, PUTing and DELETEing the contents of the index. The GET verbs of this interface is published directly through the reverse-proxy component of the discovery layer interface, allowing 3rd parties to reuse our search index (either with code based on our high-level python API, or any other software that supports the same kind of search index).

BETA version of the discovery layer probably requires throttling and/or other forms of protection from queries that would potentially degrade performance.
 

Components
----------

TODO: define each rectangle in above diagram

TODO: salvage good bits of the following gumphf into above definitions.

