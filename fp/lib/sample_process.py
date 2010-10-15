# Import system modules
import itertools
import random
import os
# Import custom modules
import view
import store
import point_store, point_process
import sample_store
import image_store


# Define core

def extractDataset(targetDatasetPath, paths, parameters):
    # Unpack
    multispectralImagePath, panchromaticImagePath, positiveLocationPath = paths
    windowGeoLength, negativeRatio, multispectralPixelShiftValue, shiftCount = parameters
    # Show feedback
    view.sendFeedback('Extracting dataset...\n\ttargetDatasetPath = %s' % targetDatasetPath)
    # Extract samples
    extractor = Extractor(targetDatasetPath, windowGeoLength, multispectralPixelShiftValue, shiftCount, negativeRatio)
    extractor.extractSamples(positiveLocationPath, multispectralImagePath, panchromaticImagePath)
    # Record
    targetDataset = extractor.getSampleDatabase()
    multispectralImage = image_store.load(multispectralImagePath)
    panchromaticImage = image_store.load(panchromaticImagePath)
    points, spatialReference = point_store.load(positiveLocationPath)
    store.saveInformation(targetDatasetPath, {
        'multispectral image': {
            'path': multispectralImagePath,
            'pixel width': multispectralImage.getPixelWidth(),
            'pixel height': multispectralImage.getPixelHeight(),
            'geo transform': multispectralImage.getGeoTransform(),
        },
        'panchromatic image': {
            'path': panchromaticImagePath,
            'pixel width': panchromaticImage.getPixelWidth(),
            'pixel height': panchromaticImage.getPixelHeight(),
            'geo transform': panchromaticImage.getGeoTransform(),
        },
        'positive location': {
            'path': positiveLocationPath,
            'location count': len(points),
            'spatial reference': spatialReference,
        },
        'windows': {
            'path': targetDatasetPath,
            'sample count': targetDataset.countSamples(),
            'positive sample count': targetDataset.countPositiveSamples(),
            'negative sample count': targetDataset.countNegativeSamples(),
        },
        'parameters': {
            'window geo length': windowGeoLength,
            'multispectral pixel shift value': multispectralPixelShiftValue,
            'shift count': shiftCount,
            'negative ratio': negativeRatio,
        }
    })
    # Return
    return targetDataset

def combineDatasets(targetDatasetPath, datasetPaths, datasetSize=None, positiveFraction=None):
    # If positiveFraction is defined,
    if positiveFraction:
        # Get
        positiveSamplePacks = []
        negativeSamplePacks = []
        for dataset in itertools.imap(sample_store.load, datasetPaths):
            positiveSamplePacks.extend((dataset, x) for x in dataset.getPositiveSampleIDs())
            negativeSamplePacks.extend((dataset, x) for x in dataset.getNegativeSampleIDs())
        # Shuffle
        random.shuffle(positiveSamplePacks)
        random.shuffle(negativeSamplePacks)
        # Count
        totalPositiveCount = len(positiveSamplePacks)
        totalNegativeCount = len(negativeSamplePacks)
        # Chop
        # if positiveFraction >= 0.5:
        multiplier = (1 - positiveFraction) / positiveFraction
        scaledNegativeCount = int(multiplier * totalPositiveCount)
        datasetSampleIDs = positiveSamplePacks + negativeSamplePacks[:scaledNegativeCount]
        # else:
            # multiplier = positiveFraction / (1 - positiveFraction)
            # scaledPositiveCount = int(multiplier * totalNegativeCount)
            # datasetSampleIDs = positiveSamplePacks[:scaledPositiveCount] + negativeSamplePacks
    # If positiveFraction is not defined,
    else:
        # Get sampleIDs
        datasetSampleIDs = []
        for dataset in itertools.imap(sample_store.load, datasetPaths):
            datasetSampleIDs.extend((dataset, x) for x in dataset.getSampleIDs())
    # Shuffle
    random.shuffle(datasetSampleIDs)
    # Subset
    selectedDatasetSampleIDs = datasetSampleIDs[:datasetSize] if datasetSize else datasetSampleIDs
    view.sendFeedback('Making dataset with %d samples...' % len(selectedDatasetSampleIDs))
    return sample_store.save(targetDatasetPath, selectedDatasetSampleIDs)


# Define tools

