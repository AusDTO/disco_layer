Oriento = require('oriento');

/////////////// SETUP ORIENT ///////////////
//TODO: Change this to a require a new modele that is resposible for providing the database object
console.log("Connecting to orientDb");
moment = require('moment');

dateFormat = "YYYY-MM-DD HH:mm:ss" 

var server = Oriento({
  host: 'localhost',
  port: 2424,
  username: 'root',
  password: 'nokas123'
});

console.log("Connected to OrientDb, Getting Database");

dbs = server.list();
if (dbs.filter(function(db){return db.name == "webContent"}).length == 0){
	db = server.create({ name: 'webContent', type: 'graph', storage: 'plocal'}).then(function (db) {
		console.log('Created: ' + db.name);
		});
} else {
	db = server.use('webContent');
}
console.log("Database connected, Querying");

//nowDateTime = moment("2015-06-02 12:48:05", "YYYY-MM-DD HH:mm:ss");
nowDateTime= moment();


// Tue Jun 02 2015 12:48:01 GMT+0000 

console.log("The Date: " + nowDateTime.format(dateFormat));

db.query('select protocol, host, port, path, nextFetchDateTime from webDocumentContainer ' +
					'where nextFetchDateTime <=:comparisonDateTime ' +
					'OR nextFetchDateTime IS NULL ' +
					'ORDER BY nextFetchDateTime', 
	{
	params: {    
		comparisonDateTime: nowDateTime.format(dateFormat)
		},
		limit: 50
	})
	.then(function (results){
		console.log(results);
		db.close();
		server.close();
	});
