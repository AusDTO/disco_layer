    var Sequelize = require('sequelize');

    module.exports = function(sequelize, DataTypes) {
        return sequelize.define('webDocument', {
            url: {
                type: Sequelize.STRING,
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
            }

            /*indexes: [{
                        unique: true,
                        fields: ['url']
                    }]
*/
        });
    };