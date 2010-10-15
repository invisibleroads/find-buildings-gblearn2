# Import system modules
import os
import re
import glob
import itertools
# Import custom modules
import store


# Core

class Store(object):

    def __init__(self, basePath='.'):
        # Make the folder if it doesn't exist
        self.basePath = store.makeFolderSafely(basePath)
        # Set folderPathByName
        self.folderPathByName = dict((key, os.path.join(basePath, folderNameByName[key])) for key in folderNameByName)

    # Fill

    def fillPath(self, baseFolderName, folderName):
        # Make sure that folderName is valid
        match = pattern_name.match(folderName)
        if not match: 
            explanation = 'Names can have letters, digits, underscores, hyphens, spaces, parentheses, commas and periods.'
            raise FolderError('Invalid name: %s\n%s' % (folderName, explanation))
        # Fill path
        baseFolderPath = store.makeFolderSafely(self.folderPathByName[baseFolderName])
        template = templateByFolderName[baseFolderName]
        fileName = fileNameByFolderName[baseFolderName]
        folderPath = os.path.join(baseFolderPath, template % (store.makeTimestamp(), folderName))
        filePath = os.path.join(store.makeFolderSafely(folderPath), fileName)
        # Return
        return filePath

    def fillImagePath(self, imageName):
        return self.fillPath('images', imageName)

    def fillRegionPath(self, regionName):
        return self.fillPath('regions', regionName)

    def fillWindowPath(self, windowName):
        return self.fillPath('windows', windowName)

    def fillDatasetPath(self, datasetName):
        return self.fillPath('datasets', datasetName)

    def fillClassifierPath(self, classifierName):
        return self.fillPath('classifiers', classifierName)

    def fillScanPath(self, scanName):
        return self.fillPath('scans', scanName)

    def fillLocationPath(self, locationName):
        return self.fillPath('locations', locationName)

    def fillPatchPath(self, patchName):
        return self.fillPath('patches', patchName)

    # Get paths

    def getPaths(self, baseFolderName, folderName):
        'Return a list of paths with the latest first'
        # Get paths
        baseFolderPath = self.folderPathByName[baseFolderName]
        template = templateByFolderName[baseFolderName]
        folderPaths = glob.glob(os.path.join(baseFolderPath, template % ('*', folderName)))
        # Sort by timestamp
        folderPacks = [(pattern_timestamp.match(store.extractFileBaseName(x)).group(1), x) for x in folderPaths]
        folderPacks.sort()
        folderPaths = [x[1] for x in reversed(folderPacks)]
        # Append fileNames
        fileName = fileNameByFolderName[baseFolderName]
        return [os.path.join(x, fileName) for x in folderPaths]

    def getImagePaths(self, imageName): 
        return self.getPaths('images', imageName)

    def getRegionPaths(self, regionName): 
        return self.getPaths('regions', regionName)

    def getWindowPaths(self, windowName):
        return self.getPaths('windows', windowName)

    def getDatasetPaths(self, datasetName):
        return self.getPaths('datasets', datasetName)

    def getClassifierPaths(self, classifierName): 
        return self.getPaths('classifiers', classifierName)

    def getScanPaths(self, scanName): 
        return self.getPaths('scans', scanName)

    def getLocationPaths(self, locationName): 
        return self.getPaths('locations', locationName)

    def getPatchPaths(self, patchName):
        return self.getPaths('patches', patchName)

    # Get path

    def getImagePath(self, imageName): 
        return getPath(imageName, self.getImagePaths, 'image set')

    def getRegionPath(self, regionName): 
        return getPath(regionName, self.getRegionPaths, 'region set')

    def getWindowPath(self, windowName):
        return getPath(windowName, self.getWindowPaths, 'window set')

    def getDatasetPath(self, datasetName):
        return getPath(datasetName, self.getDatasetPaths, 'dataset')

    def getClassifierPath(self, classifierName): 
        return getPath(classifierName, self.getClassifierPaths, 'classifier')

    def getScanPath(self, scanName): 
        return getPath(scanName, self.getScanPaths, 'scan list')

    def getLocationPath(self, locationName): 
        return getPath(locationName, self.getLocationPaths, 'location list')

    def getPatchPath(self, patchName): 
        return getPath(patchName, self.getPatchPaths, 'patch set')

    # Get information

    def getImageInformation(self, imageName):
        # Get path
        imagePath = self.getImagePath(imageName)
        # Return information
        import image_store
        return image_store.Information(imagePath)

    def getRegionInformation(self, regionName):
        # Get path
        regionPath = self.getRegionPath(regionName)
        # Return information
        import region_store
        return region_store.Information(regionPath)

    def getWindowInformation(self, windowName):
        # Get path
        windowPath = self.getWindowPath(windowName)
        # Return information
        import window_store
        return window_store.Information(windowPath)

    def getClassifierInformation(self, classifierName):
        # Get path
        classifierPath = self.getClassifierPath(classifierName)
        # Return information
        import classifier
        return classifier.Information(classifierPath)

    def getScanInformation(self, scanName):
        # Get path
        scanPath = self.getScanPath(scanName)
        # Return information
        import scan_store
        return scan_store.Information(scanPath)

    def getPatchInformation(self, patchName):
        # Get path
        patchPath = self.getPatchPath(patchName)
        # Return information
        import patch_store
        return patch_store.Information(patchPath)

# Get

def getFolderName(filePath):
    return os.path.basename(os.path.dirname(filePath))

def getPath(name, method, description):
    paths = method(name)
    if not paths: raise FolderError('Could not find %s: %s' % (description, name))
    return paths[0]


# Set
folderNames = 'images', 'regions', 'windows', 'datasets', 'classifiers', 'scans', 'locations', 'patches'
fileNames = 'image', 'region', 'window', 'dataset', 'classifier', 'scan', 'location', 'patch'
fileNameByFolderName = dict(itertools.izip(folderNames, fileNames))
folderNameByName = dict((x[1], '%d-%s' % x) for x in itertools.izip(itertools.count(1), folderNames))
templateByFolderName = dict(itertools.izip(folderNames, [
    '%s-image-%s',
    '%s-region-%s',
    '%s-window-%s',
    '%s-dataset-%s',
    '%s-classifier-%s',
    '%s-scan-%s',
    '%s-location-%s',
    '%s-patch-%s',
]))


# Set patterns
pattern_timestamp = re.compile('(\d+)-')
pattern_name = re.compile(r'[a-zA-Z1-9_\- (),.]+')


# Define

class WebStore(object):

    def __init__(self, basePath):
        # Make the folder if it doesn't exist
        self.basePath = store.makeFolderSafely(basePath)
        # Set folderPathByName
        self.folderPathByName = dict((key, os.path.join(basePath, folderNameByName[key])) for key in folderNameByName)

    def getPath(self, fileType, fileName):
        fileTypePath = os.path.join(self.basePath, folderNameByName[fileType])
        return store.makeFolderSafely(os.path.join(fileTypePath, str(fileName)))

    def getImagePath(self, imageID):
        return getPath('images', imageID)

    def getRegionPath(self, regionID):
        return getPath('regions', regionID)

    def getWindowPath(self, windowID):
        return getPath('windows', windowID)

    def getDatasetPath(self, datasetID):
        return getPath('datasets', datasetID)

    def getClassifierPath(self, classifierID):
        return getPath('classifiers', classifierID)

    def getScanPath(self, scanID):
        return getPath('scans', scanID)


# Error

class FolderError(Exception):
    pass
