from fp.tests import *

class TestScanController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='scan', action='index'))
        # Test response...
