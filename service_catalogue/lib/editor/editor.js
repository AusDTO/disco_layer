/**
 * This is a self-contained module that defines its routes, callbacks, models and views
 * all internally. Such approach to code organization follows the recommendations of TJ:
 *
 * http://vimeo.com/56166857
 *
 */

var app = module.exports = module.parent.exports.setAppDefaults();

// Don't just use, but also export in case another module needs to use these as well.
app.callbacks = require('./controllers/editor');
app.models = require('./models');

//-- For increased module encapsulation, you could also serve templates with module-local 
//-- paths, but using shared layouts and partials may become tricky
//var hbs = require('hbs');
//app.set('views', __dirname + '/views');
//app.set('view engine', 'handlebars');
//app.engine('handlebars', hbs.__express);

// Module's Routes. Please note this is actually under /hello, because module is attached under /hello
app.get('/', app.callbacks.home);
app.get('/edit/organisation/*/*/*', app.callbacks.showOrganisation);
app.get('/autocomplete/*/*/*/*', app.callbacks.autocomplete);
app.get('/edit/service/*/*/*/*', app.callbacks.showServiceEditor);
app.get('/edit/org_definition/*/*/*', app.callbacks.showOrgDefnEditor);
app.get('/edit/org_model/*/*/*', app.callbacks.showOrgModelEditor);
app.get('/edit/dimension/*/*/*/*', app.callbacks.showDimensionEditor);
app.get('/edit/component/*/*/*/*', app.callbacks.showComponentEditor);
app.get('/edit/channel/*/*/*/*', app.callbacks.showChannelEditor);
app.post('/edit/service/*/*/*/*', app.callbacks.showServiceEditor);
app.post('/edit/org_definition/*/*/*', app.callbacks.showOrgDefnEditor);
app.post('/edit/org_model/*/*/*', app.callbacks.showOrgModelEditor);
app.post('/edit/dimension/*/*/*/*', app.callbacks.showDimensionEditor);
app.post('/edit/component/*/*/*/*', app.callbacks.showComponentEditor);
app.post('/edit/channel/*/*/*/*', app.callbacks.showChannelEditor);
app.get('/submit/*/*', app.callbacks.submit);
app.get('/repo/*/*', app.callbacks.showRepo);