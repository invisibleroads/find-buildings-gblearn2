# Import system modules
import os
import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import tempfile
# Import custom modules
from libraries import region_store, store


class Test(unittest.TestCase):

    def setUp(self):
        self.regionStore = region_store.Store(tempfile.mkstemp(suffix='db')[1])

    def tearDown(self):
        store.removeSafely(self.regionStore.getPath())

    def testGetFrameInsideFrame(self):
        self.regionStore.addFrame((10, 10, 20, 20))
        self.regionStore.addFrame((20, 20, 30, 30))
        self.assertEqual(self.regionStore.getFrameInsideFrame((0, 0, 25, 25)), (10, 10, 20, 20))


if __name__ == '__main__':
    unittest.main()
