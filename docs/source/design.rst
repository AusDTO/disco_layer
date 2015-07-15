Design
======

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];

      subgraph cluster_njs {
         label="<<node.js>>";
	 crawl [shape=ellipse];
      }
      subgraph cluster_govau {
      label="<<www>>";
      pub [label="all of the\nCommonwealth\nonline resources" fillcolor=green];
      }
      crawl -> pub;

      subgraph cluster_pg {
      label="<<postgres>>";
	content_db [label="database of all\nthe content"];
	stage_db [label="metadata\nstage"];
      }
      crawl -> content_db;

      subgraph cluster_od {
         label="<<open data>>";
	 srvcat [label="service\ncatalogue" fillcolor=green];
	 traffic [label="web traffic" fillcolor=green];
      }
      subgraph cluster_celery {
         label="<<python:celery>>";
         extract [label="extract\ninformation" shape=ellipse];
         manage [label="manage\nmetadata" shape=ellipse];
         maintain [label="maintain\nindexes" shape=ellipse];
      }
      subgraph cluster_es {
         label="<<elasticsearch>>";
         indexes [label="search\nindexes"];
         raw_api [label="low-level\nsearch API" fillcolor=green shape=ellipse];
      }
      extract -> content_db;
      extract -> stage_db;
      manage -> stage_db;
      srvcat -> manage [dir=back];
      traffic -> manage [dir=back];
      maintain -> stage_db;
      maintain -> indexes;
      raw_api -> indexes;

      subgraph cluster_disco {
         label="<<python:django>>"
	 disco [label="discovery\nservices"];
	 api [label="high-level\nAPI" shape=ellipse fillcolor=green];
	 ui [label="user\ninterface" shape=ellipse fillcolor=green];
      }
      disco -> raw_api;
      api -> disco;
      ui -> disco;
      
   }


In the above diagram:
 * green items are fully public/open
 * white items are private instances of open source code
 * rectangles are noun-like things, components of the system
 * ellipses are verb-like things such as tasks or interfaces


Open interfaces
---------------

The green ellipses are interfaces.

The discovery service **user interface** is a mobile-friendly web application. It is a place to impliment "consierge service" type features, that assist people locate government resources. The DEV team consideres it least likely to be important over the long term, but likely to be useful for demonstrations and proofs of concept.

The discovery service **high-level API** is a REST integration surface, designed to support/enable discoverability features in other applications (such as Commonwealth web sites). They are essentially wrappers that exploit the power of the low-level search API in a way that is convenient to users. The DEV team considers it highly-likely that signifacant value could be added at this layer.

The **low-level search API** is simply the read-only part of the native elasticsearch interface. It's our post-processed data, derived from public web pages and open data, using our open source code. We don't know if or how other people might use this interface, but would be delighted if that happened.


Public Resources
----------------

The green rectangles are public resources. Either open data (published at data.gov.au) or content from Commonwealth web sites. This dovetails into other DTO work on service catalogue and analytics.


Outsourced Workload
-------------------

The white elippses are tasks performed by commodity cloud infrastructure, using instances of our open source code (either python code running in celery worker processes, or javascript code running in a node worker processes). This compute workload is administered by DTO, because we are responsible for the search index content.

The **discovery service** is special. It's the only service component that DTO administers. That's because it's our unique product and we want to make it the best it can possibly be. So we add the value to commodity *Infrastructure as a Service* in this unusual instance.

For production, the box labelled "<<postgres>>" is outsourced (to a *Database as a Service* provider). This is because we think it's better value than diverting our time into database administration. There are numerous self-hosted postgres servers in our development environment however (typically using the default postgres:latest docker image, see `docker-compose.yml` files in the repository)

The elasticsearch **search indexes** are currently actually self-hosted on commodity cloud infrastructure, however we aspire to move these to *Elasticsearch as a Service* when we get round to it. We are likely to do this when/before we release a public beta.


Crawling all the things
-----------------------

The node.js crawler app is currently found in the `crawler/` folder of the https://github.com/AusDTO/discoveryLayer repository. We expect to split it out into it's own repository sooner or later. It suits our needs very well right now, but at some point we may replace it with a more sophistocated turnkey system such as apache nutch.

The crawler is packaged in a docker container, where a cron job kicks off a crawling job at predetermined schedule (see `crawler/crontab.txt`). That job does three things:
 * schedules "resource visits" based on the database content
 * visits resources per the schedule, and updates the database if they have changed
 * examines links in the pages it fetches, and schedules visits to any new resources found

The crawler only visits Commonwealth resources (.gov.au domains, currently excluding state subdomains). The result of all that is that the database fills up with "all the Commonwealth resources", those resources are checked on a regulalar schedule and the database is updated when they change.


Adding value to public resources
--------------------------------

The crawling activity creates and maintains a database of all the content. There are three value-adding post-processing steps that result in the useful search index which powers the discovery services. They are:
 * extract information
 * manage metadata
 * maintain indexes

In the simplest case, the information extraction step could simply take a copy of the resource (which may be in one of various formats) and create a text representation ofit. For example, this is currently done for HTML content using the python Goose library (https://pypi.python.org/pypi/goose-extractor). PDF article extraction is yet to be implemented, but shelling-out to the pdftotxt tool from Xpdf (http://www.foolabs.com/xpdf/download.html) might work OK. The DBPedia open source project  has some much more sophistocated information extraction features (http://dbpedia.org/services-resources/documentation/extractor) which may be relevent as new requirements emerge in this step.

The metadata management step combines the extracted information with aditional data, such as context from the service catalogue. In a very simple case, this might be contextural information such as "this page is associated with that service" or observations about user behavior (e.g. this is a popular page). There are potentially many kinds of supplimentary data that could be incorporated here, however development will be driven by the requirements of the index maintainer.

The search indexes are maintained using the excellent django-haystack library (http://haystacksearch.org/).

