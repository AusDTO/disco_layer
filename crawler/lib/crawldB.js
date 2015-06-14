"use strict";
var winston = require('winston');
var Oriento = require('oriento');
var moment = require('moment')
var Promise = require('bluebird');
var logFile = 'logs/crawl.log';
var conf = require('../config/config.js');

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

	connect: function() {
		winston.info("Setting up database")
		this.dbs = this.server.list() 
		 
		if (this.dbs.filter(function(dbItem){return dbItem.name == conf.get('dbName')}).length == 0){
			winston.error('crawlDb module was unable to connect to database "' + conf.get('dbName') + '", exiting')
			return callback(err);
		} else {
			this.db = this.server.use(conf.get('dbName'));
			return this;
		}
	},

	close: function() {
		winston.info("Closing Database")
		this.db.close();
		this.server.close();
	},

	newQueueList: function(max, callback) {
		
		//NOTE: Seems like order introduces some unexpected behaviour
		this.db.select('*')
			.from("webDocumentContainer")
			.where("nextFetchDateTime <= '" + moment().format() + "'")
			.or('nextFetchDateTime IS NULL ')
			.limit(max) 
			.all()
			.catch(function(e){
				winston.debug("Could not select new queue for some reason");
				winston.error(e);
			})
			.then(function(result) {   
				//winston.debug(JSON.stringify(result));
				callback(result);   
			});
	},
 
	upsert: function(document) {    
		this.db.select()
			.from("webDocumentContainer")
			.where({url:document.url})
			.one()
			.catch(function (e){
				winston.error("Select Failed for some reason: " + document.url)
				winston.error(e);
				return;
			})
			.then(function(currentDocument) {
				if (!currentDocument) {
					this.db.insert()
						.into('webDocumentContainer')
						.set(document)
						.one()	
						.then(function (returnDoc) {
						winston.debug("   (Inserted): " + document.url);
							
						})
						.catch(function(e) {
							winston.error("Insert failed for some unknown reason");
							winston.error(e);
							return;
						});
				} else {
					//TODO: change to merge and update
					this.db.delete()
					.from('webDocumentContainer')
					.where({url:document.url})
					.scalar()
					.then(function (result) {
						this.db.insert()
							.into('webDocumentContainer')
							.set(document)
							.one()	
							.then(function (returnDoc) {
								returnCopy = returnDoc;
								delete returnCopy.document;
								//winston.debug(">>>>DB RETURNED JSON>>>>>> " + JSON.stringify(returnCopy));
								winston.debug("   (Updated): " + document.url);
							}) //insert then
							.catch(function(e) {
								winston.error("Insert failed for some unknown reason");
								winston.error(e);
								return; 
							});
					}) //detele then
					.catch(function (e){
						winston.error(e);
						return;
					});
				} //end else currentDocDocument found
			}) //end sel	ect then

	},
	
	checkNextFetchDate: function(url) {
		crawlDb = this;
		return new Promise(function(resolve, reject) {
			crawlDb.db.select('nextFetchDateTime') 
			.from("webDocumentContainer")
			.where({url: url})
			.scalar()
			.then(function (result) {
				//nothing or null so fetch
				if (result == undefined) {   
					resolve(true);   
				}
				else { 
					if (Object.keys(result).length) {
						//should be a date
						resolve( !moment().isAfter(moment(result, moment.ISO_8601)) )
					}
					else {
						resolve(true)
					}
				}
			})
			.catch(function(e){
				winston.error("There was an error getting a url");
				winston.error(e);
				reject(e);
			})
		})//end promise
	},
	addIfMissing: function(document)	 {
		db = this.db;
		schemaName = this.dbSchema;
		
		db.select('count(*) as count')
		.from(this.conf.get('dbSchema'))
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
					winston.error("Unable to insert document");
					winston.error(e);
					return;
				});
			}
		})
		.catch(function(e){
			winston.error("Unable to check if document exits (a select count)");
			winston.error(e);
			return;
		}); //end select then
	}
}
