# Import system modules
import itertools
# Import custom modules
import view


# Make

def makeWindowGenerator(multispectralImage, panchromaticImage, windowGeoLength, scanRatio, frame=None):
    # Convert windowGeoLength
    windowGeoDimensions = windowGeoLength, windowGeoLength
    multispectralWindowWidth, multispectralWindowHeight = multispectralImage.convertGeoDimensionsToPixelDimensions(*windowGeoDimensions)
    panchromaticWindowWidth, panchromaticWindowHeight = panchromaticImage.convertGeoDimensionsToPixelDimensions(*windowGeoDimensions)
    # Use frame
    maxRight = multispectralImage.width - multispectralWindowWidth
    maxBottom = multispectralImage.height - multispectralWindowHeight
    if frame:
        left, top, right, bottom = frame
        # Include overlap outside frame
        right = min(right, maxRight)
        bottom = min(bottom, maxBottom)
    else:
        left, top, right, bottom = 0, 0, maxRight, maxBottom
    # Make multispectralWindowLocations
    multispectralWindowLocations = [(x, y) for x in xrange(left, right, int(multispectralWindowWidth / scanRatio)) for y in xrange(top, bottom, int(multispectralWindowHeight / scanRatio))]
    # Make panchromaticWindowLocations
    windowGeoLocations = multispectralImage.convertPixelLocationsToGeoLocations(multispectralWindowLocations)
    panchromaticWindowLocations = panchromaticImage.convertGeoLocationsToPixelLocations(windowGeoLocations)
    # Count
    locationCount = len(windowGeoLocations)
    # For each window,
    for locationIndex, multispectralWindowLocation, panchromaticWindowLocation in itertools.izip(itertools.count(), multispectralWindowLocations, panchromaticWindowLocations):
        # Make window
        multispectralPack = multispectralImage, multispectralWindowLocation, (multispectralWindowWidth, multispectralWindowHeight)
        panchromaticPack = panchromaticImage, panchromaticWindowLocation, (panchromaticWindowWidth, panchromaticWindowHeight)
        yield Window(multispectralPack, panchromaticPack)
        # Show feedback
        if locationIndex % 10 == 0: view.printPercentUpdate(locationIndex + 1, locationCount)
    view.printPercentFinal(locationCount)


class Window(object):

    multispectralWindow = None
    panchromaticWindow = None

    def __init__(self, multispectralPack, panchromaticPack):
        self.multispectralImage, self.multispectralWindowLocation, self.multispectralWindowDimensions = multispectralPack
        self.panchromaticImage, self.panchromaticWindowLocation, self.panchromaticWindowDimensions = panchromaticPack

    def getMultispectralPixelFrame(self):
        # Get xs
        multispectralX1 = self.multispectralWindowLocation[0]
        multispectralX2 = self.multispectralWindowLocation[0] + self.multispectralWindowDimensions[0]
        # Get ys
        multispectralY1 = self.multispectralWindowLocation[1]
        multispectralY2 = self.multispectralWindowLocation[1] + self.multispectralWindowDimensions[1]
        # Sort
        left, right = sorted((multispectralX1, multispectralX2))
        top, bottom = sorted((multispectralY1, multispectralY2))
        # Return
        return left, top, right, bottom

    def extractImage(self):
        if not self.multispectralWindow: self.multispectralWindow = self.multispectralImage.extractPixelWindow(self.multispectralWindowLocation, *self.multispectralWindowDimensions)
        if not self.panchromaticWindow: self.panchromaticWindow = self.panchromaticImage.extractPixelWindow(self.panchromaticWindowLocation, *self.panchromaticWindowDimensions)
        return self.multispectralWindow, self.panchromaticWindow
