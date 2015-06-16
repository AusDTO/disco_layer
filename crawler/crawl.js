"use strict";
var fs = require('fs');
var conf = require('./config/config.js');
var path = require('path');
var nodeURL = require('url');
var Crawler = require("simplecrawler");
var moment = require('moment');
var logger=require('./config/logger.js'); 
var crawlDb = require('./lib/crawlDb').connect();

//this is a seperate logger for some local debugging
var log2 = new winston.Logger({
  transports: [
    new winston.transports.File({ filename: './logs/log2.log', level: 'debug'})
  ],
  exitOnError: false
});




logger.info("CrawlJob Settings: " + JSON.stringify(conf._instance));

var count = {  deferred: 0,
		completed: 0,
		error: 0,
		serverError: 0,
		redirect: 0,
		missing: 0};
	
var crawlJob = new Crawler();
crawlJob.interval = conf.get('interval');
crawlJob.userAgent = "Digital Transformation Office Crawler - Contact Nigel 0418556653 - nigel.o'keefe@pmc.gov.au";
crawlJob.filterByDomain = false;
crawlJob.maxConcurrency =conf.get('concurrency');


// STOP JOB AFTER CONFIGURED TIME
logger.info("Job set to Run for " + conf.get('timeToRun') + " seconds (" + conf.get('timeToRun')/60 + " min) or a maximum of " + conf.get('maxItems')+ " items" );


setTimeout( function() {
	logger.debug("Time Expired, job stopped");
	crawlJob.stop();
	for (var i = 0; i < crawlJob.queue.length; i++) { 
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
var stateRegex = "(\.vic\.gov\.au$|\.nsw\.gov\.au$|\.qld\.gov\.au$|\.tas\.gov\.au$|\.act\.gov\.au$|\.sa\.gov\.au$|\.wa\.gov\.au$|\.nt\.gov\.au$)"
crawlJob.addFetchCondition(function(parsedURL) {

	if (   parsedURL.host.substring(parsedURL.host.length - 7) == ".gov.au"   ) {
			//search will be positive if found, positive
			if (parsedURL.host.search(stateRegex)  < 0 ) {
				return true; //not a state
			}else {
				logger.debug("State Domain Encountered: " + parsedURL.host ); //a state
				return false; //state domain
			
			}
		} else {
			logger.debug("Non gov.au Domain: " + parsedURL.host ); //non gov au
			return false; //not gov.au
		} 
	});


var maxItems = conf.get('maxItems');  
crawlJob.addFetchCondition( function(parsedURL) {
//TODO: Works with queue length, that is not right. Only fetch queue length counts.
//fetchedQueueLength=crawlJob.queue.length
if (crawlJob.queue.length >= maxItems) {
	//TODO: fix making copy of parsedURL
	delete parsedURL.uriPath;
	parsedURL.pathname = parsedURL.path;
	var queueItem = parsedURL;
	queueItem.url = nodeURL.format(parsedURL);
	crawlDb.addIfMissing(queueItem);
	logger.info("URL Deferred: " + queueItem.url );
	count.deferred ++;
	return false;
} else { 
	logger.debug("URL NOT Deferred: " + parsedURL.host + parsedURL.path );
	return true;
	}
});
//VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
//TODO: IT IS BEING OVERLY ENTHUSIASTIC ABOUT PREVENTING NEW URLS FROM BEING QUEUED
//ERROR
// This is becuase of my async code having to come back to sync code. Not sure where to go from here 
// becuase the most appropriate thing to do would be to make it async, but that would mean modifying the 
// simple crawler code 

// it is probably not a major issue to wait until a bit later to resolve this issue beucase it *should* only result in a
// small overselection due to the face that it only impacts the urls which are crawled and they should either be close to ready
// because an attempt to crawl them would have happened when i did this page last time or it is new anyhow.
//
//OR I could add an additional mechnism to simple crawler that works with async


//Is this resource ready for its next fetch
/*
crawlJob.addFetchCondition( function(parsedURL) {
	//fix parsed url format used in simplecrawler
	parsedURL.pathname = parsedURL.path;
	parsedURL.url = nodeURL.format(parsedURL);
	var ruleResult 
	crawlDb.checkNextFetchDate(parsedURL.url)
	.then(function(result){
		log2.debug('checkNextFetchDate outcome for: ' + parsedURL.url + " was: " + result )
		//logger.debug(parsedURL.url + " Result = " + result);
		if(!result) { 
			logger.info("Already done: " + parsedURL.url + " Result = " + result);
			count.notDue ++;
		}
		ruleResult = result;
//return true;  //TODO: THIS IS JUST FOR TESTING
	}); //has value
	logger.debug('fetchReady result: ' + ruleResult);
	return ruleResult;

});
*/
//END ERROR
//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA


//crawlJob.queue.add('http', 'www.activfire.gov.au', '80', '/');	
				
//TODO: Fetch errors, log status code for easier followup.

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
	logger.debug("A fetch timed out");
	crawlDb.upsert(queueItem);
	logger.info("Url Timedout: " + queueItem.url);
	})
.on("fetchclienterror", function(queueItem, errorData){
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
	logger.info("Url Completed: " + queueItem.url);
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
	logger.info("Url Redirect (" + queueItem.stateData.code + "): " + queueItem.url +
		" To: " + parsedURL.host + parsedURL.path);
		
	//TODO: Need to apply url checks, simple crawler does not refer 696 in crawler.js in simplecrawler 
	//           module for map reduce way of working it.
	
/* - the code to check the url meets my fetch conditions, stolen from simple crawler
// Pass this URL past fetch conditions to ensure the user thinks it's valid
	var fetchDenied = false;
	fetchDenied = crawler._fetchConditions.reduce(function(prev,callback) {  
		return prev || !callback(parsedURL);
	},false);

	if (fetchDenied) {
		// Fetch Conditions conspired to block URL
		return false;
	}
*/


	crawlJob.queue.add(parsedURL.protocol, parsedURL.host, parsedURL.port, parsedURL.path);	
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	crawlDb.upsert(queueItem);
	//TODO: Not queuing redirects
	count.redirect++;	
});
			
logger.debug('Querying DB for new crawl queue');

crawlDb.newQueueList(conf.get('initQueueSize'), function(results) {
	if (results.length > 0) {			
		logger.info('Initialising queue with  ' + (results.length) + ' items from DB');
		for (var j = 0; j < results.length; j++) {
				var parsedURL = nodeURL.parse(results[j].url);
				if (parsedURL.port == null) {
					parsedURL.port = 80; 
					}
				crawlJob.queue.add(parsedURL.protocol, parsedURL.hostname, parsedURL.port, parsedURL.pathname);	
				//TODO - should set these to automatically pass the domain and ready to fetch tests.
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
