winston = require('winston');
var convict = require('convict');


var conf = convict({
    debug: {
        doc: 'Turn on debugging messages (flag only)',
        format: Boolean,
        default: false,
        arg: 'debug'
    },
    initQueueSize: {
        doc: 'How many items to put in initial queue',
        default: 100,
        arg: 'queue'
    },
    maxItems: {
        doc: 'Stop the job after this many fetches',
        format: 'int',
        default: 1000,
        arg: 'max'
    },
    timeToRun: {
        doc: 'Stop the job after this time',
        format: 'int',
        default: 3000,
        arg: 'time'
    },
    fetchIncrement: {
        doc: 'Wait this many days before refetching the items',
        format: 'int',
        default: 7,
        arg: 'fetchwait'
    },
    concurrency: {
        doc: 'How much concurrenct should the crawler implement',
        format: 'int',
        default: 2,
        arg: 'conc'
    },
        interval: {
        doc: 'Millisecond intervale between requests',
        format: 'int',
        default: 2000,
        arg: 'interval'
    },
    logFile: {
        doc: 'logfile location',
        //TODO: Path validation
        format: function check(val) {
            return true;
        },
        default: './logs/crawl.log',
        arg: 'logfile'
    },
    //TODO - Ensure folder is there, otherwise no file logging.
    dbHost: {
        doc: 'Database Host',
        format: String,
        default: '52.64.24.77',
        arg: 'dbHost'
    },
    dbPort: {
        doc: 'Database Port',
        format: 'int',
        default: 2424,
        arg: 'dbPort'
    },
    //TODO: Create new DB user account.
    dbUser: {
        doc: 'Database Username',
        format: String,
        default: 'root',
        arg: 'dbUser'
    },
    //TODO: Create new DB user account.
    dbPass: {
        doc: 'Database Password',
        format: String,
        default: 'developmentpassword',
        arg: 'dbPass'
    },
    dbName: {
    doc: 'The Database to use',
    format: String,
    default: 'webContent',
    arg: 'dbName'
    },
    dbSchema: {
    doc: 'The Database Schema Being Used',
    format: String,
    default: 'webDocumentContainer',
    arg: 'dbSchema'
    }
});


conf.validate();

module.exports = conf;

//console.log(JSON.stringify(conf));