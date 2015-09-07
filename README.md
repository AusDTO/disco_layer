#Overview

The AusDTO Discovery Layer is infrastructure in support of the aim outlined here:

https://www.dto.gov.au/blog/making-government-discoverable

It is at "Proof Of Concept" status (ALPHA), meaning it aims to address technical risks (answer the question "could that work?") rather than evaluate product-market fit (BETA status) or provide a reliable public service (PRODUCTION status).

More information:
 * http://ausdto-discovery-layer.readthedocs.org (documentation)
 * https://github.com/AusDTO/discoveryLayer (code)
 * https://github.com/AusDTO/discoveryLayer/issues (tickets, support)
 * http://waffle.io/AusDTO/discoveryLayer (kanban) 


Note also this depends on the https://github.com/AusDTO/discoCrawl and https://github.com/AusDTO/serviceCatalogue components. This is explained in more detail in the documentation at http://ausdto-discovery-layer.readthedocs.org/


## install

pre-requsites (ubuntu packages):
 * python-dev
 * python-pip
 * libpq-dev
 * python-virtualenv

Then

   virtualenv .venv
   . .venv/bin/activate
   pip install -r requirements.txt

