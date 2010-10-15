# Import system modules
import os
import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
# Import custom modules
from libraries import sample_process, image_store


class Test(unittest.TestCase):

    def testCenterMachine(self):
        # Initialize
        windowDimensions = 3, 3
        canvasFrame = -10, -10, 11, 11
        badFrame = -10, -10, 0, 0
        centerMachine = sample_process.CenterMachine(canvasFrame, windowDimensions, badFrames=[badFrame])
        centers = centerMachine.makeCenters(10000)
        frames = [image_store.centerPixelFrame(x, *windowDimensions) for x in centers]
        # Make sure that none of the good frames overlap each other
        groups_good = [set((x, y) for x in xrange(left, right) for y in xrange(top, bottom)) for left, top, right, bottom in frames]
        overlap = reduce(lambda x, y: x.intersection(y), groups_good)
        self.assertEqual(overlap, set())
        # Make sure that none of the good frames overlap bad frames
        points_bad = [(x, y) for x in xrange(badFrame[0], badFrame[2]) for y in xrange(badFrame[1], badFrame[3])]
        points_good = reduce(lambda x, y: x.union(y), groups_good)
        self.assertEqual(set(points_good).intersection(set(points_bad)), set())


if __name__ == '__main__':
    unittest.main()
