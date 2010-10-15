from fp.tests import *

class TestWindowController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='window', action='index'))
        # Test response...
