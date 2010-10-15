from fp.tests import *

class TestImageController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='image', action='index'))
        # Test response...
