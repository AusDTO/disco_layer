module.exports{
	debug = true,
	initQueueSize = 100,   //get this many from the database to kick the job off.
	maxItems = 1000,  //Stop the job after this many fetches.
	timeToRun =  240,		//Stop the job after this many seconds
	fetchIncrement = 7,	//Days to wait for next fetchi
	interval = 3000,
	logFile = 'logs/crawl.log',
	count = {  
		deferred: 0,
		completed: 0,
		error: 0,
		serverError: 0,
		missing: 0 ,
		notDue: 0 }
}