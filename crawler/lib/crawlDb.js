"use strict";
var Oriento = require('oriento');
var moment = require('moment')
var Promise = require('bluebird');
var logFile = 'logs/crawl.log';
var conf = require('../config/config.js');
var logger=require('../config/logger');

/////NOTE: ORIENTDB NEEDS ITS DATETIME FORMAT ALTERED TO WORK NICELY WITH THE ORIENTO API
// ALTER DATABASE DATETIMEFORMAT yyyy-MM-dd'T'HH:mm:ssX
/////

module.exports = {
	server: Oriento({ 
		host: conf.get('dbHost'),
		port: conf.get('dbPort'),
		username: conf.get('dbUser'),
		password: conf.get('dbPass')
		}),
	get: function() {
		return this;
	},

	connect: function() {
		logger.info("Setting up database")
		this.dbs = this.server.list() 
		 
		if (this.dbs.filter(function(dbItem){return dbItem.name == conf.get('dbName')}).length == 0){
			logger.error('crawlDb module was unable to connect to database "' + conf.get('dbName') + '", exiting')
			return callback(err);
		} else {
			logger.info('Database Successfully Connected');
			this.db = this.server.use(conf.get('dbName'));
			return this;
		}
	},

	close: function() {
		logger.info("Closing Database")
		this.db.close();
		this.server.close();
	},

	newQueueList: function(limit, callback) {
		//TODO: Primisify this

		//NOTE: Seems like order introduces some unexpected behaviour
		this.db.select('*')
			.from("webDocumentContainer")
			.where("nextFetchDateTime <= '" + moment().format() + "'")
			.or('nextFetchDateTime IS NULL ')
			.limit(limit) 
			.all()
			.catch(function(e){
				logger.debug("Could not select new queue for some reason");
				logger.error(e);
			})
			.then(function(result) {   
				callback(result);   
				logger.verbose("QueueList: " + JSON.stringify(result));
			});
	},
 
	upsert: function(document) {    
		//Non destructive update or insert
		//NOTE: This does not use the query builder becuase I wasnt able to get it working with the combination of CONTENT and UPSERT

		//Add some hints for orientDb so that it handles the documents properly (type d = document)
		document.stateData['@class'] =  'webDocumentStateData';
		document.stateData['@type'] =  'd';
		document['@type'] =  'd';

		this.db.query("UPDATE webDocumentContainer CONTENT :document WHERE url= :url",
			{params: {
				document: document,
				url: document.url
				}
		})
		.then(function(){
			logger.debug("Database UPSERT Complete");
		})
		.catch(function(e){
			logger.error("Database UPSERT Failed");
			logger.error(e);
		});
	},
	
	readyForFetch: function(url) {
		var crawlDb = this;
		return new Promise(function(resolve, reject) {
			crawlDb.db.select('nextFetchDateTime') 
			.from("webDocumentContainer")
			.where({url: url})
			.scalar()
			.then(function (result) {
				//nothing or null so fetch
				if (result == undefined) {   
					logger.debug('readyForFetch url: '+ url + '\nreadyForFetch result: ' + result);
					resolve(true);   
				}
				else { 
					logger.debug('readyForFetch url: '+ url + " Database result:  " + result);
					if (Object.keys(result) == '@rid') {
						//no date
						logger.debug('readyForFetch url: '+ url + '\nFound but no date');
						resolve(true);
					} else {
						logger.debug('readyForFetch url: '+ url + '\nreadyForFetch Date Check: ' + moment().isAfter(moment(result, moment.ISO_8601)));
						resolve( moment().isAfter(moment(result, moment.ISO_8601)) )
					}
				}
			})
			.catch(function(e){
				logger.error("There was an error getting a url");
				logger.error(e);
				reject(e);
			})
		})//end promise
	},
	addIfMissing: function(document)	 {
		var db = this.db;
		var schemaName = conf.get('dbSchema');
		
		db.select('count(*) as count')
		.from(conf.get('dbSchema'))
		.where({url: document.url})
		.scalar()
		.then(function (count){
			if (count == 0) {
				db.insert()
				.into("webDocumentContainer")
				.set(document)
				.one()
				.then(function(){
				})
				.catch(function(e){
					logger.error("Unable to insert document");
					logger.error(e);
					return;
				});
			}
		})
		.catch(function(e){
			logger.error("Unable to check if document exits (a select count)");
			logger.error(e);
			return;
		}); //end select then
	}
}
