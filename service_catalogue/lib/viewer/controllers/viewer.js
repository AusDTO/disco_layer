var exports = module.exports;
var fs = require('fs');
var CONF = require('config');
var S = require('string');
var jf = require('jsonfile');
var lunr = require('lunr');
exports.graph = function (req, res) {
    var template = __dirname + '/../views/graph';
    var context = {};

    res.render(template, context);
}
exports.graph_data = function (req, res) {
    var tmppath = '/home/maxious/sc/catalogues/';

    fs.readdir(tmppath, function (err, files) {
        if (err) {
            res.status(500).send(JSON.stringify(e));
        } else {
            var nodeids = new Set();
            var edgeids = new Set();
            var dimdata = {
                "nodes": [{id: "AUSGOV", label: 'Australian Government Services'}], "edges": []

            };

            // load each service from service file
            files.forEach(function (file) {
                if (file != 'model.json' && file != 'definition.json') {
                    try {
                        var data = jf.readFileSync(tmppath + file);
                        // org
                        nodeids.add(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceOrganisation.id);
                        dimdata["nodes"].push({
                            id: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceOrganisation.id,
                            label: data.organisationDefinition.serviceOrganisation.name,
                            size: 1
                        });
                        dimdata["edges"].push({
                            id: data.organisationDefinition.serviceOrganisation.id + "AUSGOV",
                            source: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceOrganisation.id ,
                            target: data.organisationDefinition.serviceOrganisation.id +  "AUSGOV"
                        });
                        // dimensions
                        for (var i in data.organisationDefinition.serviceDimensions) {
                            nodeids.add(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceDimensions[i].id);
                            dimdata["nodes"].push({
                                id: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceDimensions[i].id,
                                label: data.organisationDefinition.serviceDimensions[i].name,
                                size: 1
                            });
                            dimdata["edges"].push({
                                id: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceDimensions[i].id,
                                source: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceOrganisation.id ,
                                target: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceDimensions[i].id
                            });
                        }
                        for (var i in data.organisationDefinition.links) {
                            if (nodeids.has(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source)
                                && nodeids.has(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].target)) {
                                if(!edgeids.has(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source + data.organisationDefinition.links[i].target)) {
                                    edgeids.add(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source + data.organisationDefinition.links[i].target);
                                    dimdata["edges"].push({
                                        id: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source + data.organisationDefinition.links[i].target,
                                        source: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source,
                                        target: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].target
                                    });
                                } else {
                                    console.log(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source + data.organisationDefinition.links[i].target);
                                }
                            } else {
                                if (!nodeids.has(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source)) {
                                    console.log(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].source)
                                }
                                if (!nodeids.has(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].target)) {
                                    console.log(data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.links[i].target);
                                }


                            }
                        }
                    } catch (e) {
                        console.log(file);
                        console.log(e);
                        res.status(500).send(JSON.stringify(e));
                    }
                }
            });
        }
        res.status(200).send(JSON.stringify(dimdata));
    });

}
exports.tree = function (req, res) {
    var template = __dirname + '/../views/tree';
    var context = {};
    var alertDanger = [];
    res.render(template, context);
}
exports.home = function (req, res) {
    var template = __dirname + '/../views/home';
    //https://raw.githubusercontent.com/olivernn/lunr.js/master/example/index_builder.js
    var index = lunr(function () {
        this.field('title', {boost: 10})
        this.field('body')
        this.ref('id')
    })
    //TODO automatically sync from github
    var tmppath = '/home/maxious/sc/catalogues/';
    var alertDanger = []
    fs.readdir(tmppath, function (err, files) {
        if (err) {
            alertDanger.push(err);
            var context = {
                alertDanger: alertDanger
            }

            res.render(template, context);
        } else {
            var dimdata = {};
            // load each service from service file
            files.forEach(function (file) {
                if (file != 'model.json' && file != 'definition.json') {
                    try {
                        var data = jf.readFileSync(tmppath + file);

                        for (var i in data.organisationDefinition.serviceDimensions) {
                            if (data.organisationDefinition.serviceDimensions[i].type == 'SVC') {
                                data.organisationDefinition.serviceDimensions[i].serviceOrganisation = data.organisationDefinition.serviceOrganisation;
                                dimdata[data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceDimensions[i].id] = data.organisationDefinition.serviceDimensions[i];
                                index.add({
                                    id: data.organisationDefinition.serviceOrganisation.id + data.organisationDefinition.serviceDimensions[i].id,
                                    title: data.organisationDefinition.serviceDimensions[i].name,
                                    body: data.organisationDefinition.serviceDimensions[i].description
                                });
                            }
                        }
                    } catch (e) {
                        console.log(file);
                        console.log(e);
                        alertDanger.push("Cannot parse JSON in " + file + " due to " + e);
                    }
                }
            });


            var context = {
                data: JSON.stringify(dimdata), index: JSON.stringify(index),
                alertDanger: alertDanger,
                pageTitle: "Viewer"
            }

            res.render(template, context);
        }
    })
}