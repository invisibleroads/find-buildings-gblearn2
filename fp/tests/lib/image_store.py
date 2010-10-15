# Import system modules
import os
import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
# Import custom modules
from libraries import image_store


class Test(unittest.TestCase):

    def testCenterPixelFrame(self):
        self.assertEqual(image_store.centerPixelFrame((1, 1), 3, 3), (0, 0, 3, 3))
        self.assertEqual(image_store.centerPixelFrame((2, 2), 4, 4), (0, 0, 4, 4))

    def testGetCenter(self):
        self.assertEqual(image_store.getCenter((0, 0, 3, 3)), (1, 1))
        self.assertEqual(image_store.getCenter((0, 0, 4, 4)), (2, 2))


if __name__ == '__main__':
    unittest.main()
