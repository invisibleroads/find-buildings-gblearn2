from fp.tests import *

class TestLocationController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='location', action='index'))
        # Test response...
