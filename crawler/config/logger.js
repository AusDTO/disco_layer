var logger = require('winston')

var conf = require('./config.js');
var stdLog = conf.get('logFile') + '_std' ;
var errLog = conf.get('logFile') + '_err';

if (conf.get('debug')) {
  logger.transports.Console.level = 'debug';
  //logger.remove(winston.transports.Console);

  logger.add(winston.transports.File, {
    name: 'standard',
    filename: stdLog,
    level: 'debug'
  });
  logger.add(winston.transports.File, {
    name: 'error',
    filename: errLog,
    level: 'error'
  });
  logger.info('Debug logging enabled');
} else {
  logger.transports.Console.level = 'info';
  //logger.remove(winston.transports.Console);
  logger.add(winston.transports.File, {
    name: 'standard',
    filename: stdLog,
    level: 'info'
  });
  logger.add(winston.transports.File, {
    name: 'error',
    filename: errLog,
    level: 'error'
  });
}

logger.info('Logging Configured');

module.exports = logger;
