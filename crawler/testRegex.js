//TODO Migrate to a testing library

var hosts = [
    "humanservices.gov.au",
    "environment.gov.au",
    "ramint.gov.au",
    "nfsa.gov.au",
    "sa.gov.au",
    "vic.gov.au",
    "www.vic.gov.au",
    "something.qld.gov.au",
    "www.something.wa.gov.au",
    "something.wa.gov.au",
    "nt.gov.au",
]
var stateSubDomain = /(^|\.)vic\.gov\.au$|(^|\.)nsw\.gov\.au$|(^|\.)qld\.gov\.au$|(^|\.)tas\.gov\.au$|(^|\.)act\.gov\.au$|(^|\.)sa\.gov\.au$|(^|\.)wa\.gov\.au$|(^|\.)nt\.gov\.au$/;
//var stateDomain = /^vic\.gov\.au$|^nsw\.gov\.au$|^qld\.gov\.au$|^tas\.gov\.au$|^act\.gov\.au$|^sa\.gov\.au$|^wa\.gov\.au$|^nt\.gov\.au$/;

hosts.forEach(function(host) {

    console.log("Host: " + host + "\t Outcome: " + (host.search(stateSubDomain) < 0));
    //      	console.log("Host: " + host + "\t Domain Outcome: " + (host.search(stateDomain) <0 ) + "\n");
});
