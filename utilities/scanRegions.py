#!/usr/bin/python


"""\
Scan regions.

[parameters]
classifier name = NAME
scan ratio = FLOAT

[probabilityName1]
region name = NAME

[probabilityName2]
region name = NAME

..."""


# Import system modules
# Import custom modules
import script_process
from fp.lib import store, classifier, image_store, probability_store, evaluation_process, patch_process, point_process


def step(taskName, parameterByName, folderStore, options):
    # Get parameters
    classifierName = parameterByName['classifier name']
    classifierPath = folderStore.getClassifierPath(classifierName)
    classifierInformation = folderStore.getClassifierInformation(classifierName)
    windowLengthInMeters = classifierInformation.getWindowLengthInMeters()
    scanRatio = parameterByName['scan ratio']
    regionName = parameterByName['region name']
    regionPath = folderStore.getRegionPath(regionName)
    regionInformation = folderStore.getRegionInformation(regionName)
    regionDataset = regionInformation.getRegionDataset()
    # Prepare
    imageName = regionInformation.getImageName()
    imagePath = folderStore.getImagePath(imageName)
    imageInformation = folderStore.getImageInformation(imageName)
    multispectralImagePath = imageInformation.getMultispectralImagePath()
    multispectralImage = image_store.load(multispectralImagePath)
    panchromaticImagePath = imageInformation.getPanchromaticImagePath()
    positiveLocationPath = imageInformation.getPositiveLocationPath()
    regionFrames = regionDataset.getRegionFrames()
    # Record
    targetProbabilityPath = folderStore.fillProbabilityPath(taskName)
    probabilityInformation = {
        'classifier': {
            'name': classifierName,
            'path': classifierPath,
        },
        'parameters': {
            'window length in meters': windowLengthInMeters,
            'scan ratio': scanRatio, 
        },
        'probability': {
            'region name': regionName,
            'region path': regionPath,
            'image name': imageName,
            'image path': imagePath,
        },
    }
    store.saveInformation(targetProbabilityPath, probabilityInformation)
    # If this is not a test,
    if not options.is_test:
        # Scan
        info = classifier.scan(targetProbabilityPath, classifierPath, multispectralImagePath, panchromaticImagePath, scanRatio, regionFrames)
        # Save
        print 'Saving probability matrix as a shapefile...'
        probability_store.saveShapefile(targetProbabilityPath, targetProbabilityPath, image_store.load(multispectralImagePath), windowLengthInMeters)
        # Evaluate
        print 'Evaluating windows...'
        windowPerformance, wrongPixelCenters, actualPixelPointMachine = evaluation_process.evaluateWindows(targetProbabilityPath, positiveLocationPath, multispectralImagePath, windowLengthInMeters)
        probabilityInformation['performance'] = windowPerformance
        probabilityInformation['performance'].update(info)
    else:
        wrongPixelCenters = []
        windowPixelWidth, windowPixelHeight = multispectralImage.convertGeoDimensionsToPixelDimensions(windowLengthInMeters, windowLengthInMeters)
        actualPixelPointMachine = point_process.PointMachine([], 'INTEGER', windowPixelWidth, windowPixelHeight)
    # Update
    store.saveInformation(targetProbabilityPath, probabilityInformation)
    # Build patch
    patch_process.buildPatchFromScan(wrongPixelCenters, folderStore, taskName, targetProbabilityPath, multispectralImagePath, panchromaticImagePath, actualPixelPointMachine, classifierInformation, options.is_test)


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
