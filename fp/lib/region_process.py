# Import system modules
import random
import numpy
import math
# Import custom modules
import point_process
import sample_process


# Core

class ExampleMachine(object):

    'Places positive and negative examples in a frame'

    def __init__(self, positivePixels, exampleCountPerRegion, testFractionPerRegion, testRegionDataset, windowPixelDimensions, pixelShiftValue, shiftCount):
        # Set positivePixelMachine
        self.positivePixelMachine = point_process.PointMachine(positivePixels, 'INTEGER')
        # Set fractions
        self.testFractionPerLength = numpy.sqrt(testFractionPerRegion)
        # Set counts
        self.testCountPerRegion = int(math.ceil(exampleCountPerRegion * testFractionPerRegion))
        self.trainingCountPerRegion = exampleCountPerRegion - self.testCountPerRegion
        # Set
        self.windowPixelDimensions = windowPixelDimensions
        self.pixelShiftValue = pixelShiftValue
        self.shiftCount = shiftCount
        self.testRegionDataset = testRegionDataset

    def placeInFrame(self, regionFrame):
        # Get testRegionFrame
        testRegionFrame = self.testRegionDataset.getFrameInsideFrame(regionFrame)
        # Get positive locations in region
        regionalPositives = self.positivePixelMachine.getPointsInsideFrame(regionFrame)
        regionalPositivePixelMachine = point_process.PointMachine(regionalPositives, 'INTEGER')
        # Get positive locations
        trainingPositives = regionalPositivePixelMachine.getRandomPointsOutsideFrame(testRegionFrame, 
            self.trainingCountPerRegion)
        trainingPositiveShifteds = list(sample_process.shiftPoints(trainingPositives, 
            self.pixelShiftValue, self.shiftCount))
        testPositives = regionalPositivePixelMachine.getRandomPointsInsideFrame(testRegionFrame, 
            self.testCountPerRegion)
        testPositiveShifteds = list(sample_process.shiftPoints(testPositives, 
            self.pixelShiftValue, self.shiftCount))
        # Get negative locations in training region
        trainingNegativeCenterMachine = sample_process.CenterMachine(regionFrame, 
            self.windowPixelDimensions, 
            badCenters=trainingPositives+trainingPositiveShifteds,
            badFrames=[testRegionFrame])
        trainingNegativeCount = self.trainingCountPerRegion - len(trainingPositives)
        trainingNegatives = trainingNegativeCenterMachine.makeCenters(trainingNegativeCount)
        # Get negative locations in test region
        testNegativeCenterMachine = sample_process.CenterMachine(testRegionFrame, 
            self.windowPixelDimensions,
            badCenters=testPositives+testPositiveShifteds)
        testNegativeCount = self.testCountPerRegion - len(testPositives)
        testNegatives = testNegativeCenterMachine.makeCenters(testNegativeCount)
        # Return
        return {
            'training_positive': trainingPositives,
            'training_positive_shifted': trainingPositiveShifteds,
            'training_negative': trainingNegatives,
            'test_positive': testPositives,
            'test_positive_shifted': testPositiveShifteds,
            'test_negative': testNegatives,
        }

def placeTestRegion(regionFrame, testFractionPerRegion):
    # Unpack
    multispectralLeft, multispectralTop, multispectralRight, multispectralBottom = regionFrame
    testFractionPerLength = numpy.sqrt(testFractionPerRegion)
    # Get dimensions
    width = multispectralRight - multispectralLeft
    widthCut = testFractionPerLength * width
    height = multispectralBottom - multispectralTop
    heightCut = testFractionPerLength * height
    # Pick quadrant
    whichQuadrant = random.choice(xrange(4))
    # Lower left
    if whichQuadrant == 0:
        testMultispectralLeft = multispectralLeft
        testMultispectralTop = multispectralTop + heightCut
    # Upper left
    elif whichQuadrant == 1:
        testMultispectralLeft = multispectralLeft
        testMultispectralTop = multispectralTop
    # Upper right
    elif whichQuadrant == 2:
        testMultispectralLeft = multispectralLeft + widthCut
        testMultispectralTop = multispectralTop
    # Lower right
    elif whichQuadrant == 3:
        testMultispectralLeft = multispectralLeft + widthCut
        testMultispectralTop = multispectralTop + heightCut
    # Pack
    testRegionFrame = testMultispectralLeft, testMultispectralTop, testMultispectralLeft + widthCut, testMultispectralTop + heightCut
    # Return
    return testRegionFrame
