Oriento = require('oriento');
Crawler = require("simplecrawler");
fs = require('fs');
path = require('path');
nodeURL = require('url');
moment = require('moment');

////// Run Setttings

//TODO: Move to params
debug = true;
maxItems = 9999;
timeToRun =  600;		//in seconds
fetchIncrement = 1;	//Days to wait for next fetch
count = {
		deferred: 0,
		completed: 0,
		error: 0,
		serverError: 0,
		missing: 0 ,
		notDue: 0,
	};

dateFormat = "YYYY-MM-DD HH:mm:ss";

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



/////////////// FUNCTION TO ADD QUEUE ITEM ///////////////
//TODO: Consider if this should become a DAO
function addIfMissing(queueItem) { 
	//TODO: Check statedata is missing before nulling
	queueItem.stateData = null;
//	console.debug("Trying to freeze: " + JSON.stringify(queueItem.url));
		db.query('select count(*) as count from webDocumentContainer where url=:url', {params: { url: queueItem.url}})
		.then(function (result){
			if (result[0].count == 0) {
				//console.debug("Url needs to be stored: " + queueItem.url);
				//TODO: change back to query builder and scalar
				db.query("INSERT INTO webDocumentContainer content " + JSON.stringify(queueItem));
			} else { 
//				console.debug("Ignoring: " + queueItem.url + ' ||| ' + JSON.stringify(queueItem)); 
			}
		}); //end select then
	}

	/////////////// STOP JOB AFTER CONFIGURED TIME ///////////////
	console.info("Job set to Run for " + timeToRun + " seconds");
	setTimeout( function() {
		crawlJob.stop();
		console.debug("Time Expired, job stopped");
		//TODO: Consider alternative... crawlJob.queue.forEach(addItemToDB(item));
		for (var i = 0; i < crawlJob.queue.length; i++) { 
			addIfMissing(crawlJob.queue[i]);
			//console.debug("Deferred: " + crawlJob.queue[i]);
			count.deferred += 1		
			} //end for
			
			setTimeout(function() {
				db.close();
				server.close();
				process.exit();
			}, 1000);

	}, timeToRun*1000); //end settimeout


		/////////////// SETUP ORIENT ///////////////
		//TODO: Change this to a require a new modele that is resposible for providing the database object
		console.debug("Connecting to orientDb");

		var server = Oriento({
		  host: 'localhost',
		  port: 2424,
		  username: 'root',
		  password: 'nokas123'
		});

		console.debug("Connected to OrientDb, Getting Database");

		dbs = server.list();
		if (dbs.filter(function(db){return db.name == "webContent"}).length == 0){
			console.error('Unable to connect to database webContent, exiting')
			process.exit()
			//db = server.create({ name: 'webContent', type: 'graph', storage: 'plocal'}).then(function (db) {
			//	console.debug('Created: ' + db.name);
				});
		} else {
			db = server.use('webContent');
			console.info("Database connected, Setting up crawler");
		}

	///////////////////// GET ITEMS THAT ARE WAITING TO BE CRAWLED /////////////////////
	console.debug('Starting setting up crawl');
	console.debug('Query DB');
	db.query('select url, nextFetchDateTime from webDocumentContainer ' +
						'where nextFetchDateTime <=:comparisonDateTime ' +
						'OR nextFetchDateTime IS NULL ' +
						'ORDER BY nextFetchDateTime', 
		{
		params: {    
			comparisonDateTime: moment().format(dateFormat), 
			}
		})
		.then(function (results){
			console.debug('DB Query Done');
			if (results.length > 0) {
				console.debug('Instantiating Crawler with ' + results[0].url);
				//Check for database errors
				//TODO: Extract settings to a config file				
				crawlJob = new Crawler(results[0].url);
				crawlJob.interval = 1000;
				crawlJob.maxDepth = 3;
				crawlJob.userAgent = "DTO Testing Crawler - Contact Nigel 0418556653";
				//TODO: Fix hack use all domains in the simplecrawler module - maybe add an option


				console.debug('adding Fetch Conditions');
				
				//Exclude Domains
				crawlJob.addFetchCondition(function(parsedURL) {
				
				//TODO: Exclude (or mark?) for state based domains.
					return parsedURL.host.substring(parsedURL.host.length - 7) == ".gov.au";
				});

				//Stop after N urls
				crawlJob.addFetchCondition(function(parsedURL) {
					if (crawlJob.queue.length >= maxItems) {
						delete parsedURL.uriPath;
						parsedURL.pathname = parsedURL.path;
						queueItem = parsedURL;
						queueItem.url = nodeURL.format(parsedURL);
						addIfMissing(queueItem)	;	
						count.deferred += 1;
						return false;
					} 
					return true;
					
				});

				//Only fetch if its due
				//TODO: This is not right, this needs a syncronous call or promise
				crawlJob.addFetchCondition(function(parsedURL) {
					//console.debug("Checking if url already done: " + JSON.stringify(parsedURL));
					var outcome;
					parsedURL.pathname = parsedURL.path;
					queueItem = parsedURL;
					queueItem.url = nodeURL.format(parsedURL);
					db.query('select nextFetchDateTime as nextFetchDateTime count from webDocumentContainer where url=:url', {params: { url: queueItem.url}})
					.then(function (result){
						if(result.length == 0) {  //Assuming 0 or 1 as url is unique key
							outcome = true;
						} else {
							if (!result[0].nextFetchDateTime) {
								outcome = true;
								//console.debug("Url(" + queueItem.url + ") found with no dts, returning: ");
							} else {
								//console.debug("Url(" + queueItem.url + ") found with dts: " + result[0].nextFetchDateTime + ", returning: " + moment().isAfter(result[0].nextFetchDateTime));
								outcome = moment().isAfter(result[0].nextFetchDateTime);
							}
						}
						if (!outcome) {
							console.debug('Url Not Due: ' + queueItem.url);
							count.notDue++;
						}
					});
				});

				console.debug('Adding event handlers');
				crawlJob
					.on("queueerror", function(errData, urlData){
						console.error("There was a queue error, Queue Erorr URL/Data: " + JSON.stringify(errData) + JSON.stringify(urlData));
						//console.debug("Queue Error Data: " + JSON.stringify(urlData));
						count.error ++;
						//TODO: If there is an error or 404, then we need to decide when to discard that entry and prevent recrawl. Might need a flag in the database.
					})
					.on("fetcherror", function(queueItem, response){
						console.info("Url Fetch Error: " + queueItem.url);
						//console.debug("Error Item" + JSON.stringify(queueItem));
						//TODO: Maybe I should just flick it to the complete handler.

						//TODO: decide what to do with server errors
						//TODO: decide what to do with server errors
						//need to store for at least a while.
						//maybe easiet would be to check if is still in some pages outlinks.
						//should be logged anyhow.
						count.serverError++;
					})
					.on("fetch404", function(){
						console.debug("A fetch 404");	
						//TODO: Decide what to do wtih not found
						//need to store for at least a while.
						//maybe easiet would be to check if is still in some pages outlinks.
						//should be logged anyhow.
						count.missing++;
					})
					.on("fetchtimeout", function(queueItem){
						console.debug("A fetch timed out");
					})
					.on("fetchclienterror", function(queueItem, errorData){
						console.error("There was a fetch client error");
						//console.debug("Fetch Client Error Item: " + JSON.stringify(queueItem));
						//console.debug("Error Client Error Data: " + JSON.stringify(errorData));
						//TODO: If there is an error or 404, then we need to decide when to discard that entry and prevent recrawl. Might need a flag in the database.
						count.error ++;
					})
					.on("fetchcomplete", function(queueItem, responseBuffer, response){ 
						//console.debug("A fetch completed");	
						queueItem.lastFetchDateTime = moment().format(dateFormat);
						nextFetch = moment();
						nextFetch.add(7, 'days')
						queueItem.nextFetchDateTime = nextFetch.format(dateFormat);
						queueItem.stateData['@class'] = "webDocumentStateData";
						queueItem.document = responseBuffer.toString('base64');
							
						db.delete()
							.from('webDocumentContainer')
							.where({url:queueItem.url})
							.limit(1)
							.scalar()
							.then(function (total) {
								//console.debug('deleted', total, 'entries');
								//TODO: Should the insert be here instead
							});
						//TODO: Use common inserting tool
						db.insert()
							.into('webDocumentContainer')
							.set(queueItem)
							.one()	
							.then(function (doc) {
								count.completed ++;				
								console.info("Url Completed: " + queueItem.url + " ("  + queueItem.stateData.contentLength + ")");
							});
					})
					.on("complete", function() {
						console.info("Stats: " + JSON.stringify(count));
						setTimeout(function() {
							db.close();
							server.close();
							process.exit();
							}, 1000);
					})
					.on("queueadd", function(queueItem){
						//console.debug("Queued - " + queueItem.url);
					})
					.on("fetchstart", function(){
						//console.debug("Fetch Started");
					})
					.on("crawlstart", function(){
						//console.debug("Crawler started event did fire");
					})
					.on("fetchredirect", function(){
						//console.debug("A fetch redirected");	
					});
					
				console.debug('Starting Crawler');
			
				console.debug('Adding ' + (results.length - 1) + ' extra items from DB');
				
				for (var j = 1; j < results.length; j++) {
						console.debug("Queueing: " + results[j].url);
						parsedURL = nodeURL.parse(results[j].url);
						if (parsedURL.port == null) {
							parsedURL.port = 80; 
							}
						//console.debug("Attempting to add adding: " + JSON.stringify(parsedURL));
						crawlJob.queue.add(parsedURL.protocol, parsedURL.hostname, parsedURL.port, parsedURL.pathname);	
					}
			} else {
			console.info("Nothing ready to crawl, exiting");
			}
			
		crawlJob.start();
		console.debug("Crawler Started");
});


