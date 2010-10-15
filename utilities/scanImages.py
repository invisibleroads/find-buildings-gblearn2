#!/usr/bin/python
"""\
Scan images.  Evaluate windows if given the complete set of positive
locations for an image.

[parameters]
classifier name = NAME
scan ratio = FLOAT
coverage fraction = FLOAT

[probabilityName1]
image name = NAME

[probabilityName2]
image name = NAME

..."""
# Import system modules
# Import custom modules
import script_process
from fp.lib import store, classifier, image_store, probability_store, region_store, evaluation_process, patch_process, point_process


def step(taskName, parameterByName, folderStore, options):
    # Get parameters
    imageName = parameterByName['image name']
    imagePath = folderStore.getImagePath(imageName)
    imageInformation = folderStore.getImageInformation(imageName)
    multispectralImagePath = imageInformation.getMultispectralImagePath()
    multispectralImage = image_store.load(multispectralImagePath)
    scanRatio = float(parameterByName['scan ratio'])
    classifierName = parameterByName['classifier name']
    classifierPath = folderStore.getClassifierPath(classifierName)
    classifierInformation = folderStore.getClassifierInformation(classifierName)
    windowLengthInMeters = classifierInformation.getWindowLengthInMeters()
    panchromaticImagePath = imageInformation.getPanchromaticImagePath()
    positiveLocationPath = imageInformation.getPositiveLocationPath()
    coverageFraction = parameterByName.get('coverage fraction', 1)
    # Record
    targetProbabilityPath = folderStore.fillProbabilityPath(taskName)
    regionPath = targetProbabilityPath + '_region'
    probabilityInformation = {
        'classifier': {
            'name': classifierName,
            'path': classifierPath,
        },
        'parameters': {
            'window length in meters': windowLengthInMeters,
            'scan ratio': scanRatio, 
            'coverage fraction': coverageFraction,
        },
        'probability': {
            'region path': regionPath,
            'image name': imageName,
            'image path': imagePath,
        },
    }
    # Run
    store.saveInformation(targetProbabilityPath, probabilityInformation)
    if not options.is_test:
        # Frame
        xMax = multispectralImage.width
        yMax = multispectralImage.height
        xMargin = int(xMax * (1 - coverageFraction) / 2)
        yMargin = int(yMax * (1 - coverageFraction) / 2)
        regionFrames = [(xMargin, yMargin, xMax - xMargin, yMax - yMargin)]
        regionDataset = region_store.save(regionPath, regionFrames)
        regionDataset.saveShapefile(regionPath, multispectralImage)
        # Scan
        info = classifier.scan(targetProbabilityPath, classifierPath, multispectralImagePath, panchromaticImagePath, scanRatio, regionFrames)
        # Save
        print 'Saving probability matrix as a shapefile...'
        probability_store.saveShapefile(targetProbabilityPath, targetProbabilityPath, multispectralImage, windowLengthInMeters)
        # Evaluate windows
        windowPerformance, wrongPixelCenters, actualPixelPointMachine = evaluation_process.evaluateWindows(targetProbabilityPath, positiveLocationPath, multispectralImagePath, windowLengthInMeters)
        probabilityInformation['performance'] = windowPerformance
        probabilityInformation['performance'].update(info)
    else:
        wrongPixelCenters = []
        windowPixelWidth, windowPixelHeight = multispectralImage.convertGeoDimensionsToPixelDimensions(windowLengthInMeters, windowLengthInMeters)
        actualPixelPointMachine = point_process.PointMachine([], 'INTEGER', windowPixelWidth, windowPixelHeight)
    # Update
    store.saveInformation(targetProbabilityPath, probabilityInformation)
    # Save patch
    patch_process.buildPatchFromScan(wrongPixelCenters, folderStore, taskName, targetProbabilityPath, multispectralImagePath, panchromaticImagePath, actualPixelPointMachine, classifierInformation, options.is_test)


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
