import tasks
from mock import patch, MagicMock
from mock_django.models import ModelMock
from django.test import TestCase


class BasePageValidationTestCase(TestCase):
    def setUp(self):
        self.bad_pages = (
            {},{
                'orient_rid': '@eg42g24b',
                'orient_version': '12345',
                'orient_class': 'webDocumentContainer',
            },{
                'url':'http://swarmforge.net/',
                'orient_version': '12345',
                'orient_class': 'webDocumentContainer',
            },{
                'url':'http://swarmforge.net/',
                'orient_rid': '@eg42g24b',
                'orient_class': 'webDocumentContainer',
            },{
                'url':'http://swarmforge.net/',
                'orient_rid': '@eg42g24b',
                'orient_version': '12345',})
        self.good_page = {
            'url':'http://swarmforge.net/',
            'orient_rid': '@eg42g24b',
            'orient_version': '12345',
            'orient_class': 'webDocumentContainer',
        }
        # assumption!
        # version and rid always both change together
        self.good_page_dirty = {}
        for k in self.good_page:
            self.good_page_dirty[k] = self.good_page[k]
        self.good_page_dirty['orient_version'] = '12346'
        self.good_page_dirty['orient_rid'] = '@1abt2b346'


class InputValidationTestCase(BasePageValidationTestCase):
    '''
    ensure @shared_task functions guard agains invalid input
    '''
    def test_update_page_in_db(self):
        for p in self.bad_pages:
            with self.assertRaises(tasks.InvalidPageDataError):
                tasks.update_page_in_db(p)

    def test_insert_page_in_db(self):
        for p in self.bad_pages:
            with self.assertRaises(tasks.InvalidPageDataError):
                tasks.insert_page_in_db(p)

    def test_PageDictValdator(self):
        pvd = tasks.PageDictValidator()
        for p in (self.good_page, self.good_page_dirty):
            self.assertTrue(pvd.valid(p))
        for p in self.bad_pages:
            self.assertFalse(pvd.valid(p))

        for k in tasks.PageDictValidator.REQUIRED_PROPERTIES:
            p = self.good_page
            if k in p.keys():
                del p[k]
                self.assertFalse(pvd.valid(p))

    def test_sync_page_sinks(self):
        with self.assertRaises(tasks.InvalidPageIDError):
            tasks.sync_page_sinks('foo')


class DBCRUDTestCase(BasePageValidationTestCase):
    def test_db_updated_does_save_change(self):
        '''
        If the page already exists
        and has different data
        then update_page_in_db should call Page.save
        '''
        tasks.insert_page_in_db(self.good_page)
        with patch('spiderbucket.tasks.Page.save') as mock_save:
            tasks.update_page_in_db(self.good_page_dirty)
            self.assertTrue(mock_save.called)

    def test_db_insert_does_save_change(self):
        '''
        if the page does not already exist
        then insert_page_in_db should call Page.save
        '''
        with patch('spiderbucket.tasks.Page.save') as mock_save:
            tasks.insert_page_in_db(self.good_page)
            self.assertTrue(mock_save.called)

    def test_db_update_page_does_publish_changes(self):
        '''
        of update_page_in_db makes a change
        that change is dispatched to the sync_page_sinks
        '''
        tasks.insert_page_in_db(self.good_page)
        with patch('spiderbucket.tasks.sync_page_sinks.delay') as mock_sync:
            tasks.update_page_in_db(self.good_page_dirty)
            self.assertTrue(mock_sync.called)

    def test_db_insert_page_does_publish_changes(self):
        '''
        of insert_page_in_db makes a change
        that change is dispatched to the sync_page_sinks
        '''
        with patch('spiderbucket.tasks.sync_page_sinks.delay') as mock_sync:
            tasks.insert_page_in_db(self.good_page)
            self.assertTrue(mock_sync.called)


class PushPageDictTestCase(BasePageValidationTestCase):
    def test_input_guard(self):
        '''
        push_page_dict should guard against bad input
        '''
        for p in self.bad_pages:
            with self.assertRaises(tasks.InvalidPageDataError):
                tasks.push_page_dict(p)

    def test_update_existing(self):
        '''
        If page already exists in the db,
        push_page_dict should call update_page_in_db
        '''
        tasks.insert_page_in_db(self.good_page)
        update_method = 'spiderbucket.tasks.update_page_in_db.delay'
        with patch(update_method) as mock_update:
            tasks.push_page_dict(self.good_page_dirty)
            self.assertTrue(mock_update.called)

    def test_insert_new(self):
        '''
        If page does not exist in the db,
        push_page_dict should call insert_page_in_db
        '''
        insert_method = 'spiderbucket.tasks.insert_page_in_db.delay'
        with patch(insert_method) as mock_insert:
            tasks.push_page_dict(self.good_page)
            self.assertTrue(mock_insert.called)


class PageSyncSubscriberTestCase(BasePageValidationTestCase):
    def test_config_is_valid(self):
        '''
        PageSyncSubscriber should reference valid configuration
        '''
        pss = tasks.PageSyncSubscribers()
        task_type = type(tasks.sync_page_sinks)
        for c in pss.HARDCODED_CONFIG:
            keys = c.keys()
            self.assertIn('name', keys)
            self.assertIn('push', keys)
            self.assertIn('delete', keys)
            for k in keys:
                self.assertIn(k, ('name', 'push', 'delete'))

    def test_subscribers_purged(self):
        '''
        syncing a page that doesn't exist in the db
        should results in every subscribed delete task getting called
        '''
        pss = tasks.PageSyncSubscribers()
        mocks = []
        for t in pss.list_delete_task_names():
            patcher = patch("spiderbucket.tasks.%s.delay" % t)
            mocks.append(patcher.start())
        tasks.sync_page_sinks(1) # absent
        for m in mocks:
            self.assertTrue(m.called)

    def test_subscribers_pushed(self):
        '''
        syncing a page that exists in the db
        should result in every subscribed push task getting valled
        '''
        pss = tasks.PageSyncSubscribers()
        mocks = []
        for t in pss.list_push_task_names():
            patcher = patch("spiderbucket.tasks.%s.delay" % t)
            mocks.append(patcher.start())
        tasks.insert_page_in_db(self.good_page)
        tasks.sync_page_sinks(1) # PRESUMPTION !
        for m in mocks:
            self.assertTrue(m.called)


class SolrSyncTestCase(TestCase):
    # no longer required due to use of NulTask
    # and plan to adopt celery-haystack
    pass
