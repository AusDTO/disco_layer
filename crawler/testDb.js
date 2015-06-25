
var conf = require('./config/config.js');
var logger=require('./config/logger.js'); 
crawlDb = require('./lib/crawlDb').connect();
var fs = require('fs');
moment = require('moment');

fs.readFile('./update.json', function(error, documentString){

	document = JSON.parse(documentString);
	lastFetchDateTime = moment().format();
	nextFetch = moment().add(conf.get('fetchIncrement'), 'days');

	tempFakeDocument = {
		url:"fakeUrl1",
		stateData: {},
		lastFetchDateTime: moment().format(),
		nextFetchDateTime: nextFetch.format(),
		document: "a stupid string to play a document".toString('base64')
	}

	document = JSON.parse(documentString);
	
	crawlDb.upsert(tempFakeDocument)
	//crawlDb.upsert(document);
/*

	if(document) {

		console.log('seems like i have the document');
		console.log('protocol: ' + document.host);
	}
	if(error) {
		console.log("File error exiting");
		return;
	} else {
		console.log('sending crawlDb.upsert for:' + document.url);
		console.log('crawlDb.upsert sent for:' + document.url);
		
	}
	*/
});



