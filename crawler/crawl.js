"use strict";
var fs = require('fs');
var conf = require('./config/config.js');
var path = require('path');
var nodeURL = require('url');
var Crawler = require("simplecrawler");
var moment = require('moment');



var winston = require('winston');
//TODO: disable winston when debug
//           will have to define my own logger	

var crawlDb = require('./lib/crawldB').connect();

winston.add(winston.transports.File, { filename: conf.get('logFile') }); 

winston.info("CrawlJob Settings: " + JSON.stringify(conf._instance));

var count = {  deferred: 0,
		completed: 0,
		error: 0,
		serverError: 0,
		missing: 0 ,
		notDue: 0 };
	
var crawlJob = new Crawler();
crawlJob.interval = conf.get('interval');
crawlJob.userAgent = "Digital Transformation Office Crawler - Contact Nigel 0418556653 - nigel.o'keefe@pmc.gov.au";
crawlJob.filterByDomain = false;
//TODO: Set concurrency




// STOP JOB AFTER CONFIGURED TIME
winston.info("Job set to Run for " + conf.get('timeToRun') + " seconds (" + conf.get('timeToRun')/60 + " min)" );

setTimeout( function() {
	winston.debug("Time Expired, job stopped");
	crawlJob.stop();
	for (var i = 0; i < crawlJob.queue.length; i++) { 
		crawlDb.addIfMissing(crawlJob.queue[i]);
		count.deferred ++;		
		} //end for
		

		winston.info("Stats: " + JSON.stringify(count));
		setTimeout(function() {
			crawlDb.close();
			process.exit();
		}, 1000);
}, conf.get('timeToRun')*1000); //end settimeout

////////////// SETUP CRAWLER  ///////////////
	//Check for database errors

winston.debug('adding Fetch Conditions');

//Exclude URLS which are not nat gov sites
var stateRegex = "(vic.gov\.au$|nsw\.gov\.au$|qld\.gov\.au$|tas\.gov\.au$|act\.gov\.au$|sa\.gov\.au$|wa\.gov\.au$|nt\.gov\.au$)"
crawlJob.addFetchCondition(function(parsedURL) {
	if (   parsedURL.host.substring(parsedURL.host.length - 7) == ".gov.au"   ) {
			//search will be positive if found, positive
			if (parsedURL.host.search(stateRegex)  < 0 ) {
				return true; //not a state
			}else {
				return false; //state domain
				winston.debug("State Domain Encountered: " + parsedURLhostname ); //a state
			}
		} else {
			return false; //not gov.au
			winston.debug("Non gov.au Domain: " + parsedURLhostname ); //a state
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
		winston.debug("Deferred: " + parsedURL.url);
		count.deferred ++;
		return false;
	} 
	return true;
})

//Is this resource ready for its next fetch
crawlJob.addFetchCondition( function(parsedURL) {
	//fix parsed url format used in simplecrawler
	parsedURL.pathname = parsedURL.path;
	parsedURL.url = nodeURL.format(parsedURL);
	
	crawlDb.checkNextFetchDate(parsedURL.url)
	.then(function(result){
		winston.debug("     Already done: " + parsedURL.url);
		return result;
		count.notDue ++;
	}); //has value
});
	
winston.debug('Adding event handlers');
crawlJob
.on("queueerror", function(errData, urlData){
	winston.error("There was a queue error, Queue Erorr URL/Data: " + JSON.stringify(errData) + JSON.stringify(urlData));
	count.error ++;
})
.on("fetcherror", function(queueItem, response){
	crawlDb.upsert(queueItem);
	winston.info("Url Fetch Error: " + queueItem.url);
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
	winston.info("Url was 404: " + queueItem.url);
	})
.on("fetchtimeout", function(queueItem){
	winston.debug("A fetch timed out");
	crawlDb.upsert(queueItem);
	winston.info("Url Timedout: " + queueItem.url);

	})
.on("fetchclienterror", function(queueItem, errorData){
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	
	crawlDb.upsert(queueItem);
	winston.warn("Url Client Error: "  + queueItem.url);
	count.error++;
})
.on("fetchcomplete", function(queueItem, responseBuffer, response) { 
	queueItem.lastFetchDateTime = moment().format();
	var nextFetch = moment();
	nextFetch.add(conf.get('fetchIncrement'), 'days')
	queueItem.nextFetchDateTime = nextFetch.format();
	queueItem.stateData['@class'] = "webDocumentStateData";
	//winston.debug("DocumentContainer (- Document):" + JSON.stringify(queueItem));
	queueItem.document = responseBuffer.toString('base64');
	crawlDb.upsert(queueItem);
	winston.info("Url Completed: " + queueItem.url);
	count.completed++;
})
.on("discoveryComplete", function() {
	//This is where we can add the resources back to the document
})
.on("complete", function() {
	winston.info("Stats: " + JSON.stringify(count));
	setTimeout(function() {
		crawlDb.close();
		process.exit();
		}, 5000); 
})
.on("queueadd", function(queueItem){
	//winston.debug("Queued - " + queueItem.url);
})
.on("fetchstart", function(queueItem, requestOptions){
	//winston.debug("Fetch Started");
})
.on("crawlstart", function(){
	//winston.debug("Crawler started event did fire");
})
.on("fetchredirect", function(){
	//winston.debug("A fetch redirected");	
});
			
winston.debug('Querying DB for new crawl queue');


crawlDb.newQueueList(conf.get('initQueueSize'), function(results) {
	if (results.length > 0) {			
		winston.info('Initialising queue with  ' + (results.length) + ' items from DB');
		for (var j = 0; j < results.length; j++) {
				var parsedURL = nodeURL.parse(results[j].url);
				if (parsedURL.port == null) {
					parsedURL.port = 80; 
					}
				crawlJob.queue.add(parsedURL.protocol, parsedURL.hostname, parsedURL.port, parsedURL.pathname);	
				//TODO - should set these to automatically pass the domain and ready to fetch tests.
			} 
	} else {
		winston.info("Nothing ready to crawl, exiting");
		crawlDb.close();
		process.exit();
	}
	crawlJob.queue.freeze("theInitialQueue.json", function() {});
	
	crawlJob.start();
	winston.info("Crawler Started");
})
