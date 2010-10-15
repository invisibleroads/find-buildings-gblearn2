#!/usr/bin/python
"""\
Sample example locations from regions.

[parameters]
example count per region = INTEGER
multispectral pixel shift value = INTEGER
shift count = INTEGER

[windowName1]
region name = NAME

[windowName2]
region name = NAME

..."""
# Import system modules
import os
# Import custom modules
import script_process
from fp.lib import store, image_store, point_store, region_store, region_process, sample_process, window_process, view


def run(ownerID, webStore, windowName, regionID, parameterByName):
    """
    Sample windows from the specified region and return statistics
    """
    # Import custom modules
    from fp import model
    from fp.model import meta
    # Prepare region
    region = meta.Session.query(model.Region).get(regionID)
    if not region:
        return
    # Prepare location
    location = meta.Session.query(model.Location).get(locationID)
    if not location:
        return
    # Prepare a new window set
    window = model.Window(windowName, ownerID, regionID)
    meta.Session.add(window)
    meta.Session.commit()
    targetWindowPath = webStore.getWindowPath(window.id)
    # Sample windows
    sampleWindows(targetWindowPath, region, location, parameterByName)
    # Mark it complete
    window.is_complete = True
    meta.Session.commit()


def step(taskName, parameterByName, folderStore, options):
    # Prepare
    targetWindowPath = folderStore.fillWindowPath(taskName)
    regionName = parameterByName['region name']
    regionPath = folderStore.getRegionPath(regionName)
    region = region_store.Information(regionPath)
    # Sample windows
    sampleWindows(targetWindowPath, region, location, parameterByName, options)


def sampleWindows(targetWindowPath, region, location, parameterByName, options=None):
    # Get parameters
    exampleCountPerRegion = parameterByName['example count per region']
    multispectralPixelShiftValue = parameterByName['multispectral pixel shift value']
    shiftCount = parameterByName['shift count']
    # Prepare regionFrames



    regionSet = region.getDataset()
    # regionDataset = region_store.load(region.path)
    regionFrames = regionDataset.getRegionFrames()
    regionFrameCount = len(regionFrames)
    # Prepare counts
    testRegionSet = region.getTestDataset()
    # testRegionDataset = region_store.load(regionInformation.getTestRegionPath())
    testFractionPerRegion = regionInformation.getTestFractionPerRegion()
    # Load imageDataset
    imagePath = folderStore.getImagePath(regionInformation.getImageName())
    imageInformation = image_store.Information(imagePath)
    multispectralImage = image_store.load(imageInformation.getMultispectralImagePath())
    panchromaticImage = image_store.load(imageInformation.getPanchromaticImagePath())
    # Load locations
    positiveGeoLocations, spatialReference = point_store.load(imageInformation.getPositiveLocationPath())
    # Convert
    windowLengthInMeters = regionInformation.getWindowLengthInMeters()
    windowPixelDimensions = multispectralImage.convertGeoDimensionsToPixelDimensions(windowLengthInMeters, windowLengthInMeters)
    positivePixels = multispectralImage.convertGeoLocationsToPixelLocations(positiveGeoLocations)
    # Place examples
    exampleMachine = region_process.ExampleMachine(positivePixels, exampleCountPerRegion, testFractionPerRegion, testRegionDataset, windowPixelDimensions, multispectralPixelShiftValue, shiftCount)
    examplePacks = []
    if options and not options.is_test:
        print 'Placing examples in %s regions for "%s"...' % (regionFrameCount, taskName)
        for regionFrame in regionFrames:
            examplePacks.append(exampleMachine.placeInFrame(regionFrame))
            exampleCount = len(examplePacks)
            if exampleCount % 10 == 0: 
                view.printPercentUpdate(exampleCount, regionFrameCount)
        view.printPercentFinal(regionFrameCount)
    exampleInformation = {}
    trainingPaths = []
    testPaths = []
    # Set
    targetWindowFolderPath = os.path.dirname(targetWindowPath)
    if options and not options.is_test:
        # For each exampleName,
        for exampleName in examplePacks[0].keys():
            # Convert
            examplePixelLocations = sum((x[exampleName] for x in examplePacks), [])
            exampleGeoLocations = multispectralImage.convertPixelLocationsToGeoLocations(examplePixelLocations)
            examplePath = os.path.join(targetWindowFolderPath, exampleName)
            exampleLabel = 1 if 'positive' in exampleName else 0
            # Save
            point_store.save(examplePath, exampleGeoLocations, spatialReference)
            exampleInformation[exampleName + ' count'] = len(examplePixelLocations)
            # Extract
            print 'Extracting %s windows for %s...' % (len(examplePixelLocations), exampleName)
            window_process.extract(examplePath, exampleGeoLocations, exampleLabel, windowLengthInMeters, multispectralImage, panchromaticImage)
            (testPaths if 'test' in exampleName else trainingPaths).append(examplePath)
    # Record
    information = {
        'windows': {
            'window length in meters': windowLengthInMeters,
            'spatial reference': spatialReference,
        },
        'regions': {
            'name': regionName,
            'path': regionPath,
            'count': regionFrameCount,
        },
        'examples': exampleInformation,
    }
    # Combine
    if options and not options.is_test:
        information['training set'] = sample_process.combineDatasets(sample_process.makeTrainingPath(targetWindowFolderPath), trainingPaths).getStatistics()
        information['test set'] = sample_process.combineDatasets(sample_process.makeTestPath(targetWindowFolderPath), testPaths).getStatistics()
    # Save information
    store.saveInformation(targetWindowPath, information)


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