class Extractor(object):

    # Constructor

    def __init__(self, sampleDatabasePath, windowGeoLength, multispectralPixelShiftValue, shiftCount, negativeRatio):
        self.sampleDatabase = sample_store.create(sampleDatabasePath)
        self.windowGeoDimensions = windowGeoLength, windowGeoLength
        self.multispectralPixelShiftValue = multispectralPixelShiftValue
        self.shiftCount = shiftCount
        self.negativeRatio = negativeRatio

    # Core

    def getSampleDatabase(self):
        return self.sampleDatabase

    def extractSamples(self, positiveLocationPath, multispectralImagePath, panchromaticImagePath):
        view.sendFeedback('Loading images...\n\tmultispectralImagePath = %s\n\tpanchromaticImagePath = %s' % (multispectralImagePath, panchromaticImagePath))
        multispectralImage = image_store.load(multispectralImagePath)
        panchromaticImage = image_store.load(panchromaticImagePath)
        view.sendFeedback('Generating geoCenters...\n\tmultispectralPixelShiftValue = %s\n\tshiftCount = %s\n\tnegativeRatio = %s' % (self.multispectralPixelShiftValue, self.shiftCount, self.negativeRatio))
        positiveMultispectralPixelCenters = self.loadPixelCenters(multispectralImage, positiveLocationPath)
        negativeMultispectralPixelCenters = self.makePixelCenters(multispectralImage, positiveMultispectralPixelCenters)
        positiveGeoCenters = multispectralImage.convertPixelLocationsToGeoLocations(positiveMultispectralPixelCenters)
        negativeGeoCenters = multispectralImage.convertPixelLocationsToGeoLocations(negativeMultispectralPixelCenters)
        view.sendFeedback('Extracting positive samples...')
        self.extract(1, positiveGeoCenters, multispectralImage, panchromaticImage)
        view.sendFeedback('Extracting negative samples...')
        self.extract(0, negativeGeoCenters, multispectralImage, panchromaticImage)

    def extract(self, hasRoof, geoCenters, multispectralImage, panchromaticImage):
        # Initialize
        windowCount = len(geoCenters)
        # For each geoCenter,
        for windowIndex, geoCenter in enumerate(geoCenters):
            window = [x.extractCenteredGeoWindow(geoCenter, *self.windowGeoDimensions) for x in multispectralImage, panchromaticImage]
            if window[0] and window[1]: self.sampleDatabase.addSample(hasRoof, geoCenter, *window)
            if windowIndex % 100 == 0: 
                view.printPercentUpdate(windowIndex + 1, windowCount)
        view.printPercentFinal(windowCount)

    # Define helpers

    def loadPixelCenters(self, image, shapePath):
        originalGeoLocations = point_store.load(shapePath)[0]
        originalPixelLocations = image.convertGeoLocationsToPixelLocations(originalGeoLocations)
        return shiftCopyPoints(originalPixelLocations, self.multispectralPixelShiftValue, self.shiftCount)

    def makePixelCenters(self, image, positivePixelCenters):
        negativeCount = int(len(positivePixelCenters) * self.negativeRatio)
        canvasPixelDimensions = image.width, image.height
        windowPixelDimensions = image.convertGeoDimensionsToPixelDimensions(*self.windowGeoDimensions)
        centerMachine = CenterMachine(canvasPixelDimensions, windowPixelDimensions)
        return centerMachine.makeCenters(positivePixelCenters, negativeCount)


class CenterMachine(object):

    def __init__(self, canvasFrame, windowDimensions, badCenters=None, badFrames=None):
        # Set
        if not badCenters: badCenters = []
        if not badFrames: badFrames = []
        self.windowDimensions = windowDimensions
        # Extract
        windowWidth, windowHeight = windowDimensions
        left, top, right, bottom = canvasFrame
        # Bound possible centers
        minX, minY = image_store.getCenter((left, top, left + windowWidth, top + windowHeight))
        maxX, maxY = image_store.getCenter((right - windowWidth, bottom - windowHeight, right, bottom))
        centerFrame = minX, minY, maxX + 1, maxY + 1
        # Mark
        self.badFrames = set()
        self.eligibleCenters = image_store.getPixelsInFrame(centerFrame)
        for badCenter in badCenters: 
            self.markBadCenter(badCenter)
        for badFrame in badFrames:
            self.markBadFrame(badFrame)

    def makeCenters(self, howMany):
        # While we need more centers,
        centers = []
        while self.eligibleCenters and len(centers) < howMany:
            # Get new center
            center = random.choice(self.eligibleCenters)
            centerFrame = image_store.centerPixelFrame(center, *self.windowDimensions)
            # If the center is good,
            if self.isGoodFrame(centerFrame):
                # Append
                centers.append(center)
                # Mark
                self.markBadFrame(centerFrame)
            # Remove
            self.eligibleCenters.remove(center)
        # Return
        return centers

    def isGoodFrame(self, frame):
        # Extract
        left, top, right, bottom = frame
        # For each badFrame,
        for badFrame in self.badFrames:
            # Extract
            badLeft, badTop, badRight, badBottom = badFrame
            # Test
            isLeftBetween = (badLeft <= left) and (left < badRight)
            isTopBetween = (badTop <= top) and (top < badBottom)
            isRightBetween = (badLeft < right) and (right <= badRight)
            isBottomBetween = (badTop < bottom) and (bottom <= badBottom)
            # If there is overlap, then the frame is bad
            if isLeftBetween:
                if isTopBetween or isBottomBetween: return False
            elif isRightBetween:
                if isTopBetween or isBottomBetween: return False
        return True

    def markBadCenter(self, center):
        self.markBadFrame(image_store.centerPixelFrame(center, *self.windowDimensions))

    def markBadFrame(self, frame):
        self.badFrames.add(frame)


# Define helpers

def shiftPoints(originalPoints, shiftValue, shiftCount):
    # Uses shiftCopyPoints and removes originals to prevent duplicates
    return shiftCopyPoints(originalPoints, shiftValue, shiftCount) - set(originalPoints)

def shiftCopyPoints(originalPoints, shiftValue, shiftCount):
    points = set(originalPoints)
    shiftDirections = permutePairwiseShifts(shiftValue)
    for point in originalPoints:
        for shift in random.sample(shiftDirections, shiftCount):
            points.add((point[0] + shift[0], point[1] + shift[1]))
    return points

def permutePairwiseShifts(shiftValue):
    values = -shiftValue, 0, shiftValue
    pairs = [(x, y) for x in values for y in values]
    pairs.remove((0, 0))
    return pairs

def makeTrainingPath(folderPath):
    return os.path.join(folderPath, 'training')

def makeTestPath(folderPath):
    return os.path.join(folderPath, 'test')
