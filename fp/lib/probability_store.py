# Import system modules
import os
# Import custom modules
import parameter_store
import image_store
import point_store, point_process
import region_store
import store


def load(probabilityPath, withNegative=True):
    # Open
    probabilityFile = open(probabilityPath, 'rt')
    # Initialize
    probabilityPacks = []
    # For each line,
    for line in probabilityFile:
        # Extract fields
        fields = line.split()
        # Return if we find a line that doesn't have four fields
        if len(fields) != 4: 
            return probabilityPacks
        # Convert fields
        x = int(fields[0])
        y = int(fields[1])
        label = int(fields[2])
        probability = float(fields[3])
        # Skip negative labels if the user doesn't want them
        if label == 0 and not withNegative: 
            continue
        # Append
        probabilityPacks.append((x, y, label, probability))
    # Close
    probabilityFile.close()
    # Return
    return probabilityPacks


def loadPredictedPixelCenters(probabilityPath, windowPixelDimensions):
    # Load predictedWindowLocations
    predictedWindowLocations = [x[:2] for x in load(probabilityPath, withNegative=False)]
    # Return predictedPixelCenters
    return [image_store.getWindowCenter(x, *windowPixelDimensions) for x in predictedWindowLocations]


def saveShapefile(targetPath, sourceProbabilityPath, multispectralImage, windowLengthInMeters):
    # Get pixelDimensions
    windowPixelWidth, windowPixelHeight = multispectralImage.convertGeoDimensionsToPixelDimensions(windowLengthInMeters, windowLengthInMeters)
    # Load positiveProbabilityPacks
    positiveProbabilityPacks = load(sourceProbabilityPath, withNegative=False)
    # Center
    positivePixelCenters = [(x[0] + windowPixelWidth / 2, x[1] + windowPixelHeight / 2) for x in positiveProbabilityPacks]
    # Convert
    positiveGeoCenters = multispectralImage.convertPixelLocationsToGeoLocations(positivePixelCenters)
    # Save
    point_store.save(targetPath, positiveGeoCenters, multispectralImage.getSpatialReference())


class Information(store.Information):

    def __init__(self, informationPath):
        super(Information, self).__init__(informationPath)
        self.imageInformation = image_store.Information(self.expandPath(self.getImagePath()))

    def getImagePack(self):
        return self.imageInformation.getMultispectralImage(), self.imageInformation.getPanchromaticImage()

    def hasPerformance(self):
        return 'performance' in self.information

    def getImageName(self):
        return self.information['probability']['image name']

    def getImagePath(self):
        return self.information['probability']['image path']

    def getRegionPath(self):
        return self.information['probability']['region path']

    def getClassifierPath(self):
        return self.information['classifier']['path']

    @parameter_store.convert
    def getScanRatio(self):
        return 'scan ratio'

    @parameter_store.convert
    def getWindowLengthInMeters(self):
        return 'window length in meters'

    def hasRegionName(self):
        return 'region name' in self.information['probability']

    def getPackage(self):
        # Get
        windowGeoLength = self.getWindowLengthInMeters()
        multispectralImage, panchromaticImage = self.getImagePack()
        actualLocationPath = self.expandPath(self.imageInformation.getPositiveLocationPath())
        windowPixelDimensions = multispectralImage.convertGeoDimensionsToPixelDimensions(windowGeoLength, windowGeoLength)
        # Filter actual locations by scanned regions
        actualGeoLocations = point_store.load(actualLocationPath)[0]
        actualPointMachine = point_process.PointMachine(actualGeoLocations, 'REAL')
        filteredGeoLocations = set()
        for multispectralPixelFrame in region_store.load(self.getRegionPath()).getRegionFrames():
            geoFrame = multispectralImage.convertPixelFrameToGeoFrame(multispectralPixelFrame)
            filteredGeoLocations.update(actualPointMachine.getPointsInsideFrame(geoFrame))
        # Return
        return multispectralImage, panchromaticImage, filteredGeoLocations, windowPixelDimensions
