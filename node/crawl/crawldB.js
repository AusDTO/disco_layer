/////NOTE: ORIENTDB NEEDS ITS DATETIME FORMAT ALTERED TO WORK NICELY WITH THE ORIENTO API
// ALTER DATABASE DATETIMEFORMAT yyyy-MM-dd'T'HH:mm:ssX
/////

Oriento = require('oriento');
moment = require('moment')
Promise = require('bluebird');

module.exports = {
	server: Oriento({
			host: 'localhost',
			port: 2424,
			username: 'root',	
			password: 'nokas123'}),
	dbName: "webContent",
	dbSchemaName: "webDocumentContainer",
	dbs: null,
	db: null,

//////////////////////////////////////////////////////////////////
	connect: function() {
		console.log("Setting up database")
		this.dbs = this.server.list() 

		if (this.dbs.filter(function(dbItem){return dbItem.name == this.dbName}).length == 0){
			console.error('crawlDb module was unable to connect to database " + dbName + ", exiting')
			return callback(err);
		} else {
			this.db = this.server.use(this.dbName);
			return this;
		}
	},

//////////////////////////////////////////////////////////////////	
	close: function() {
		console.log("Closing Database")
		this.db.close();
		this.server.close();
	},

//////////////////////////////////////////////////////////////////
newQueueList: function(max, callback) {
		
		//NOTE: Seems like order introduces some unexpected behaviour
		this.db.select('*')
			.from("webDocumentContainer")
			.where("nextFetchDateTime <= '" + moment().format() + "'")
			.or('nextFetchDateTime IS NULL ')
			.limit(max) 
			.all()
			.catch(function(e){
				console.log("Could not select new queue for some reason");
				console.log(e);
			})
			.then(function(result) {   
				//console.debug(JSON.stringify(result));
				callback(result);   
			});
	},
 
 //////////////////////////////////////////////////////////////////
	upsert: function(document) {    
		this.db.select()
			.from("webDocumentContainer")
			.where({url:document.url})
			.one()
			.catch(function (e){
				console.error("Select Failed for some reason: " + document.url)
				console.error(e);
				return;
			})
			.then(function(currentDocument) {
				if (!currentDocument) {
					this.db.insert()
						.into('webDocumentContainer')
						.set(document)
						.one()	
						.then(function (returnDoc) {
							console.debug("   (Inserted): " + document.url);
							
						})
						.catch(function(e) {
							console.error("Insert failed for some unknown reason");
							console.error(e);
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
								//console.debug(">>>>DB RETURNED JSON>>>>>> " + JSON.stringify(returnCopy));
								console.debug("   (Updated): " + document.url);
							}) //insert then
							.catch(function(e) {
								console.error("Insert failed for some unknown reason");
								console.error(e);
								return; 
							});
					}) //detele then
					.catch(function (e){
						console.error(e);
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
//						console.log("Url checkNextFetchDate: ",  !moment().isAfter(moment(result, moment.ISO_8601)), "\n    Based on: ", moment(result, moment.ISO_8601) );
						resolve( !moment().isAfter(moment(result, moment.ISO_8601)) )
					}
					else {
						resolve(true)
					}
				}
			})
			.catch(function(e){
				console.error("There was an error getting a url");
				console.error(e);
				reject(e);
			})
		})//end promise
	},
	addIfMissing: function(document)	 {
		db = this.db;
		schemaName = this.dbSchema;
		
		db.select('count(*) as count')
		.from(this.dbSchemaName)
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
					console.error("Unable to insert document");
					console.error(e);
					return;
				});
			}
		})
		.catch(function(e){
			console.error("Unable to check if document exits (a select count)");
			console.error(e);
			return;
		}); //end select then
	}
}
