
moment = require('moment');
			 dateFormat = "YYYY-MM-DD HH:mm:ss" 

			thecurrentfetch = moment().format(dateFormat);
			nextFetch = moment();
			nextFetch.add(7, 'days');


			 queueItem.lastFetchDateTime = workingNow.toString(); // defaults to now
			 queueItem.nextFetchDateTime = nextFetch.toString();
			 
			 //TODO: Format date as: yyyy-MM-dd HH:mm:ss or change orientDB format.
			 
console.log("Now: "  + fetchNow.format(dateFormat));
console.log("1WK: " + nextFetch.format(dateFormat));
 
