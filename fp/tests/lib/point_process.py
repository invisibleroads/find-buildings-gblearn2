# Import system modules
import os
import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
# Import custom modules
from libraries import point_process


class Test(unittest.TestCase):

    def testPointMachine(self):
        points = [(x, y) for x in xrange(-3, 4) for y in xrange(-3, 4)]
        pointMachine = point_process.PointMachine(points, 'INTEGER')
        self.assertEqual(pointMachine.getPointsInsideFrame((-3, -3, 0, 0)), [(-3, -3), (-3, -2), (-3, -1), (-2, -3), (-2, -2), (-2, -1), (-1, -3), (-1, -2), (-1, -1)])


if __name__ == '__main__':
    unittest.main()
