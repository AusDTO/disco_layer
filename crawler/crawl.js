"use strict";
var fs = require('fs');
var conf = require('./config/config');
var path = require('path');
var nodeURL = require('url');
var Crawler = require("simplecrawler");
var moment = require('moment');
var logger = require('./config/logger');
var util = require('./lib/buildWebDocument');

var crawlDb = require('./lib/ormCrawlDb')





debugger;
logger.info("CrawlJob Settings: " + JSON.stringify(conf._instance));

var count = {
    deferred: 0,
    completed: 0,
    error: 0,
    serverError: 0,
    redirect: 0,
    missing: 0
};

var crawlJob = new Crawler();


//Override the queueURL method becuase the existing one does not easily support in the fetchConditions.


crawlJob.interval = conf.get('interval');
crawlJob.userAgent = "Digital Transformation Office Crawler - Contact Nigel 0418556653 - nigel.o'keefe@pmc.gov.au";
crawlJob.filterByDomain = false;
crawlJob.maxConcurrency = conf.get('concurrency');
crawlJob.timeout = 20000; //ms


crawlJob.baseQueueURL = crawlJob.queueURL;
crawlJob.queueURL = require('./lib/queueURL');

// STOP JOB AFTER CONFIGURED TIME
logger.info("Job set to Run for " + conf.get('timeToRun') + " seconds (" + conf.get('timeToRun') / 60 + " min) or a maximum of " + conf.get('maxItems') + " items");


setTimeout(function() {
    logger.debug("Time Expired, job stopped");
    crawlJob.stop();
    for (var i = 0; i < crawlJob.queue.length; i++) {
        crawlJob.queue[i].status = 'deferred';
        crawlDb.addIfMissing(crawlJob.queue[i]);
        count.deferred++;
    } //end for


    logger.info("Stats: " + JSON.stringify(count));
    setTimeout(function() {
        //crawlDb.close();
        //process.exit();
    }, 1000);
}, conf.get('timeToRun') * 1000); //end settimeout

////////////// SETUP CRAWLER  ///////////////
//Check for database errors

logger.debug('adding Fetch Conditions');
//Exclude URLS which are not nat gov sites


var stateRegex = /(^|\.)vic\.gov\.au$|(^|\.)nsw\.gov\.au$|(^|\.)qld\.gov\.au$|(^|\.)tas\.gov\.au$|(^|\.)act\.gov\.au$|(^|\.)sa\.gov\.au$|(^|\.)wa\.gov\.au$|(^|\.)nt\.gov\.au$/;
crawlJob.addFetchCondition(function(parsedURL) {

    if (parsedURL.host.substring(parsedURL.host.length - 7) == ".gov.au") {
        //search will be positive if found, positive
        if (parsedURL.host.search(stateRegex) < 0) {
            return true; //not a state
        } else {
            logger.info("State Domain Encountered: " + parsedURL.host); //a state
            return false; //state domain

        }
    } else {
        logger.debug("Non gov.au Domain: " + parsedURL.host); //non gov au
        return false; //not gov.au
    }
});

//NOTE: This should only be used for testing purposes. It is not accurate becuase it doesnt account for fetched/unfetched
var maxItems = conf.get('maxItems');

if (maxItems > 0) {
    logger.info("Adding maxItems to process rule");
    crawlJob.addFetchCondition(function(parsedURL) {
        if (crawlJob.queue.length >= maxItems) {
            delete parsedURL.uriPath;
            parsedURL.pathname = parsedURL.path;
            var queueItem = parsedURL;
            queueItem.url = nodeURL.format(parsedURL);
            queueItem.status = 'deferred';
            crawlDb.addIfMissing(queueItem);
            logger.info("URL Deferred (q=" + crawlJob.queue.length + "): " + queueItem.url);
            count.deferred++;
            return false;
        } else {
            return true;
        }
    });
}


