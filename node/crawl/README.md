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
1. Install node
 
2. Install orientDb

   TBA

3. Configure webDocumentContainer schema

   TBA

4. Configure datetimeformat

   TBA

5. Install Dependencies

   * npm install simplecrawler
   * npm install moment
   * npm install oriento
   * npm install bluebird


##Significant Functions
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
