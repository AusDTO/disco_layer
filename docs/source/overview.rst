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
      ui [label="user\ninterfaces" shape=ellipse];
      api [label="API" shape=ellipse];
      colab [label="collaborate" shape=ellipse ];
      pub [label="publish/release" shape=ellipse];
      ddash [label="development\ndashboards" shape=ellipse];
      pipe [label="development\npipeline" fillcolor=green];
      build [label="built\nartefacts" shape=folder fillcolor=green]; 
      src [label="source\ncode" shape=folder fillcolor=green];

      subgraph cluster_private {
	  deployed [label="deployed\ncomponents" shape=folder fillcolor=orange];
	  backing [label="backing\nservices" shape=folder fillcolor=orange];
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

The green items are "strictly open". We encourage their reuse, and support them to the extent we can. The orange ones are private, because we need control to provide reliable services, however they are instances of the open artefacts. So no secret sauce, we just keep our discrete instance private (so that we can provide reliable API and user interfaces).


Source Code
-----------

github. Get over it.

http://github.com/AusDTO/


Right now, many of our projects are not shared publically (private repositories in GitHub). This is for a variety of reasons, we expect "almost all repositories are public" to be the norm soon.

 Use tickets for issues etc, model ourselves on other sucessful open source projects. This is the primary developer collaboration channel. Documentation and other built artefacts are funnels into this collaboration channel. Tournaments augment this channel (not the other way around).


Built Artefacts
---------------

Various species of artefact, all versionsed in lock-step (driven from tagging protocol in the versino control system). Dogfood/Exemplify the tagging and version control elements from the design guide / service standard.

Docker images. Published through hub.docker.com.

Release management: On every commit to source code, The CI service (Jenkins, part of Development Pipeline) creates a docker images if the tests pass. After testing, the docker image is posted to a private repository (e.g. quay.io). This may be abandoned if we move to continuous delivery. These are then published (pushed to hub.docker.io) in lock-step with deployment. In other words, deploy from the public repository, not the private one (if it needs to exist beyond the present pre-alpha stage).

Technical documentation. Published through readthedocs.org.

Source code packages. Released through github (if required), package management systems, etc.


Development Pipeline
--------------------

Continuous Integration / Deployment using jenkins. Current pipeline (target state, per repository), after change on any branch:

 * readthedocs.org callback; update technical docs
 * jenkins callback; test suites (unit, functional, ...)
 * tests pass (jenkins); build container, publish (to private registry?) 
 * decision to release/deploy; kill deployed component, respawn (uses public latest)

Jenkins is configured to use GitHub auth. anon can see results/history but not change config or trigger jobs. So built/tests behavior is pegged to source code (pull requests welcome).


Deployed Components
-------------------

Commodity infrastructure as a service. Currently docker on Amazon AWS, but whatever.

Architecturally, essentially "12 factor" stateless, horisontaly scailable apps. Push state to backing services.


Backing Services
----------------

Databases, message queues, search indexes, etc. Where possible, buy "as a service" value added infrastructure to leverage economies of scope and scale.

Self-hosted implementations are acceptible in the development ecosystems, but pushing to a backing service should be norm during beta and beyond. 
