"use strict";
var Crawler = require("simplecrawler");
var fs = require('fs');
var path = require('path');
var nodeURL = require('url');
var moment = require('moment');
var crawlDb = require('./crawldB').connect();
var console = require('console');

//TODO: Move to params
var stateRegex = "(vic.gov\.au$|nsw\.gov\.au$|qld\.gov\.au$|tas\.gov\.au$|act\.gov\.au$|sa\.gov\.au$|wa\.gov\.au$|nt\.gov\.au$)"^M


domain = immi.gov.au


var crawlJob = new Crawler("*******THE GOOGLE SEARCH************");


////////////// SETUP CRAWLER  ///////////////
	//Check for database errors
	//TODO: Extract settings to a config file
	crawlJob.interval = interval;
	crawlJob.userAgent = "DTO Testing Crawler - Contact Nigel 0418556653";
	crawlJob.filterByDomain = false;
	console.debug('adding Fetch Conditions');



	//only non state gov.au domains AND google
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
        if(  parsedURL.host = "www.google.com.au"
             && parsedURL.path.search("num=100") >= 0
             && parsedURL.path.search("q=filetype%3Apdf+site") >= 0   ) {
          return true;
        }
        return false; //not gov.au or google search
				console.debug("Non gov.au Domain: " + parsedURLhostname ); //a state
      }
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





	crawlJob.start();
	console.info("Crawler Started");
})
