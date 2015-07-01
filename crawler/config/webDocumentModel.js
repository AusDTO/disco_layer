    var Sequelize = require('sequelize');

    module.exports = function(sequelize, DataTypes) {
        return sequelize.define('webDocument', {
            url: {
                type: Sequelize.TEXT,
                allowNull: false,
                primaryKey: true,
                isUrl: true
            },
            host: {
                type: Sequelize.STRING
            },
            document: {
                type: Sequelize.BLOB
            },

            lastFetchDateTime: {
                type: Sequelize.DATE
            },
            nextFetchDateTime: {
                type: Sequelize.DATE
            },
            path: {
                type: Sequelize.STRING
            },
            port: {
                type: Sequelize.INTEGER
            },
            protocol: {
                type: Sequelize.STRING
            },
            httpCode: {
                type: Sequelize.INTEGER
            },
            contentType: {
                type: Sequelize.STRING
            },
            stateData: {
                type: Sequelize.JSON
            },
            fetchStatus: {
                type: Sequelize.STRING
            },
            fetched: {
                type: Sequelize.BOOLEAN
            },
            //NOTE: This is not yet populated
            outlinks: {
                type: Sequelize.ARRAY(Sequelize.TEXT)
            },
            hash:{
                type: Sequelize.STRING
            }
        },{
            indexes: [
                // Create a unique index on email
                {
                    name: 'url',
                    unique: true,
                    method: 'BTREE',
                    fields: ['url']
                }, {
                    name: 'lastFetchDateTime',
                    method: 'BTREE',
                    fields: ['lastFetchDateTime']
                }, {
                    name: 'nextFetchDateTime',
                    method: 'BTREE',
                    fields: ['nextFetchDateTime']
                }, {
                    name: 'host',
                    method: 'BTREE',
                    fields: ['host']
                }, {
                    name: 'httpCode',
                    method: 'BTREE',
                    fields: ['httpCode']
                }, {
                    name: 'fetchStatus',
                    method: 'BTREE',
                    fields: ['fetchStatus']
                }
            ]
        });
    };