#Overview
This appplication crawls all gov.au domaians (excluding states and territories) and stores the resouces
found in a database. It is the intent that other components of the discovery layer will then modify and 
enhane that crawled information to support an improved user experience.

It is a node application largely based on the simplecrawler projecct and orientDb.

##Major ToDo Items
The following are acknowledged as major todo items.

1. Logging
2. Externalisation of config

##Setup Instructions

Tested with node node 12.2 and orientDb 2.0.9. For node module dependencie refer to package information.
Steps:
###Install node
 
###Install orientDb

   TBA

###Configure webDocumentContainer schema

   TBA

###Configure datetimeformat

   `ALTER DATABASE DATETIMEFORMAT yyyy-MM-dd'T'HH:mm:ssX`

###Install Dependencies
Dependencies are configured in the package.

   * `npm install`

###Run
The following command line parameters can be used.
* debug
 - Turn on debugging messages (flag only)
 - format: Boolean
 - default: false
* queue
 - format: int
 - How many items to put in initial queue
 - default: 100
* max
 - Stop the job after this many fetches
 - format: 'int'
 - default: 1000
* time
 - Stop the job after this time
 - format: 'int'
 - default: 3000
* fetchwait
 - Wait this many days before refetching the items
 - format: 'int'
 - default: 7
* interval
 - Millisecond intervale between requests
 - format: 'int'
 - default: 2000
* logfile
 - logfile location
 - default: 'logs/crawl.log
* dbHost
 - Database Host
 - format: String
 - default: '52.64.24.77'
* Database Port
 - format: 'int'
 - default: 2424
 - arg: 'dbPort'
* dbUser
 - Database Username
 - format: String
 - default: 'root'
* dbPass
 - Database Password
 - format: String
 - default: 'developmentpassword'
* dbName
 - The Database to use
 - format: String
 - default: 'webContent',
* dbSchema
 - The Database Schema Being Used
 - format: String
 - default: 'weDocumentContainer'


##Significant Internal Functions
### Timeout
This function allow the application to only run for a specific time. Once completed any resources that have not
been fetched are persisted to be selected later. 

### Fetch Condition - gov.au domain restriction
Ensures that we only follow links to Australian Government Domains

### Fetch Condition - Max items Processed
No items are processed above the max items limit, they are instead persisted to the database to be fetched another time.

### Fetch Condition - Only Fetch If Due
Items are not processed if the next Fetch data has not been reached.

### newQueueList
Fetches a list of items that are ready to be fetched from the database.

###addIfMissing
Stores an item in the database if not already there. Used when deffering tasks.

###upSert
Update or Insert. If item is missing it will insert otherwise it will create a copy delete and insert.

>Note: This should be supported by the oriento library but it only appears to support the set clause where in this scenario the merge is needed.


###checkNextFetchDate
Gets and checks the next fetch date in the database ccompared to todays date.
