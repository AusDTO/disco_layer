Overview
========

These are technical documents, they are only concerned with what and how. Specifics of who and when are contained in the git logs. This blog post explains why and where:

https://www.dto.gov.au/news-media/blog/making-government-discoverable


.. graphviz::

   digraph d {
      node [shape="rectangle" style=filled fillcolor=white];
      rankdir=LR;

      pui [label="user\ninterface" shape=ellipse fillcolor=green];
      api [label="API" shape=ellipse fillcolor=green];
      
      subgraph cluster_app {
         label="discovery service"
	 worker;
	 nginx [label="reverse\nproxy"];
	 app [label="apps" shape=folder];
      }
      subgraph cluster_support {
         label="supporting tools";
	 crawler;
	 mt [label="metadata\nmanagement"];
      }
      
      pui -> nginx;
      api -> nginx;

      bs [label="backing\nservices" fillcolor=lightgrey];
      pub [label="public\ndata" shape=folder fillcolor=green];
      pub -> mt [dir=back];
      pub -> crawler [dir=back];
      pub -> worker [dir=back];
      crawler -> bs;
      nginx -> app -> bs;
      nginx -> bs;
      worker -> bs;
   }


The user discovery later aims to provide useful features that enable users and 3rd party applications to discover government resources. It is currently in pre-ALPHA status, meaning a working technical assessment, not yet considered suitable for public use (even by "early-adopters").


Development
-----------

Discovery service:

 * http://github.com/AusDTO/discoveryLayer Code
 * http://github.com/AusDTO/discoveryLayer/issues Discussion
 * http://waffle.io/AusDTO/discoveryLayer Kanban
 * http://ausdto-discovery-layer.readthedocs.org/ Documentation

Crawler:

 * http://github.com/AusDTO/disco_crawler Code 
 * http://github.com/AusDTO/disco_crawler/issues Discussion
 * http://ausdto-disco-crawler.readthedocs.org/ Documentation

Metadata management (currently service catalogue):

 * http://github.com/AusDTO/serviceCatalogue Code 
 * http://github.com/AusDTO/serviceCatalogue/issues Discussion
 * http://ausdto-service-catalogue.readthedocs.org/ Documentation

