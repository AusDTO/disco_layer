Value Propositions
==================

This page is a bunch of ideas about how the discovery layer could demonstrate it's use. It's really just a sketch, a conversation starter. As it becomes more resolved it should be refactored into a dynamic online conversation (probably move the better ideas into the ticket/comment collaboration channel).

The value propositions currently fall into two broad groups:
 * new features than improve existing online resources
 * analytic inisghts that drive improvement


Improve existing online resources
---------------------------------

Widgets that government webmasters incorporate into their sites to make them better.

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];

      subgraph cluster_website {
         label="<<discovery-enhanced web resource>>";
	 info [label="informative\ncontent"];
	 menu [label="traditional\nnavigation\nstructures"];
	 cms [label="content\nmanagement\nsystem"];
	 widget [label="disco\nwidget" fillcolor=gold];
	 info -> cms;
	 menu -> cms;
      }
      ux [label="user\nexperience" shape=ellipse];
      ux -> info;
      ux -> menu;
      ux -> widget;

      api [label="high-level\ndiscovery\nAPI" shape=ellipse];
      disco [label="disco service" shape=component];
      widget -> api -> disco;
   }


These widgets provide useful functionality, such as:
 * conventional "search this site" search engine functionality
 * algorithmic navigation ("content recommendation engine")
 * instrumentation to support analytics / dashboard features
 * whatever other features we discover are usefull using an open minded, consultation-driven and empirical development approach.


Conventional search
^^^^^^^^^^^^^^^^^^^

Many government sites implement their own "search this site" feature. Using our index, it is possible to search all the resources. It's should be trivialy simple (famous last words?) to apply a filter to create a "search this site" service for any indexed site.

.. graphviz::

   digraph d {
      node [shape=rectangle style=filled fillcolor=white];
      subgraph cluster_asis {
         label="current situation: siloed search";
	 ux1 [label="user\nexperience" shape=ellipse fillcolor=green];
	 subgraph cluster_silo {
	    label="agency site";
	    sw1 [label="bespoke\nsearch\nwidget"];
	    se1 [label="local\nsearch\nengine" shape=component];
	 }
	 ux1 -> sw1 -> se1;
      }
      subgraph cluster_tobe {
         label="future state: common platform";
	 ux2 [label="user\nexperience" shape=ellipse fillcolor=green];
	 subgraph cluster_shared {
	    label="agency site";
	    sw2 [label="local instance of\ndisco search widget" fillcolor=gold];
	 }
	 subgraph cluster_common {
	    label="shared service";
	    se2 [label="open\nsearch\nAPI" shape=ellipse fillcolor=green];
	    se2b [label="disco service" shape=component];
	 }
	 ux2 -> sw2 -> se2 -> se2b;
      }
   }

This would be valuable from a shared-service perspective. By providing this through an open API, agencies will not need to continue paying for third party search providers. It might also create an opportunity to focus more of the existing search expertise onto a common platform, improving search across government.

A conventional search widget is a potentially low-impact change to existing sites, which could connect the sites to our analytics instrumentation as a highly desirable side effect.


Algorithmic navigation
^^^^^^^^^^^^^^^^^^^^^^

tl;dr!

Imagine a small bird starting each day with a choice: should I spend today scratching around for seeds, or should I go hunting for a big juicy worm? If I hunt, I will get nothing to eat until I get to feast, but it's highly uncertain how long that will take. If I gather, I will be eating small frequent meals throughout the day (and my day wil be spent scratching around in the dirt, again, <sigh>).

Bird geeks have observed something cool (https://en.wikipedia.org/wiki/Optimal_foraging_theory). For a given environment, if gathering behavior will take 80% ( or $x %)of the sunlight hours to meet a bird's nutritional requirements, then birds will typically spend the first 20% (or 100-$x %) of the day exhibiting hunting behavior and then switch to gathering for the rest of the day. Unless they hit paydirt when hunting, in which case the spent the rest of the day on nestbuilding, courtship, and other things they would rather be doing than scratching around in the dirt. And so it also is with online user behavior...

Users typically hunt (browse using links and menus) for the resources they need until they run out of patience, at which point their behavior switches to gathering (using a search feature, either provided by the site or an external provider). Searching is not as much fun as gathering, it makes you think about searching (rather than thinking about whatever it is you came to the site to do).

The importance of good search features is obvious during the gathering behavior mode, but the same technology can also have a positive impact on their experience before then, during the hunting mode.

From a user's perspective, a good hunting experience is about serendipity. Bingo! I found what I need, <happy feeling>. From an interface design perspective we typically focus on affordance, making it obvious/intuitive how to find what you need (don't make the user think).

