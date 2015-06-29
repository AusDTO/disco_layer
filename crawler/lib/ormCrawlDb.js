var Sequelize = require('sequelize');
var moment = require('moment');
var Promise = require('bluebird');
var conf = require('../config/config.js');
var logger = require('../config/logger');



module.exports = {
    db: new Sequelize(
        conf.get('dbName'),
        conf.get('dbUser'),
        conf.get('dbPass'), {
            host: conf.get('dbHost'),
            dialect: 'postgres',
            pool: {
                max: 5,
                min: 0,
                idle: 10000
            },
            logging: null
        }),
    webDocument: null,

    connect: function() {
        orm = this;
        return new Promise(function(resolve, reject) {
            orm.db.authenticate()
                .then(function() {
                    orm.db.import('../config/webDocumentModel');
                    //orm.db.sync({force: true});
                    orm.db.sync();
                    orm.webDocument = orm.db.model('webDocument');
                    resolve(orm);
                })
                .catch(function(e) {
                    reject(e);
                });
        });
    },

    upsert: function(document) {
        orm = this;
        return new Promise(function(resolve, reject) {
            orm.webDocument.upsert(document)
                .then(function(result) {
                    resolve(result);
                })
                .catch(function(e) {
                    reject(e);
                });
        });
    },

    readyForFetch: function(url) {
        orm = this;
        return new Promise(function(resolve, reject) {
            orm.webDocument.findOne({
                where: {
                    url: url
                }
            })
            //TODO CHECK NULL TREATMENT
            .then(function(result) {
                if (result !== null) {
                    if (result.nextFetchDateTime <= moment()) {
                        logger.debug("Url: " + url + " is ready to fetch");
                        resolve(true);
                    } else {
                        logger.debug("Url: " + url + " is not ready to fetch");
                        resolve(false);
                    }
                } else {
                    logger.debug("Url: " + url + " is ready to fetch (not found)");
                    resolve(false);
                }
            });
        });
    },



    addIfMissing: function(document) {
        orm = this;
        return new Promise(function(resolve, reject) {
            orm.webDocument.findOrCreate({
                where: {
                    url: document.url
                },
                host: document.host
            })
                .then(function(result, newRow) {
                    if (newRow) {
                        logger.debug('addIfMissing Added URL: ' + document.url);
                    } else {
                        logger.debug('addIfMisssing URL Existed: ' + document.url);
                    }
                    resolve(result, newRow);
                })
                .catch(function(e) {
                    logger.debug('addIfMissing Failed for url: ' + document.url);
                    logger.error('addIfMission Result Error: ' + e);
                    reject(e);
                });
        });
    },

    newQueueList: function(limit, callback) {
        orm = this;
        return new Promise(function(resolve, reject) {
            var now = moment().format();
            orm.webDocument.findAll({
                where: Sequelize.or({
                    nextFetchDateTime: {
                        lte: now
                    }
                }, {
                    nextFetchDateTime: null
                }),
                limit: conf.get('initQueueSize')
            })
                .then(function(result) {
                    resolve(result);
                })
                .catch(function(e) {
                    logger.error("Queue Select Failed: " + row.url);
                    reject(e);
                });
        });
    },

};