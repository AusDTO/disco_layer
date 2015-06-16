var logger = require('winston');

var conf = require('./config.js');


logger.transports.Console.level = 'log';

/*var logger = new winston.Logger({
  transports: [
    new winston.transports.Console({level:'debug'}),
  ],
  exitOnError: false
});

*/
module.exports = logger;
