
//Eventually this should be generically defined as a view within the service information. Then it can be further customised.
//For now it just selects the nodes which are known to be the services, and outputs all the successors and decendants as attributes.
//link information will be appended to target contents - this is particularly something that should be defined in views.

fs = require('fs');
cytoscape = require('cytoscape');
conf = require('./config/config.js');
path = require('path');
var logger=require('./config/logger.js'); 


logger.info(JSON.stringify(conf));



//TODO: Loop through all organisations.
logger.log("Loading Service File");
fs.readFile(conf.get('input'), function (err,data) {
	if (err) {
		logger.info("In error condition opening events file");
		logger.info("__dirname: " + __dirname);
		return logger.log(err);
		}
	data = JSON.parse(data);
	 
//	logger.log("The Data::::\n" +  JSON.stringify(data, null, 2));
	
	var elements = data.organisationDefinition.serviceDimensions;
	elements = elements.concat(data.organisationDefinition.serviceOrganisation)
	.concat(data.organisationDefinition.components);
	logger.log("File Elements Loaded: " + elements.length);
	//logger.log("Example Element: " + JSON.stringify(elements[3]));

//TODO - Validate JSON

	logger.log("Translating Service Data For Cytoscape");
	logger.log("   Nodes...");
	// restructure to meet the needs of cytoscape
	var cyElements = [];
	elements.forEach(function(element) {
		//logger.log(element.type);
		var tempElement ={};
		tempElement.data = element;
		cyElements.push(tempElement);
	//	}
	});

	logger.log("   Links...");
	var links = data.organisationDefinition.links;
	// restructure to meet the needs of cytoscape
	var cyLinks = [];
	links.forEach(function(element) {
		var tempElement = {};
		tempElement.data = element;
		cyLinks.push(tempElement);
		});

	logger.log("Service Data Loaded, Creating  CytoScape Graph");

	var cy = cytoscape({
		elements: { 
			nodes: cyElements, 
			edges: cyLinks
			}
	});


	logger.log("Outputing search optimised service document");
	//TODO: Use model or field to determine the dimensions we are interested in.

	
	
	serviceElements = cy.$("[type = '" + conf.get('serviceNodeType') + "']");
	
	logger.debug("Looking for: " + "[type = '" + conf.get('serviceNodeType') + "']" );
	logger.debug("Service Elements Found: " + serviceElements.size());
	var serviceDocument;
	var ancestors;
	var successors; 


//NOTE: Information that maintains relevence is maintained on the service
//            Information that has decreasing relevence with distance is maintained on the dimensions or subs.
	logger.log('Starting Loop over services');
	//TODO: Make sure that the folder is there - fs.writeFile does not ensure.
	if( !fs.existsSync(conf.get('outputs')) ) {
		fs.mkdirSync(conf.get('outputs'));
		}	
	serviceElements.forEach(function(service, i, eles) {
		logger.profile(service.data('name'));
		serviceDocument = {documentType : "ServiceInformation"};
		serviceDocument.service = service.data();
		serviceDocument.service.secondary = false;
		serviceDocument.service.lifeEvents = [];
		serviceDocument.service.serviceTypes = [];

		if (service.data('lifeEvents').length > 0 ) {
			serviceDocument.service.lifeEvents = service.data('lifeEvents');			
		}
		if (service.data('serviceTypes').length > 0 ) {
			serviceDocument.service.serviceTypes = service.data('serviceTypes');			
		}

		ancestors = service.predecessors().nodes();
		serviceDocument.Dimension = [];
		ancestors.forEach(function(ele, i, eles) { 
			//If there is an ancestor service then this service is secondary
			if (ele.isNode()) {
				if (   ele.data('type') === conf.get('serviceNodeType')   )  {
					serviceDocument.service.secondary = true;
					//serviceDocument.service.name + service.data('name');  
				} 
				//dijkstra gets the distance from the service node to this node
				var dijkstra = cy.elements().dijkstra(ele, directed=true);				
				var dist = dijkstra.distanceTo( service );
				serviceDocument.Dimension[i] = {};
				serviceDocument.Dimension[i].dist = dist;	 
				serviceDocument.Dimension[i].id = ele.id();	 
				serviceDocument.Dimension[i].name = ele.data( 'name');	 
				serviceDocument.Dimension[i].desc = ele.data( 'description');	 
				serviceDocument.Dimension[i].url = ele.data( 'url');	 
				if (typeof ele.data('lifeEvents') !== 'undefined') {
					if (ele.data('lifeEvents').length > 0 ) {
						serviceDocument.service.lifeEvents = serviceDocument.service.lifeEvents.concat(ele.data('lifeEvents'));
					}
				}
				if (typeof ele.data('serviceTypes') !== 'undefined') {
					if (ele.data('serviceTypes').length > 0 ) {
						serviceDocument.service.serviceTypes = serviceDocument.service.serviceTypes.concat(ele.data('serviceTypes'));
					}
				}
				//TODO: Consider adding information from incomming link for each service - not required yet though
			}
		}); //forEach ancestor

		serviceDocument.Subs = [];
		successors = service.successors().nodes();
		successors.forEach(function(ele, i, eles) { 
			if (ele.isNode()) {
				serviceDocument.Subs[i] = {};
				serviceDocument.Subs[i].id  = ele.id();
				serviceDocument.Subs[i].name = ele.data( 'name');
				serviceDocument.Subs[i].desc = ele.data('description');
				//Add link information - requried for DHS atleast
			}
		}); //forEach successor

		fs.writeFile(path.join(conf.get('outputs'), service.id() + '(' + service.data('name') + ').json'), JSON.stringify(serviceDocument, null, 2));
		logger.profile(service.data('name'));
	});//for each service node












});
