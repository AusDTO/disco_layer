
//Eventually this should be generically defined as a view within the service information. Then it can be further customised.
//For now it just selects the nodes which are known to be the services, and outputs all the successors and decendants as attributes.
//link information will be appended to target contents - this is particularly something that should be defined in views.

fs = require('fs');
cytoscape = require('cytoscape');
path = require('path');

filename = 'DHS12.json';
orgname = 'DHS';
serviceNodeType = 'SVC';


//TODO: Loop through all organisations.
console.log("Loading Service File");
fs.readFile(path.join(__dirname, filename), function (err,data) {
	if (err) {
		console.info("In error condition opending events file");
		console.info("__dirname: " + __dirname);
		return console.log(err);
		}
	data = JSON.parse(data);
	 
//	console.log("The Data::::\n" +  JSON.stringify(data, null, 2));
	
	var elements = data.organisationDefinition.serviceDimensions;
	elements = elements.concat(data.organisationDefinition.serviceOrganisation)
	.concat(data.organisationDefinition.components);
	console.log("File Elements Loaded: " + elements.length);
	//console.log("Example Element: " + JSON.stringify(elements[3]));

	console.log("Translating Service Data For Cytoscape");
	console.log("   Nodes...");
	// restructure to meet the needs of cytoscape
	var cyElements = new Array();
	elements.forEach(function(element) {
		//console.log(element.type);
		var tempElement = new Object();
		tempElement.data = element;
		cyElements.push(tempElement);
	//	}
	});

	console.log("   Links...");
	var links = data.organisationDefinition.links;
	// restructure to meet the needs of cytoscape
	var cyLinks = new Array();
	links.forEach(function(element) {
		var tempElement = new Object();
		tempElement.data = element;
		cyLinks.push(tempElement);
		});

	console.log("Service Data Loaded, Creating  CytoScape Graph");

	var cy = cytoscape({
		elements: { 
			nodes: cyElements, 
			edges: cyLinks
			}
	});


	console.log("Outputing search optimised service document");
	//TODO: Use model or field to determine the dimensions we are interested in.

	
	
	serviceElements = cy.$("[type = '" + serviceNodeType + "']");
	
	console.log("Looking for: " + "[type = '" + serviceNodeType + "']" );
	console.log("Service Elements Found: " + serviceElements.size());
	var serviceDocument;
	var ancestors;
	var successors; 

	console.log('Starting Loop over services')
	
	serviceElements.forEach(function(service, i, eles) {
	console.time(service.data('name'));
		serviceDocument = {documentType : "ServiceInformation"};
		serviceDocument.service = service.data();
		ancestors = service.predecessors().nodes();
		serviceDocument.Dimension = new Array;
		//TODO: Add organisation information			
		//console.log("Ancestors Found: " + ancestors.size());
		ancestors.forEach(function(ele, i, eles) { 
			if (ele.isNode()) {
				var dijkstra = cy.elements().dijkstra(ele, directed=true);				
				var dist = dijkstra.distanceTo( service );
				serviceDocument.Dimension[i] = new Object;
				serviceDocument.Dimension[i].dist = dist;	 
				serviceDocument.Dimension[i].id = ele.id();	 
				serviceDocument.Dimension[i].name = ele.data( 'name');	 
				serviceDocument.Dimension[i].desc = ele.data( 'description');	 
				//TODO: Consider adding information from incomming link for each service - not required yet though
			}
		});

		serviceDocument.Component = new Array;

		successors = service.successors().nodes();
		successors.forEach(function(ele, i, eles) { 
			if (ele.isNode()) {
				serviceDocument.Component[i] = new Object;
				serviceDocument.Component[i].id  = ele.id();
				serviceDocument.Component[i].name = ele.data( 'name');
				serviceDocument.Component[i].desc = ele.data('description');
				//Add link information - requried for DHS atleast
			}
		});
				
		fs.writeFile(path.join(__dirname, orgname, service.id() + '(' + service.data('name')+ ').json'), JSON.stringify(serviceDocument, null, 2));
		console.timeEnd(service.data('name'));
	});












});
