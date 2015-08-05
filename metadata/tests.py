import tasks
from mock import patch, MagicMock
from mock_django.models import ModelMock
from django.test import TestCase

class InsertResourceFromRowTestCase(TestCase):
    def test_new_resource_saved(self):
        dispatch = patch("django.db.connection.execute")
        dispatch.start() # stubbing patch
        with patch('metadata.tasks.Resource.save') as mock_save:
            tasks.insert_resource_from_row(['','','','','','','','',''])
            self.assertTrue(mock_save.called)
