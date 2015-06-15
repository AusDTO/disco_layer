logger = require('winston');

var conf = require('./config.js');


var logger = new winston.Logger({
  transports: [
    new winston.transports.Console({level:'info'}),
    new winston.transports.File({ filename: conf.get('logFile'), level: 'info'})
  ],
  exitOnError: false
});

//enable debug logging if requested (default is info)
if (conf.get('debug')) {
	logger.transports.file.level = 'debug'
	logger.transports.console.level = 'debug'
}

module.exports = logger;
