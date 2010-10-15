from fp.tests import *

class TestRegionController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='region', action='index'))
        # Test response...
