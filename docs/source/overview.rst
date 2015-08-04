Overview
========

These are technical documents, they are only concerned with what and how. 

This blog post explains why and where:

https://www.dto.gov.au/news-media/blog/making-government-discoverable

Specifics of who and when are contained in the git logs.


.. graphviz::

   digraph d {
      node [shape="rectangle" style=filled fillcolor=white];
      rankdir=LR;
      ui [label="user\ninterfaces" shape=ellipse fillcolor=green];
      api [label="API" shape=ellipse fillcolor=green];
      colab [label="collaborate" shape=ellipse fillcolor=gold];
      pub [label="publish/release" shape=ellipse];
      ddash [label="development\ndashboards" shape=ellipse fillcolor=green];
      pipe [label="development\npipeline"];
      build [label="built\nartefacts" shape=folder fillcolor=green]; 
      src [label="source\ncode" shape=folder fillcolor=green];

      subgraph cluster_private {
	  deployed [label="deployed\ncomponents" shape=folder];
	  backing [label="backing\nservices" shape=folder];
      }
      
      ui -> deployed;
      api -> deployed;
      colab -> src;
      pub -> build;
      ddash -> pipe;
      pipe -> src;
      pipe -> build;
      pipe -> backing;
      pipe -> deployed;
      build -> src;
      deployed -> backing;
      deployed -> build;
   }

The green items are "strictly open". We encourage their reuse, and support them to the extent we can. The white ones are private, however they are instances of the open artefacts. So no secret sauce, we just keep our discrete instance private (so that we can provide reliable API and user interfaces).


Development
-----------

Discovery layer itself:

 * http://github.com/AusDTO/discoveryLayer Code
 * http://github.com/AusDTO/discoveryLayer/issues Discussion
 * http://waffle.io/AusDTO/discoveryLayer Kanban
 * http://ausdto-discovery-layer.readthedocs.org/ Documentation

Also depends on disco_crawler:

 * http://github.com/AusDTO/disco_crawler Code 
 * http://github.com/AusDTO/disco_crawler/issues Discussion
 * http://ausdto-disco-crawler.readthedocs.org/ Documentation

And depends on serviceCatalogue:

 * http://github.com/AusDTO/serviceCatalogue Code 
 * http://github.com/AusDTO/serviceCatalogue/issues Discussion
 * http://ausdto-service-catalogue.readthedocs.org/ Documentation

