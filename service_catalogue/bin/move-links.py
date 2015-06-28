import json
json_data = open('/home/maxious/Downloads/DHS.json')
doc = json.load(json_data)
componentsMapping = {};
dimsMapping = {}
i = 0
for cmp in doc['organisationDefinition']['components']:
    componentsMapping[cmp['id']] = i
    i = i + 1
i = 0
for dim in doc['organisationDefinition']['serviceDimensions']:
    dimsMapping[dim['id']] = i
    i = i + 1
for link in doc['organisationDefinition']['links']:
    if 'source' in link:
        source = None
        print link
        if link['source'] == doc['organisationDefinition']['serviceOrganisation']['id']:
            source = doc['organisationDefinition']['serviceOrganisation']
        if link['source'] in componentsMapping:
            source = doc['organisationDefinition']['components'][componentsMapping[link['source']]]
        if link['source'] in dimsMapping:
            source = doc['organisationDefinition']['serviceDimensions'][dimsMapping[link['source']]]
        if source:

            del link['source']
            if 'links' not in source:
                source['links'] = []
            source['links'].append(link)

with open('/home/maxious/Downloads/DHS.json','w') as out:
    del doc['organisationDefinition']['links']
    json.dump(doc,out, sort_keys=True,
                                indent=4, separators=(',', ': '))