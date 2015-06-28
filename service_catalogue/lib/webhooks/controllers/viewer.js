var exports = module.exports;
var fs = require('fs');
var CONF = require('config');
var S = require('string');
var jf = require('jsonfile');
var lunr = require('lunr');
exports.graph = function (req, res) {
    var template = __dirname + '/../views/home';
}
    exports.home = function (req, res) {
        var template = __dirname + '/../views/home';
    //https://raw.githubusercontent.com/olivernn/lunr.js/master/example/index_builder.js
    var index = lunr(function () {
        this.field('title', {boost: 10})
        this.field('body')
        this.ref('id')
    })
    var data = jf.readFileSync('/home/maxious/serviceCatalogue/DHS.json');
    var dimdata = {};
    for (var i in data.organisationDefinition.serviceDimensions)
    {
        if (data.organisationDefinition.serviceDimensions[i].type == 'SVC') {
            dimdata[data.organisationDefinition.serviceDimensions[i].id] = data.organisationDefinition.serviceDimensions[i];
            index.add({
                id: data.organisationDefinition.serviceDimensions[i].id,
                title: data.organisationDefinition.serviceDimensions[i].name,
                body: data.organisationDefinition.serviceDimensions[i].description
            });
        }
    }

    var context = {data: JSON.stringify(dimdata), index: JSON.stringify(index)}

            res.render(template, context);
}