This wisdom is applied to good user-interface design. But there is also such thing as good **undesign**.

Some systems use algorithms to suggest content users based on artificial intelligence (guessing machines), rather than spending time and money argueing about menues and links. If the user-centric design challenge is really hard, for example product catelogue with a very large number of products and no common obvious way to organise them, then the algorithmic techniques can perform much better than a human design process. It's horses for courses, there are other situations where a well designed menu is very effective and the algorithmic techniques are useless. There are also individual differences in how people think about navigation, even an information architecture that most people consider well designed will encounter *impedance mismatch* when some people try to wrap thear heads around it. What's obvious to you is not always obvious to me, and vica-versa.

This kind of algorithmic navigation technology is used extensively in online advertising and e-commerce sites (where it is known as "recommendation engine" functionality, https://en.wikipedia.org/wiki/Recommender_system). The more diverse the users, and the more diverse the content, then the better algorithmic navigation seems to perform (and the harder it is for humans to sucessfully design good information architecture solutions).

At it's heart, a recommendation engine can be framed as a search problem. The links provided by the recommendation engine are effectively the results of a carefully constructed search; "given everything we know about stuff, find higly relevant resources". When it works well, the user expereinces serendipitous links (Ah ha! that's what I'm hunting for). This means they catch a worm and get to feast, avoid a dreary day of scrtaching around in the dirt, and get to spend their time on things they would rather be doing.

In the above context, "stuff" can be the content of the resource being viewed, information about this user, information about user behavior in general, other things we know about the topic of the page. See https://youtube.com/watch?y=13yQbaW2V4Y for a nice presentation about using solr/lucern to implement recommendation engine features. The technical approach with elasticsearch would be equivalent.

Now, focus on our specific problem domain:
 * all the government content
 * all the individuals and businesses
 * every kind of interaction with government

This definitely seems to meet the criteria where algorithmic navigation tends to outperform human design processes. With thousands of individual sites and millions of reources, it's also many orders of magnitude cheaper than continueing to curate, design and maintain bespoke information architectures.

Also unusually in our specfoc problem domain, we are **definitely NOT** in the business of aggregating data on our users and leveraging it for purposes other than those for which it was gathered. That could actually be illegal under the Privacy Act, and it's just not how we roll (see Australian Public Service values and Code Of Conduct). It's would also be highly counterproductuive; the APS is trusted by the Australian public and we should always try to build on that, never erode it.

So, if we use the "collaborative filtering" approach with implicitly collected data, then it must be open data. Appropriate open data does not exist yet (I think - at least I haven't found it yet), however it isn't hard to imagine that aggregate, deindividualised traffic analysis could be published that might be useful. For example, a fusion of customer data sold by ISPs (e.g. HitWise) with traffic based on our own instrumentation (e.g. http://piwik.org/ or Google Analytics). In other words, look at user-behavior (how resources are used together) to analyse the content, but not analyse the users themselves.

A more promising approach seems to be content based filtering, that combines information extracted from public resources with metadata about government services (and possibly legislation).


Analytic insights
-----------------

 * tools for government webmasters
 * expose the evidence-base, open the discussion
 * refactor existing resources to enhance the user-experience
 * double-loop learning and digital darwinism


Dashboards and more open data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dashboard blah blah blah.

this search stuff will generate new data, of course it should be open.


Content Cage-Fight
^^^^^^^^^^^^^^^^^^

 1) publish a techie/how-to blog post: use the haystack API and More Like This (MLT) queries to produce a "semantic footprint" for every item in the service catalogue.
 2) pick out some particularally muddy footprints and (privately) ask, can we do better? do we really need this many pages about the same stuff? are all these pages really related? Are the links between them OK or are we keeping users in the dark? that sort of thing.
 3) Bring the content ownership/authorship graph into the same room, provide cucumber sandwiches and don't let them out until they agree to make it better.


Double-loop learning and digital darwinism
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MuHaHaHaaaa... (TODO: elaborate)
