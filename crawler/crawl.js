"use strict";
var fs = require('fs');
var conf = require('./config/config.js');
var path = require('path');
var nodeURL = require('url');
var Crawler = require("simplecrawler");
var moment = require('moment');
var logger=require('./config/logger.js'); 


var crawlDb = require('./lib/crawlDb').connect();


logger.info("CrawlJob Settings: " + JSON.stringify(conf._instance));

var count = {  deferred: 0,
		completed: 0,
		error: 0,
		serverError: 0,
		redirect: 0,
		missing: 0};
	
var crawlJob = new Crawler();

//Override the queueURL method becuase the existing one does not easily support in the fetchConditions.


crawlJob.interval = conf.get('interval');
crawlJob.userAgent = "Digital Transformation Office Crawler - Contact Nigel 0418556653 - nigel.o'keefe@pmc.gov.au";
crawlJob.filterByDomain = false;
crawlJob.maxConcurrency =conf.get('concurrency');
crawlJob.timeout = 10000; //ms


crawlJob.baseQueueURL = crawlJob.queueURL;
crawlJob.queueURL = require('./lib/queueURL');
 
// STOP JOB AFTER CONFIGURED TIME
logger.info("Job set to Run for " + conf.get('timeToRun') + " seconds (" + conf.get('timeToRun')/60 + " min) or a maximum of " + conf.get('maxItems')+ " items" );


setTimeout( function() {
	logger.debug("Time Expired, job stopped");
	crawlJob.stop();
	for (var i = 0; i < crawlJob.queue.length; i++) { 
		crawlJob.queue[i].status = 'deferred';
		crawlDb.addIfMissing(crawlJob.queue[i]);
		count.deferred ++;		
		} //end for
		

		logger.info("Stats: " + JSON.stringify(count));
		setTimeout(function() {
			crawlDb.close();
			process.exit();
		}, 1000);
}, conf.get('timeToRun')*1000); //end settimeout

////////////// SETUP CRAWLER  ///////////////
	//Check for database errors

logger.debug('adding Fetch Conditions');
//Exclude URLS which are not nat gov sites

//TODO: is currently excluding [somthing]sa.gov.au  e.g. csa.gov.au

var stateRegex = "(\.vic\.gov\.au$|\.nsw\.gov\.au$|\.qld\.gov\.au$|\.tas\.gov\.au$|\.act\.gov\.au$|\.sa\.gov\.au$|\.wa\.gov\.au$|\.nt\.gov\.au$)"
crawlJob.addFetchCondition(function(parsedURL) {

	if (   parsedURL.host.substring(parsedURL.host.length - 7) == ".gov.au"   ) {
			//search will be positive if found, positive
			if (parsedURL.host.search(stateRegex)  < 0 ) {
				return true; //not a state
			}else {
				logger.info("State Domain Encountered: " + parsedURL.host ); //a state
				return false; //state domain
			
			}
		} else {
			logger.debug("Non gov.au Domain: " + parsedURL.host ); //non gov au
			return false; //not gov.au
		} 
	});

//NOTE: This should only be used for testing purposes. It is not accurate becuase it doesnt account for fetched/unfetched
var maxItems = conf.get('maxItems');

if(maxItems > 0 ) {  
	logger.info("Adding maxItems to process rule")
	crawlJob.addFetchCondition( function(parsedURL) {
	if (crawlJob.queue.length >= maxItems) {
		delete parsedURL.uriPath;
		parsedURL.pathname = parsedURL.path;
		var queueItem = parsedURL;
		queueItem.url = nodeURL.format(parsedURL);
		queueItem.status = 'deferred';
		crawlDb.addIfMissing(queueItem);
		logger.info("URL Deferred (q="  + crawlJob.queue.length + "): " + queueItem.url );
		count.deferred ++;
		return false;
	} else { 
		return true;
		}
	});
}				

logger.debug('Adding event handlers');
crawlJob
.on("queueerror", function(errData, urlData){
	logger.error("There was a queue error, Queue Erorr URL/Data: " + JSON.stringify(errData) + JSON.stringify(urlData));
	count.error ++;
})
.on("fetcherror", function(queueItem, response){
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	crawlDb.upsert(queueItem);
	logger.info("Url Fetch Error (" + queueItem.stateData.code + "): " + queueItem.url);
	count.serverError++;
})
.on("fetch404", function(queueItem, response){
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	crawlDb.upsert(queueItem);
	count.missing++;
	logger.info("Url was 404: " + queueItem.url);
	})
.on("fetchtimeout", function(queueItem){
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	crawlDb.upsert(queueItem);
	logger.info("Url Timedout(" + queueItem.stateData.code + "): " + queueItem.url);
	})
.on("fetchclienterror", function(queueItem, errorData){
	logger.debug("queueItem:" + JSON.stringify(queueItem));

	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	
	crawlDb.upsert(queueItem);
	logger.info("Url Fetch Client Error (" + queueItem.stateData.code + "): " + queueItem.url);
	count.error++;
})
.on("fetchcomplete", function(queueItem, responseBuffer, response) { 
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	//logger.debug("DocumentContainer (- Document):" + JSON.stringify(queueItem));
	queueItem.document = responseBuffer.toString('base64');
	crawlDb.upsert(queueItem);
	
	logger.info("Url Completed(" + queueItem.stateData.code + "): " + queueItem.url);
	count.completed++;
})
.on("discoveryComplete", function() {
	//This is where we can add the resources back to the document
})
.on("complete", function() {
	logger.info("Stats: " + JSON.stringify(count));
	setTimeout(function() {
		crawlDb.close();
		process.exit();
		}, 5000); 
})
.on("queueadd", function(queueItem){
	logger.debug("Queued - " + queueItem.url);
})
.on("fetchstart", function(queueItem, requestOptions){
	logger.debug("URL Fetch Started " +  queueItem.url);
})
.on("crawlstart", function(){
	logger.debug("Crawler started event did fire");
})
.on("fetchredirect", function( queueItem, parsedURL, response ){
	crawlJob.queueURL(nodeURL.format(parsedURL));	

	logger.info("Url Redirect (" + queueItem.stateData.code + "): " + queueItem.url +
		" To: " + nodeURL.format(parsedURL));
	//Queue the redirect location
	queueItem.lastFetchDateTime = moment().format();

	//store the outcome for the source
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	crawlDb.upsert(queueItem);
	count.redirect++;	
});
			
logger.debug('Querying DB for new crawl queue');



crawlDb.newQueueList(conf.get('initQueueSize'), function(results) {
	if (results.length > 0) {
		logger.info('Initialising queue with  ' + results.length + ' items from DB');

		for (var j = 0; j < results.length; j++) {
			crawlJob.queueURL(results[j].url);	
			logger.debug("Adding: " + results[j].url);
		}
	} else {	
		logger.info("Nothing ready to crawl, exiting");
		crawlDb.close();
		process.exit();
	}
	//crawlJob.queue.freeze("theInitialQueue.json", function() {});
	crawlJob.start();
	logger.info("Crawler Started");
})
