# A New Post

Introduction:
 *

## First iteration

## Second iteration: scan-to-plan, test scaling

The second iteration basically involved scailing up from our minimal test fixture (650 resources) to something more like the size of all federal government web. It involved:
 * A scan-before-you-plan exercise; how big is "all the gov.au web" anyhow? How many domains? how many resources (e.g. web pages)? The answer is almost 2K domains (about 1,500 individual web sites) and the total number of resources is climbing towards 30M.
 * Flush out the issues of operating our proposed architecture at this scale.
 
Unsurprisingly, many things that Just Worked (TM) at 650 resources dont quite work the same at 100K resources, and other issues cropped up at the scale of 10M resources. Some of these had to be addressed to progress iteration 2, and others were analysed and informally risk assessed for impacts on potential future Alpha product.


### Scailing the DB

We used PostgreSQL in two places:
 * The crawler maintains a large table called "WebDocument" containing all the fetched content, HTTP metadata and scheduling information to drive the crawling behavior.
 * The information extraction pipeline uses various RDBMS tables for staging data between the crawler and the index.

We started out with out own dockerised postgres node in a dev environment, but it was obvious we were going to do something different for persistance at the larger scale. Rather than thinking to hard about database administration, we decided to use a cloud-based postgresql service with elastic capacity.

The current DB workload is approximately:
 * The crawler has been making a steady 10-20 queries per second for the last couple of weeks.
 * The information extractor is processing ~100 records/second (it's chasing the crawler, which had a head start)
 * The total RDBMS is currently utilising ~1TB of disk, and keeping a single node fairly warm.

We needed to tune a couple of queries and tweak a few indexes, but so far the cloud DB seems like a good decision. One notable gotcha was the performance of count(*) queries, which plummeted at some point (>5M records?) when the query planner decided to start doing full table scans rather than using the index. Instead of fixing that (indexing? replication? hints?), we just rewrote the offending queries so they didn't do that.

We are unlikely to need an order of magnitude increase in DB workload, and there's plenty of room for optimisation. The DB layer seems low risk.


### Parallel distributed workload

We use an AMQP queue (RabbitMQ) to manage most of our distributed workload. The crawler keeps it's own internal  queue (node.js, in-memory), so that won't scale-out horizontally in it's current form. This was considered low risk because it's already in the ballpark of expected workload, and we haven't broken it into parallel units yet (e.g. each with a limited range of sites).

After the crawler fetches content, there is a pipeline of jobs to move and process data from the WebDocument table, through processing steps and into the search index. The current information extraction task is a very basic stub (extract article of plain text from HTML pages using the "Goose" pytohn library), but would presumably become more intensive with growing sophistocation (article extraction from PDF and other formats, language processing, clustering analysis, etc). For this reason, this workload was designed from the outset to be handled as parallel distributed tasks (using the celery framework).

This could theoretically be run on an arbitrarially large number parallel compute nodes, but in reality we are currently close to some bottlenecks (such as DB connections) which would require more engineering to work around (connection pools, sharding/replication strategies, etc). We haven't done anytihng like that yet. It's already within cooee of the required scale, so if it's working correctly at this scale then winding it up further does not seem to repsent a lot of technical risk. 

We started out with a cloud-based rabbitmq service, but actually switched back to a self-hosted message queue as a quick and dirty solution to some latency and throughput issues. Nothing that couldn't be solved with tuning and talking to the vendor, but as a proof of concept exercise we didn't invest any time on that.

Currently the message queue is running on a very small virtual machine, with a typical high-watermark of ~50K messages, and throughput of about 200 messages/second. There is plenty of headroom on CPU, RAM and disk. All messages are going through the same queue; sometimes they are nicely shuffled but other times we get a bit of a thundering herd; breaking it up into separate exchanges give us a lot more scope for tuning and optimisation.


### Scaling the search index

With the small test fixtures, the entire search index could be dropped and recreated in the blink of an eye. With 100K resources, the same drop/create is impractically slow. One reason for this is the totally untuned elasticsearch cluster (single node, 5 shards) which is obviously not right for the task. Elasticsearch is designed to be scaled out in wide flat clusters, so the drop/reacreate performance is not surprising or much of a concern. 

The typical use-case would be heavy on query performance, with a constant trickle ot insert/delete and update (maybe 5/s, going as high as 100/s at peak). Even with our totally untuned index, we are getting satisfactory query performance with about 5 inserts/updates per second.

The biggest issue is the latency of inserts; Our ~5 inserts per second performance requires a pool of 70 worker threads, which seems high but is due to the fact we have 2-10 seconds latency on inserts. This is not too much of a concern, it seems likely that the problem should yield to index cluster tuning, but something to watch. If we have to run a much larger number of worker threads to increase our throughput, we will need to separate the message queues and use dedicated worker node types, otherwise we will have problems with a thundering herd of processes occasionally swamping the other bottlenecks in the system (etc).

The one thing we haven't tried to scale up yet is the query load. Due to the way elasticsearch/lucerne works this doesn't seem to be much of a risk. We would probably want to outsourcing that sort of workload to some sort of cloud provider anyhow. Until we have built up a full size index in our dev environmant, we don't actually know how to size or cost that yet.

Without further development, the current system will probably take another month or so for the crawler to finish scanning all of .gov.au, and then for the index to catch up. So it's wait and see for now.


## Next steps

AS mentioned in the introduction we are in discovery phase which is primarially about understanding user needs. Validating architectural assumptions and assessing technical risks is an important but secondary activity. Our main focus is on gathering information, not delivering working software (yet).

Having said that our pre-alpha, proof of concept code is open source and available to anyone who wants it. We are using GitHub for publishing and manageing issues. There's even some documentation, but set your expectations appropriately (it's far from ready to shrink-wrap!). Here are the links:

 * ...

Please feel free to raise tickets if you have issues or want support with the code or docs, and pull requests are of course welcome! 

The DTO product team is focussed on understanding user needs, improving access to government services and delivering a great user experience. We also understand that sharing our code and data might benefit society in unexpected ways, so please raise a ticket if you are interested in access to the data we collecting. We'd be delighted to hear from anyone who needs "all the Australian Government" search index, directly or through an API, or any other use-case for this stuff that we might be able to help you with.

Private messages are fine, a ticket will likely be noticed sooner :)




