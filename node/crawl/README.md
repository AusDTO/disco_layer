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


##Functions
### Timeout
This function allow the application to only run for a specific time. Once completed any resources that have not
been fetched are persisted to be selected later. 

###