crawlDb.connect()
    .then(function(crawlDb) {

        logger.debug('Adding event handlers');
        crawlJob
            .on("queueerror", function(errData, urlData) {
                logger.error("There was a queue error, Queue Erorr URL/Data: " + JSON.stringify(errData) + JSON.stringify(urlData));
                count.error++;
            })
            .on("fetcherror", function(queueItem, response) {
                crawlDb.upsert(util.buildWebDocument(queueItem))
                    .then(function() {
                        logger.info("Url Fetch Error (" + queueItem.stateData.code + "): " + queueItem.url);
                        count.serverError++;
                    });
            })
            .on("fetch404", function(queueItem, response) {
                crawlDb.upsert(util.buildWebDocument(queueItem))
                    .then(function() {
                        logger.info("Url was 404: " + queueItem.url);
                        count.missing++;
                    });
            })
            .on("fetchtimeout", function(queueItem) {
                crawlDb.upsert(util.buildWebDocument(queueItem))
                    .then(function() {
                        logger.info("Url Timedout(" + queueItem.stateData.code + "): " + queueItem.url);
                    });
            })
            .on("fetchclienterror", function(queueItem, errorData) {
                logger.debug("queueItem:" + JSON.stringify(queueItem));


                crawlDb.upsert(util.buildWebDocument(queueItem))
                    .then(function() {
                        logger.info("Url Fetch Client Error (" + queueItem.stateData.code + "): " + queueItem.url);
                        count.error++;
                    });
            })
            .on("fetchcomplete", function(queueItem, responseBuffer, response) {
                queueItem.document = responseBuffer;
                crawlDb.upsert(util.buildWebDocument(queueItem))
                    .then(function() {
                        logger.info("Url Completed(" + queueItem.stateData.code + "): " + queueItem.url);
                        count.completed++;
                    });
            })
            .on("discoveryComplete", function(queueItem, resources) {
                //Note: This occurs after fetchcomplete so resources are already gone before we can add them to database.
                //The way to do it would be to move the storage from fetch complete to here.
            })
            .on("complete", function() {
                logger.info("Stats: " + JSON.stringify(count));
                setTimeout(function() {
                    //crawlDb.close();
                    process.exit();
                }, 5000);
            })
            .on("queueadd", function(queueItem) {
                logger.debug("Queued - " + queueItem.url);
            })
            .on("fetchstart", function(queueItem, requestOptions) {
                logger.debug("URL Fetch Started " + queueItem.url);
            })
            .on("fetchheaders", function(queueItem, responseObject) {
                logger.debug("Fetching Headers: " + queueItem.url);
                logger.debug("Headers Response: " + responseObject.toString());
            })
            .on("fetchdataerror", function(queueItem, response) {
                logger.debug("Fetching Data Error: " + queueItem.url);
            })
            .on("crawlstart", function() {
                logger.debug("Crawler started event did fire");
            })
            .on("fetchredirect", function(queueItem, parsedURL, response) {
                crawlJob.queueURL(nodeURL.format(parsedURL));

                crawlDb.upsert(util.buildWebDocument(queueItem))
                    .then(function() {
                        count.redirect++;
                        logger.info("Url Redirect (" + queueItem.stateData.code + "): " + queueItem.url +
                            " To: " + nodeURL.format(parsedURL));
                    });
            });

        logger.debug('Querying DB for new crawl queue');


        crawlDb.newQueueList(conf.get('initQueueSize'))
            .then(function(results) {
                if (results.length > 0) {
                    logger.info('Initialising queue with  ' + results.length + ' items from DB');
                    results.forEach(function(item) {
                        crawlJob.queueURL(item.url);
                    });
                } else {
                    logger.info("Nothing ready to crawl, exiting");
                    //    crawlDb.close();
                    process.exit();
                }
                //crawlJob.queue.freeze("theInitialQueue.json", function() {});
                setTimeout(function() {
                    crawlJob.start();
                    logger.info('crawler started');
                }, 2000);
            });

    }); //connect then
