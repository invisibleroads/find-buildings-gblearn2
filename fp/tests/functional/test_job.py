from fp.tests import *

class TestJobController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='job', action='index'))
        # Test response...
