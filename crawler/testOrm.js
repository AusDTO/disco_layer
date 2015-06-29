console.log("starting");

var fs = require('fs');
var conf = require('./config/config.js');
var path = require('path');
var nodeURL = require('url');
var Crawler = require("simplecrawler");
var moment = require('moment');
var logger = require('./config/logger.js');
var Promise = require('bluebird');

db = require('./lib/ormCrawlDb')
    .connect()
    .then(function(orm) {
        orm.upsert({
            url: "http://fake.host.gov.au/some/random/path/and/file2.html",
            host: "fake.host.gov.au",
            lastFetchDateTime: moment(),
            nextFetchDateTime: moment().add(7, 'days'),
            path: "/",
            port: 80,
            protocol: "https",
            contentType: "text/html",
            stateData: {
                requestLatency: 437,
                requestTime: 819,
                contentLength: 40427,
                contentType: "text/html; charset=utf-8",
                code: 200,
                headers: {
                    date: "Mon, 22 Jun 2015 11:46:42 GMT",
                    server: "Apache",
                    p3p: "CP=\"NOI ADM DEV PSAi COM NAV OUR OTRo STP IND DEM\"",
                    cachecontrol: "no-cache, max-age=600",
                    pragma: "no-cache",
                    setcookie: [
                        "3d9b206e19a45952c4f378835b6dd7da=6203c0407623d08051063ed18f7920f7; path=/"
                    ],
                    expires: "max-age=29030400, public",
                    vary: "Accept-Encoding",
                    contentlength: "40427",
                    connection: "close",
                    contenttype: "text/html; charset=utf-8"
                },
                downloadTime: 382,
                actualDataSize: 40427,
                sentIncorrectSize: false
            },
            fetchStatus: "Downloaded",
            fetched: true
        });

        orm.readyForFetch("http://fake.host.gov.au/some/random/path/and/file2.html");

        orm.readyForFetch("http://fake.host.whichisnotindbgov.au/some/random/path/and/file2.html");

        orm.addIfMissing({
            url: "http://fake.host.gov.au/some/random/path/and/file2.html",
            host: "fake.host.gov.au"
        });

        orm.addIfMissing({
            url: "http://newfake.host.gov.au/some/random/path/and/file2.html",
            host: "newfake.host.gov.au"
        });

        orm.newQueueList()
            .then(function(result) {
                result.forEach(function(item) {
                        logger.debug("Queue Row: " + item.url);
                });
            });

    });

