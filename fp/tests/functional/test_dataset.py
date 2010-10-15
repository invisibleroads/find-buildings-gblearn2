from fp.tests import *

class TestDatasetController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='dataset', action='index'))
        # Test response...
