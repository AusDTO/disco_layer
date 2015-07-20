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

The green items are "strictly open". We encourage their reuse, and support them to the extent we can. The white ones are private, because we need control to provide reliable services, however they are instances of the open artefacts. So no secret sauce, we just keep our discrete instance private (so that we can provide reliable API and user interfaces).


Source Code
-----------

github. Get over it.

http://github.com/AusDTO/


Right now, many of our projects are not shared publically (private repositories in GitHub). This is for a variety of reasons, we expect "almost all repositories are public" to be the norm soon.

Use tickets for issues etc, model ourselves on other sucessful open source projects. This is the primary developer collaboration channel. Documentation and other built artefacts are funnels into this collaboration channel. Tournaments augment this channel (not the other way around).


Development Pipeline
--------------------

The above diagram indicates that the development pipeline is a thing that provides a development dashboard, and depends on source code, built artefacts, backing services and deployed components.

| Of course in reality it's not that simple. Open source development is highly organic  a marketplace for ideas, it resembles a bazaar more than anything else (https://en.wikipedia.org/wiki/The_Cathedral_and_the_Bazaar).

In the following diagrams:
 * collaboration is golden
 * the green items are public / open
 * the ellipses are verb-like things, such as interfaces or activities
 * the rectangles are noun-like things

The diagram also shows a box of white things labelled "administered cloud". The systems inside this box are *core DTO business*, we administer them ourselves and take responsability for their quality. System components outside this box are administered by partners, we are functionality dependant on them however they are our someone else's core business.

.. graphviz::

   digraph d {
      node [shape=ellipse style=filled fillcolor=white];

      repo [label="AusDTO\nrepository" fillcolor=green shape=rectangle];
      maint [label="<<DTO>>\nmaintainer" shape=rectangle];
      developer [shape=rectangle fillcolor=gold];
      od [label="open\ndata" shape=rectangle fillcolor=green];
      ddash [label="development\ndashboard" fillcolor=green];

      fork [label="fork\nrepo" fillcolor=gold];
      prepo [label="personal\nrepository" fillcolor=gold shape=rectangle];
      developer -> fork;
      fork ->prepo;
      fork -> repo;

      edit [label="change\ncode" fillcolor=gold];
      developer -> edit -> prepo;

      pr [label="pull\nrequest" fillcolor=gold];
      developer -> pr;
      pr -> prepo;
      pr -> repo;
      
      tickets [fillcolor=gold label="ticket\nconversations"];
      developer -> tickets -> repo;
      maint -> tickets;
      tickets -> od;
      merge [fillcolor=green];
      tag [fillcolor=green];
      maint -> merge -> pr;
      maint -> tag -> repo;

      subgraph cluster_admin {
         label="administered cloud";
	 jenkins [shape=rectangle];
	 ci [label="automated\ntesting"];
	 cp [label="automated\npublishing"];
	 disco [label="disco\nservices" shape=component];
	 workers [label="disco\nworkers" shape=component];
	 cd [label="automated\ndeployment"];
      }
      analytics [label="analytic\nfeedback"];
      built [label="built\nartefacts" shape=rectangle fillcolor=green];
      ui [label="user\ninterface" fillcolor=green];
      api [label=API fillcolor=green];

      bs [label="backing\nservices" shape=rectangle];

      disco -> bs;
      workers -> bs;

      repo -> ci [dir=back];
      ci -> jenkins;
      ddash -> jenkins
      jenkins -> cp;
      cp -> built;
      jenkins -> cd;
      cd -> built;
      cd -> disco;
      cd -> workers;
      ui -> disco;
      api -> disco;

      analytics -> od;
      analytics -> bs;
   }



Built Artefacts
---------------

Various species of artefact, all versionsed in lock-step (hopefully driven from tags in git). Dogfood/exemplify the tagging and version control elements from the design guide / service standard (when it's written - pester Steve).

.. graphviz::

   digraph d {
      node [shape="rectangle" style=filled fillcolor=white];

      deploy [label="automated\ndeployment" shape=ellipse];
      pub [label="automted\npublishing" shape=ellipse];
      subgraph cluster_built {
         label="built artefacts";
	 rtd [label="readthedocs.org"];
	 dh [label="hub.docker.io"];
	 pypi [label="package\ndistribution\nsystem"];
      }
      pub -> rtd;
      pub -> dh;
      pub -> pypi;

      prod [label="deployed\nsystem" ];

      node [shape=ellipse fillcolor=green];
      docs [label="developer\ndocs"];
      containers [label="linux\ncontainers"];
      libs [label="packaged\nlibraries"];
      
      rtd -> docs [dir=back];
      dh -> containers [dir=back];
      pypi -> libs [dir=back];
      
      deploy -> containers;      
      deploy -> prod;
   }

Docker images. Published through hub.docker.com.

Release management: On every commit to source code, The CI service (Jenkins, part of Development Pipeline) creates a docker images if the tests pass. After testing, the docker image is posted to a private repository (e.g. quay.io). This may be abandoned if we move to continuous delivery. These are then published (pushed to hub.docker.io) in lock-step with deployment. In other words, deploy from the public repository, not the private one (if it needs to exist beyond the present pre-alpha stage).

Technical documentation. Published through readthedocs.org.

Source code packages. Released through github (if required), package management systems, etc.


Deployed Components
-------------------

Commodity infrastructure as a service. Currently docker on Amazon AWS, but whatever.

Architecturally, essentially "12 factor" stateless, horisontaly scailable apps. Push state to backing services, twelve factor style (http://12factor.net/).


Backing Services
----------------

Databases, message queues, search indexes, etc. Where possible, buy "as a service" value added infrastructure to leverage economies of scope and scale.

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];
      disco [label="disco\nservice"];
      discoworker [label="disco\nworker"];
      crawler;
      subgraph cluster_b {
         label="outsourced backing services";
	 database;
	 elasticsearch;
	 mq [label="message\nqueue"];
      }
      crawler -> database;
      discoworker -> database;
      discoworker -> mq;
      discoworker -> elasticsearch;
      disco -> elasticsearch;
   }

Self-hosted implementations are acceptible in the development ecosystems, but pushing to a backing service should be norm during beta and beyond. 
