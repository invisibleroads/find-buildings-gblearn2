from fp.tests import *

class TestClassifierController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='classifier', action='index'))
        # Test response...
