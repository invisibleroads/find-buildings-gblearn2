# Import system modules
import sqlite3
import os
import re
# Import custom modules
import store
import folder_store
import parameter_store
import geometry_store
import image_process
import sequence


def makeRegionGenerator(multispectralImage, panchromaticImage, regionLengthInWindows, windowLengthInMeters):
    return image_process.makeWindowGenerator(multispectralImage, panchromaticImage, regionLengthInWindows * windowLengthInMeters, 1)


# Shortcuts

def create(datasetPath):
    datasetPath = store.replaceFileExtension(datasetPath, 'db')
    if os.path.exists(datasetPath): os.remove(datasetPath)
    return Store(datasetPath)

def load(datasetPath):
    datasetPath = store.replaceFileExtension(datasetPath, 'db')
    if not os.path.exists(datasetPath): raise IOError('Dataset does not exist: ' + datasetPath)
    return Store(datasetPath)

def getMultispectralPixelFrame(region):
    if isinstance(region, image_process.Window):
        return region.getMultispectralPixelFrame() 
    else:
        return region


# Save

def save(regionPath, regions):
    """
    Save regions into an SQLite database.  Regions can be frame tuples or 
    instances of the sample_process.Window class.
    """
    regionStore = Store(regionPath)
    for region in regions:
        regionStore.addRegion(region)
    return regionStore

def saveViaGenerator(regionPath, regionGenerator):
    regionStore = Store(regionPath)
    for region in regionGenerator:
        regionStore.addRegion(region)
    return regionStore


# Shapefile

def saveShapefile(targetPath, regionFrames, multispectralImage, withPixelToGeoConversion=True):
    # Get spatial reference
    spatialReference = multispectralImage.getSpatialReference()
    # Define
    def convertToWktGeometry(frame):
        # Unpack
        left, top, right, bottom = frame
        polygon = (left, top), (right, top), (right, bottom), (left, bottom)
        # Convert
        if withPixelToGeoConversion:
            polygon = multispectralImage.convertPixelLocationsToGeoLocations(polygon)
        # Return
        return 'POLYGON ((%s))' % ', '.join('%s %s' % x for x in polygon)
    # Set wktGeometries
    wktGeometries = map(convertToWktGeometry, regionFrames)
    # Save
    geometry_store.save(store.replaceFileExtension(targetPath, 'shp'), spatialReference, wktGeometries)

def loadShapefile(shapePath, multispectralImage, withGeoToPixelConversion=True):
    # Get wktGeometries
    spatialReference, wktGeometries = geometry_store.load(shapePath)[:2]
    # Make sure spatialReferences match
    # if spatialReference != multispectralImage.getSpatialReference():
        # raise IOError('Spatial references do not match:\n\t%s\n\t%s' % (shapePath, multispectralImage.getPath()))
    # Define
    pattern_polygon = re.compile(r'POLYGON \(\((.*)\)\)')
    def convertFromWktGeometry(wktGeometry):
        # Parse geoPolygon
        string = pattern_polygon.match(wktGeometry).group(1)
        polygon = [[float(x) for x in line.split()] for line in string.split(',')]
        # Make sure there are exactly four points
        # if len(polygon) != 4:
            # raise IOError('Each polygon must have exactly four points: %s' % shapePath)
        # Convert
        if withGeoToPixelConversion:
            polygon = multispectralImage.convertGeoLocationsToPixelLocations(polygon)
        # Unpack
        (left1, top1), (right1, top2), (right2, bottom1), (left2, bottom2) = polygon[:4]
        left = min(left1, left2)
        right = max(right1, right2)
        top = min(top1, top2)
        bottom = max(bottom1, bottom2)
        # Return
        return min(left, right), min(top, bottom), max(left, right), max(top, bottom)
    # Return
    return map(convertFromWktGeometry, wktGeometries)


class Store(object):

    # Constructor

    def __init__(self, datasetPath):
        # Fix extension
        datasetPath = store.replaceFileExtension(datasetPath, 'db')
        # Check whether the dataset exists
        flag_exists = True if os.path.exists(datasetPath) else False
        # Connect
        self.connection = sqlite3.connect(datasetPath)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        # If the dataset doesn't exist, create it
        if not flag_exists: 
            self.cursor.execute('CREATE TABLE regions (multispectralLeft INTEGER, multispectralTop INTEGER, multispectralRight INTEGER, multispectralBottom INTEGER)')
            self.connection.commit()
        # Remember
        self.datasetPath = datasetPath
    
    # Destructor

    def __del__(self):
        self.connection.close()

    # Add

    def addRegion(self, region):
        return self.addFrame(getMultispectralPixelFrame(region))

    @store.commit
    def addFrame(self, multispectralPixelFrame):
        return 'INSERT INTO regions (multispectralLeft, multispectralTop, multispectralRight, multispectralBottom) VALUES (?,?,?,?)', multispectralPixelFrame

    # Count

    @store.fetchOne
    def count(self):
        return 'SELECT COUNT(*) FROM regions', None, store.pullFirst

    # Get

    @store.fetchAll
    def getRegionIDs(self):
        return 'SELECT rowid FROM regions', None, store.pullFirst

    @store.fetchAll
    def getRegionFrames(self):
        return 'SELECT multispectralLeft, multispectralTop, multispectralRight, multispectralBottom FROM regions', None

    @store.fetchOne
    def getFrameInsideFrame(self, frame):
        left, top, right, bottom = frame
        return 'SELECT multispectralLeft, multispectralTop, multispectralRight, multispectralBottom FROM regions WHERE (multispectralLeft >= ? AND multispectralLeft < ?) AND (multispectralTop >= ? AND multispectralTop < ?) AND (multispectralRight > ? AND multispectralRight <= ?) AND (multispectralBottom > ? AND multispectralBottom <= ?)', (left, right, top, bottom, left, right, top, bottom)

    def getPath(self):
        return self.datasetPath

    # Cut

    def cutIDs(self, testFraction, withRandomization=True):
        # For each cut,
        for cutPack in sequence.cut(self.getRegionIDs(), testFraction, withRandomization):
            # Yield
            yield cutPack

    # Save
    
    def saveShapefile(self, targetPath, multispectralImage):
        return saveShapefile(targetPath, self.getRegionFrames(), multispectralImage)


class Information(object):

    # Constructor

    def __init__(self, informationPath):
        self.informationPath = informationPath
        self.information = store.loadInformation(informationPath)
        self.parameterByName = self.information['parameters']

    def getRegionDataset(self):
        return load(self.informationPath)

    def getTestRegionPath(self):
        return self.information['test regions']['path']

    def getTestRegionDataset(self):
        return load(self.getTestRegionPath())

    @parameter_store.convert
    def getImageName(self):
        return 'image name'

    @parameter_store.convert
    def getWindowLengthInMeters(self):
        return 'window length in meters'

    @parameter_store.convert
    def getRegionLengthInWindows(self):
        return 'region length in windows'

    @parameter_store.convert
    def getTestFractionPerRegion(self):
        return 'test fraction per region'
