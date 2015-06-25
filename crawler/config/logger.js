
var winston = require('winston')

var conf = require('./config.js');

var winston = new winston.Logger({
   transports: [
     new winston.transports.Console({level:'info'}),
     new winston.transports.File({ filename: conf.get('logFile'), level: 'info', maxsize: 1024, tailable: true})
     ]
 });
//enable debug logging if requested (default is info)
if (conf.get('debug')) {
	winston.transports.file.level = 'debug'
	winston.transports.console.level = 'debug'
	winston.info('Debug logging enabled');
}

winston.info('Logging Configured');

module.exports = winston
