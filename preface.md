# A New Post

Introduction:
 *

## First iteration

## Second iteration: scan-to-plan, test scaling

The second iteration basically involved scailing up from our minimal test fixture (650 resources) to something more like the size of all federal government web. It involved:
 * A scan-before-you-plan exercise; how big is "all the gov.au web" anyhow? How many domains? how many resources (e.g. web pages)? The answer is almost 2K domains (about 1,500 individual web sites) and the total number of resources is climbing towards 30M.
 * Flush out the issues of operating our proposed architecture at this scale.
 
Unsurprisingly, many things that Just Worked (TM) at 650 resources, dont quite work the same at 100K resources, and other issues cropped up at the scale of 10M resources. Some of these had to be addressed to progress iteration 2, and others were analysed and informally risk assessed for impacts on potential future Alpha product.

### Scailing the DB

We used PostgreSQL in two places:
 * The crawler maintains a large table called "WebDocument" containing all the fetched content, HTTP metadata and scheduling information to drive the crawling behavior.
 * The information extraction pipeline uses various RDBMS tables for staging dat between the crawler and the index.

We started out with out own dockerised postgres node in our personal develpment environments, but it was obvious we were going to need to think about how to manage persistance at the larger scale. Rather than thinking to hard about database administration, we decided to use a cloud-based postgresql service with elastic capacity.

The current workload is approximately:
 * The crawler has been making a steady ~20 queries per second for the last couple of weeks.
 * The information extractor is processing ~100 records/second (it's chasing the crawler, which had a head start)
 * The total RDBMS is currently tilising ~1TB of disk, and keeping a single node fairly warm.

We needed to tune a couple of queries and tweak a few indexes, but so far the cloud DB seems like a good decision.


### Scaling the message queue

We use RabbitMQ to manage distributed workload. The crawler has it's own internal message queue (in node.js), so that won't scale-out horizontally in it's current form.

After the crawler fetches content, there is a pipeline of jobs to move and process data from the WebDocument table, through processing steps and into the search index. These are run as asynchronous python/celery tasks, which could theoretically be run as an arbitrarially large number of parallel tasks. In reality there are bottlenecks (such as DB connections) which would require engineering solutions to scale (such as connection pools, sharding/replication, etc), but we haven't done anytihng like that yet.

We started out with a cloud-based rabbitmq service, but actually switched back to a self-hosted message queue as a quick and dirty solution to latency and throughput issues. Nothing that couldn't be solved with tuning and talking to the vendor, but as a proof of concept exercise we didn't invest any time on that.

Currently the message queue is running on a small dedicated virtual machine, with a high watermark of ~50K messages, throughput of about 200 messages/second. There is plenty of headroom on CPU, RAM and disk.
