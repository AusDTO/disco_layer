"use strict";
var Crawler = require("simplecrawler");
var fs = require('fs');
var path = require('path');
var nodeURL = require('url');
var moment = require('moment');
var crawlDb = require('./crawldB').connect();


////// Run Setttings

//TODO: Move to params
var debug = true;
var initQueueSize = 100;   //get this many from the database to kick the job off.
var maxItems = 1000;  //Stop the job after this many fetches.
var timeToRun =  240;		//Stop the job after this many seconds
var fetchIncrement = 7;	//Days to wait for next fetch
var count = {
		deferred: 0,
		completed: 0,
		error: 0,
		serverError: 0,
		missing: 0 ,
		notDue: 0
	};

var stateRegex = "(vic.gov\.au$|nsw\.gov\.au$|qld\.gov\.au$|tas\.gov\.au$|act\.gov\.au$|sa\.gov\.au$|wa\.gov\.au$|nt\.gov\.au$)"
	
var crawlJob = new Crawler("www.humanservices.gov.au");

//Console Stuffs 
//This sucks, why am I having to do the prefixing, there should be a module for this somewhere.
console.error = function(line) {
	console.log("ERROR::" + line);
}

console.warn = function(line) {
	console.log("WARN ::" + line);
}
console.info = function(line) {
	console.log("INFO ::" + line);
}
console.debug = function(line) {
	if (debug) { 
		console.log("DEBUG::" + line)
		};
}

////////////// STOP JOB AFTER CONFIGURED TIME ///////////////
console.info("Job set to Run for " + timeToRun + " seconds");
setTimeout( function() {
	console.debug("Time Expired, job stopped");
	crawlJob.stop();
	for (var i = 0; i < crawlJob.queue.length; i++) { 
		crawlDb.addIfMissing(crawlJob.queue[i]);
		count.deferred ++;		
		} //end for
		
		console.info("Stats: " + JSON.stringify(count));
		
		
				
		setTimeout(function() {
			crawlDb.close();
			process.exit();
		}, 1000);
}, timeToRun*1000); //end settimeout



////////////// SETUP CRAWLER  ///////////////
	//Check for database errors
	//TODO: Extract settings to a config file				
	crawlJob.interval = 3000;
	crawlJob.userAgent = "DTO Testing Crawler - Contact Nigel 0418556653";
	crawlJob.filterByDomain = false;
	
	console.debug('adding Fetch Conditions');

	
	
	////TODO: Testing: I think the crawler is not applying the fetch conditions to the initial url
	//only non state gov.au domains
	crawlJob.addFetchCondition(function(parsedURL) {
		if (   parsedURL.host.substring(parsedURL.host.length - 7) == ".gov.au"   ) {
				//search will be positive if found, positive
				if (parsedURL.host.search(stateRegex)  < 0 ) {
					return true; //not a state
				}else {
					return false; //state domain
					console.debug("State Domain Encountered: " + parsedURLhostname ); //a state
				}
			} else {
				return false; //not gov.au
				console.debug("Non gov.au Domain: " + parsedURLhostname ); //a state
			} 
		});

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
			console.debug("Deferred: " + parsedURL.url);
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
			console.debug("     Already done: " + parsedURL.url);
			return result;
			count.notDue ++;
		}); //has value
	});
		
	console.debug('Adding event handlers');
	crawlJob
		.on("queueerror", function(errData, urlData){
			console.error("There was a queue error, Queue Erorr URL/Data: " + JSON.stringify(errData) + JSON.stringify(urlData));
			count.error ++;
		})
		.on("fetcherror", function(queueItem, response){
			crawlDb.upsert(queueItem);
			console.info("Url Fetch Error: " + queueItem.url);
			count.serverError++;
		})
		.on("fetch404", function(queueItem, response){
			queueItem.lastFetchDateTime = moment().format();
			var nextFetch = moment();
			nextFetch.add(7, 'days')
			queueItem.nextFetchDateTime = nextFetch.format();
			queueItem.stateData['@class'] = "webDocumentStateData";
			crawlDb.upsert(queueItem);
			count.missing++;
			console.info("Url was 404: " + queueItem.url);
			})
		.on("fetchtimeout", function(queueItem){
			console.debug("A fetch timed out");
			crawlDb.upsert(queueItem);
			console.info("Url Timedout: " + queueItem.url);

			})
		.on("fetchclienterror", function(queueItem, errorData){
			//console.debug("Fetch Client Error Item: " + JSON.stringify(queueItem));
			//console.debug("Error Client Error Data: " + JSON.stringify(errorData));
			queueItem.lastFetchDateTime = moment().format();
			var nextFetch = moment();
			nextFetch.add(7, 'days')
			queueItem.nextFetchDateTime = nextFetch.format();
			queueItem.stateData['@class'] = "webDocumentStateData";
			
			crawlDb.upsert(queueItem);
			console.warn("Url Client Error: "  + queueItem.url);
			count.error++;
		})
		.on("fetchcomplete", function(queueItem, responseBuffer, response) { 
			queueItem.lastFetchDateTime = moment().format();
			var nextFetch = moment();
			nextFetch.add(7, 'days')
			queueItem.nextFetchDateTime = nextFetch.format();
			queueItem.stateData['@class'] = "webDocumentStateData";
			//console.debug("DocumentContainer (- Document):" + JSON.stringify(queueItem));
			queueItem.document = responseBuffer.toString('base64');
			crawlDb.upsert(queueItem);
			delete queueItem.document;
			console.info("Url Completed: " + queueItem.url);
			count.completed++;
		})
		.on("discoveryComplete", function() {
			//This is where we can add the resources back to the document
		})
		.on("complete", function() {
			console.info("Stats: " + JSON.stringify(count));
			setTimeout(function() {
				crawlDb.close();
				process.exit();
				}, 5000); 
		})
		.on("queueadd", function(queueItem){
			//console.debug("Queued - " + queueItem.url);
		})
		.on("fetchstart", function(queueItem, requestOptions){
			//console.debug("Fetch Started");
		})
		.on("crawlstart", function(){
			//console.debug("Crawler started event did fire");
		})
		.on("fetchredirect", function(){
			//console.debug("A fetch redirected");	
		});
			
console.debug('Querying DB for new crawl queue');
crawlDb.newQueueList(initQueueSize, function(results) {
	if (results.length > 0) {			
		console.info('Initialising queue with  ' + (results.length) + ' items from DB');
		for (var j = 0; j < results.length; j++) {
				var parsedURL = nodeURL.parse(results[j].url);
				if (parsedURL.port == null) {
					parsedURL.port = 80; 
					}
				crawlJob.queue.add(parsedURL.protocol, parsedURL.hostname, parsedURL.port, parsedURL.pathname);	
				//TODO - should set these to automatically pass the domain and ready to fetch tests.
			} 
	} else {
		console.info("Nothing ready to crawl, exiting");
		crawlDb.close();
		process.exit();
	}
	crawlJob.queue.freeze("theInitialQueue.json", function() {});
	
	crawlJob.start();
	console.info("Crawler Started");
})
