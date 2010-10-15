# Import system modules
import sqlite3
import math
# Import custom modules
import point_store
import store


def extractBadLocations(geoDiameter, locations1, locations2):
    """Return locations from locations1 whose windows do not contain locations from locations2"""
    # Initialize
    badLocations = []
    # Make a pointMachine from locations2
    pointMachine = PointMachine(locations2, 'REAL', geoDiameter, geoDiameter)
    # For each location in locations1,
    for location in locations1:
        # If the window does not contain any points from locations2,
        if not pointMachine.getPointsInsideCenteredCircle(location):
            # Append point to badLocations
            badLocations.append(location)
    # Return
    return badLocations


def makePixelPointMachine(geoCenters, windowGeoLength, image):
    'Make a pixel-based point machine from geocoordinates'
    # Convert to pixels
    pixelCenters = image.convertGeoLocationsToPixelLocations(geoCenters)
    windowPixelWidth, windowPixelHeight = image.convertGeoDimensionsToPixelDimensions(windowGeoLength, windowGeoLength)
    # Return
    return PointMachine(pixelCenters, 'INTEGER', windowPixelWidth, windowPixelHeight)


class PointMachine(object):
    
    def __init__(self, points, dataType, windowWidth=None, windowHeight=None):
        # Set
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        # Connect
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()
        # Create table
        self.cursor.execute('CREATE TABLE points (x %s, y %s)' % (dataType, dataType))
        self.connection.commit()
        # Add points
        for point in points: 
            self.addPoint(point)

    def getWindowDimensions(self):
        return self.windowWidth, self.windowHeight

    @store.commit
    def addPoint(self, point):
        return 'INSERT INTO points (x, y) VALUES (?,?)', point

    # Count

    @store.fetchOne
    def count(self):
        return 'SELECT COUNT(*) FROM points', None, store.pullFirst

    # Get

    def getPointsInsideCenteredCircle(self, center):
        # Get points inside centered window
        points = self.getPointsInsideCenteredWindow(center)
        # Define
        diameter = min(self.windowWidth, self.windowHeight)
        isInsideCircle = lambda x: computeDistance(center, x) * 2 <= diameter
        # Return
        return filter(isInsideCircle, points)

    def getPointsInsideCenteredWindow(self, windowCenter):
        x, y = windowCenter
        windowLocation = x - self.windowWidth / 2, y - self.windowHeight / 2
        return self.getPointsInsideWindow(windowLocation)

    def getPointsInsideWindow(self, windowLocation):
        left, top = windowLocation
        right, bottom = left + self.windowWidth, top + self.windowHeight
        frame = left, top, right, bottom
        return self.getPointsInsideFrame(frame)

    @store.fetchAll
    def getPointsInsideFrame(self, frame):
        left, top, right, bottom = frame
        return 'SELECT x, y FROM points WHERE (x >= ? AND x < ?) AND (y >= ? AND y < ?)', (left, right, top, bottom)

    @store.fetchAll
    def getRandomPointsInsideFrame(self, frame, howMany):
        left, top, right, bottom = frame
        return 'SELECT x, y FROM points WHERE (x >= ? AND x < ?) AND (y >= ? AND y < ?) ORDER BY RANDOM() LIMIT %s' % howMany, (left, right, top, bottom)

    @store.fetchAll
    def getRandomPointsOutsideFrame(self, frame, howMany):
        left, top, right, bottom = frame
        return 'SELECT x, y FROM points WHERE NOT ((x >= ? AND x < ?) AND (y >= ? AND y < ?)) ORDER BY RANDOM() LIMIT %s' % howMany, (left, right, top, bottom)

    @store.fetchOne
    def getRandomPoint(self):
        return 'SELECT x, y FROM points ORDER BY RANDOM() LIMIT 1', None

    # Delete

    @store.commit
    def deletePointsInsideFrame(self, frame):
        left, top, right, bottom = frame
        return 'DELETE FROM POINTS WHERE (x >= ? AND x < ?) AND (y >= ? AND y < ?)', (left, right, top, bottom)

    @store.commit
    def deletePoint(self, point):
        return 'DELETE FROM POINTS WHERE x=? AND y=?', point


def isInsideRegion(point, frame):
    x, y = point[:2]
    left, top, right, bottom = frame
    isXBetween = left <= x and x < right
    isYBetween = top <= y and y < bottom
    return isXBetween and isYBetween


def computeDistance(point1, point2):
    return math.hypot((point1[0] - point2[0]), (point1[1] - point2[1]))
