#-*- coding: utf-8; -*-
from django.core.management.base import BaseCommand, CommandError
from spiderbucket import tasks
from django.conf import settings
from git import Repo
import git.remote
import os
import json
import govservices

class Command(BaseCommand):
    help = 'source service specification (json) from Github, then update the DB as required'

    def handle(self, *args, **options):
        #raise CommandError('Eek!')
        #
        # error if the repo doesn't exits
        repo_path = settings.SERVICE_CATALOGUE_REPOSITORY_PATH
        repo_remote = settings.SERVICE_CATALOGUE_REPOSITORY_REMOTE
        repo = Repo(repo_path)
        assert not repo.is_dirty()
        found = False
        for r in repo.remotes:
            if "%s" % r == repo_remote:
                found = True
                remote = r
        if not found:
            msg = "failed to find remote (%s) in repositorty (%s)"
            print msg % (repo_remote, repo_path)
            exit
        ### this hangs...
        #remote.pull(progress=rp)
        # fetch the repo, discover changes
        # exit if no changes
        # ### what to do if working in that repo? don't do that, use a dedicated one
        # ### which branch (new config var)
        #

        # OK, we have change to process
        # 1. load all of the json into RAM
        notagencies = ('lists', 'genService', '.git')
        agencies = {}
        for d in os.listdir(repo_path):
            agency_path = os.path.join(repo_path, d)
            if d not in notagencies and os.path.isdir(agency_path):
                agencies[d] = {}
                for f in os.listdir(agency_path):
                    name = os.path.join(agency_path, f)
                    if not os.path.isdir(name):
                        agencies[d][f] = json.loads(open(name).read())
        
        #
        # now we inspect it to design the ORM class
        #
        tld = []
        dim_keys = []
        services = []
        service_keys = []
        service_keys_count = {}
        service_keys_examples = {}
        service_types = [] # todo
        doctypes = []
        subservices=[]
        subservice_keys = []
        subservice_keys_count = {}
        subservice_examples = {}
        service_tags = []
        for ak in agencies.keys():
            for s in agencies[ak]:
                #
                for k in agencies[ak][s].keys():
                    if k not in tld:
                        tld.append(k)
                    if k == 'Subs':
                        # subs seem always empty?
                        if agencies[ak][s][k] != []:
                            msg = "DISCOVERY! (%s: %s: %s)"
                            print msg % (ak, s[:-5], agencies[ak][s][k])
                    elif k == 'todo':
                        pass  # not interesting
                    elif k == u'Dimension':
                        dim_list = agencies[ak][s][k]
                        for dim in dim_list:
                            for dk in dim.keys():
                                if dk not in dim_keys:
                                    dim_keys.append(dk)
                    if k == u'service':
                        srv = agencies[ak][s][k]
                        for sk in srv.keys():
                            if sk not in service_keys:
                                service_keys.append(sk)
                                service_keys_count[sk] = 1
                                service_keys_examples[sk] = srv[sk]
                            else:
                                service_keys_count[sk] += 1
                            if srv[sk] not in (None, [], ''):
                                try:
                                    service_keys_example[sk] = srv[sk]
                                except:
                                    pass
                            # service tags
                            if sk in ("tags", "tags:"):
                                for st in srv[sk]:
                                    if st not in service_tags:
                                        service_tags.append(st)
                    if k == u'documentType':
                        dt = agencies[ak][s][k]
                        if dt not in doctypes:
                            doctypes.append(dt)
                    if k == u'subService':
                        sss = agencies[ak][s][k]
                        if len(sss) > 0:
                            for ss in sss:
                                if ss not in subservices:
                                    subservices.append(ss)
                                    for k in ss.keys():
                                        if k not in subservice_keys:
                                            subservice_keys.append(k)
                                            subservice_keys_count[k]=1
                                            subservice_examples[k] = ss[k]
                                        else:
                                            subservice_keys_count[k] += 1
                                        if '%s' % ss[k] != '':
                                            subservice_examples[k] = ss[k]
        #
        # a. generate text analysis from json
        # b. generate dot, visualise...
        # c. generate Model.model subclasses
        # d. break it into separate commands
        # e. separate service catalogue app!
        # f. build script (bootstrap self from repo).
        # g. generate haystack index
        #
        print "top level: %s" % tld
        print ''
        # dimmension
        '''
        print "dim_keys: %s" % dim_keys
        print "dim example:"
        for dk in dim.keys():
            try:
                if len(dim[dk]) > 50:
                    dim[dk] = dim[dk][:50] + '...'
            except:
                pass
            print "  %s: %s" % (dk, dim[dk])
        print ''
        '''
        # service (analysis)
        print 'service_keys'
        print "service example:"
        for sk in service_keys:
            val = None
            #try:
            val = service_keys_examples[sk]
            if type(val) == type('') and len(val) > 50:
                val = val[:50] + '...' 
            #except:
            #    pass

            print "    %s (%s)" % (sk, service_keys_count[sk]),
            if val:
                print "type: %s, example: %s" % (type(val), val)
            else:
                print ''
        
        # service tags
        #
        # 2. load all of the DB records into RAM
        #
        # None vs. '' difference causing false mismatches (bug)
        # chomp None values (kludge)
        #
        # subservices
        #
        for ss in subservices:
            for k in ss.keys():
                if ss[k] is None:
                    del(ss[k])
        db_subservices = []
        for ss in govservices.models.SubService.objects.all():
            ss_dict = {
                'name': ss.name,
                'id': ss.cat_id,
                'desc': ss.desc,
                'infoUrl': ss.info_url,
                'primaryAudience': ss.primary_audience 
                }
            for k in ss_dict.keys():
                if ss_dict[k] is None:
                    del(ss_dict[k])
            db_subservices.append(ss_dict)
        #print "number of subservices found in the db: %s" % len(db_subservices)
        # service tags
        db_servicetags = []
        for st in govservices.models.ServiceTag.objects.all():
            db_servicetags.append(st.label)

        #3. for each element in json:
        for st in service_tags:
            found_in_db = False
            for st2 in db_servicetags:
                if st2 == st:
                    found_in_db = True
            if not found_in_db:
                govservices.models.ServiceTag(label=st).save()
        for st in db_servicetags:
            found_in_json = False
            for st2 in service_tags:
                if st2 == st:
                    found_in_json = True
            if not found_in_json:
                govservices.models.ServiceTag.objects.get(label=st).delete()

        for ss in subservices:
            # raise exception if we have two non-identical subservices
            num_matched = 0
            for ss2 in subservices:
                if ss2['id'] == ss['id']:
                    num_matched += 1
                    if ss2 != ss:
                        raise Exception, "json corpus contains non-identical specifications of the same subservice \n\n %s\n\n %s" % (ss, ss2)
            # end validation step
            found_in_db = False
            for dbss in db_subservices:
                if dbss['id'] == ss['id']:
                    found_in_db=True
                    num_match=0
                    for k in ('name', 'id', 'desc', 'infoUrl', 'primaryAudience'):
                        try:
                            if dbss[k] == ss[k]:
                                num_match += 1
                        except:
                            pass
                    if num_match == len(ss):
                        found_in_db_same = True
                    else:
                        found_in_db_same = False
            # if it's not in the DB then insert it
            if not found_in_db:
                gss = govservices.models.SubService(
                    cat_id=ss['id'],
                    desc=ss['desc'],
                    name=ss['name'])
                try:
                    gss.info_url=ss['infoUrl']
                except:
                    pass
                try:
                    gss.primary_audience=ss['primaryAudience']
                except:
                    pass
                gss.save()
            # if it's changed in the DB then update it
            if found_in_db and not found_in_db_same:
                u = govservices.models.SubService.objects.get(cat_id=ss['id'])
                u.desc = ss['desc']
                u.name=ss['name']
                try:
                    u.info_url=ss['infoUrl']
                except:
                    pass
                try:
                    u.primary_audience=ss['primaryAudience']
                except:
                    pass
                u.save()
        # 4. for each element in the DB:
        #        if it's not in the json:
        #            delete it from the DB
        for dbss in govservices.models.SubService.objects.all():
            found_in_json = False
            for ss in subservices:
                if ss['id'] == dbss.cat_id:
                    found_in_json = True
            if not found_in_json:
                dbss.delete()

if __name__ == "__main__":
    # test here now,
    # but move it to tests.py later
    pass
