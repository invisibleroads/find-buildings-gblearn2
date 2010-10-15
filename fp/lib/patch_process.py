# Import system modules
import os
import random
# Import custom modules
import store
import image_store
import point_store
import window_process
import sample_process


def buildPatchFromScan(wrongPixelCenters, folderStore, scanName, scanPath, multispectralImagePath, panchromaticImagePath, actualPixelPointMachine, classifierInformation, isTest=False):
    # Show feedback
    if not isTest:
        print 'Saving patch...'
    # Initialize
    multispectralImage = image_store.load(multispectralImagePath)
    panchromaticImage = image_store.load(panchromaticImagePath)
    windowLengthInMeters = classifierInformation.getWindowLengthInMeters()
    patchTestFraction = classifierInformation.getTestDataset().countSamples() / float(classifierInformation.getTrainingDataset().countSamples()) if not isTest else 0.2
    # Set path
    targetPatchPath = folderStore.fillPatchPath(scanName + ' auto')
    targetPatchFolderPath = os.path.dirname(targetPatchPath)
    # Define shortcut
    buildPatchEasily = lambda makePath, pixelCenters: buildPatch(makePath(targetPatchFolderPath), pixelCenters, actualPixelPointMachine, multispectralImage, panchromaticImage, windowLengthInMeters)
    # Shuffle
    random.shuffle(wrongPixelCenters)
    # Prepare
    information = {
        'patches': {
            'probability name': scanName,
            'probability path': scanPath,
        },
        'windows': {
            'window length in meters': windowLengthInMeters,
            'spatial reference': multispectralImage.getSpatialReference(),
        },
    }
    if not isTest:
        # Split
        patchTestCount = int(patchTestFraction * len(wrongPixelCenters))
        # Build
        information['training set'] = buildPatchEasily(sample_process.makeTrainingPath, wrongPixelCenters[patchTestCount:]).getStatistics()
        information['test set'] = buildPatchEasily(sample_process.makeTestPath, wrongPixelCenters[:patchTestCount]).getStatistics()
    # Save
    store.saveInformation(targetPatchPath, information)


def buildPatch(targetPatchPath, pixelCenters, actualPixelPointMachine, multispectralImage, panchromaticImage, windowLengthInMeters):
    # Set paths
    targetPositivePath = targetPatchPath + '_positive'
    targetNegativePath = targetPatchPath + '_negative'
    # Label
    positivePatchPixelCenters, negativePatchPixelCenters = labelPixelCenters(pixelCenters, actualPixelPointMachine)
    # Convert
    positivePatchGeoCenters = multispectralImage.convertPixelLocationsToGeoLocations(positivePatchPixelCenters)
    negativePatchGeoCenters = multispectralImage.convertPixelLocationsToGeoLocations(negativePatchPixelCenters)
    # Save
    spatialReference = multispectralImage.getSpatialReference()
    point_store.save(targetPositivePath, positivePatchGeoCenters, spatialReference)
    point_store.save(targetNegativePath, negativePatchGeoCenters, spatialReference)
    # Extract
    window_process.extract(targetPositivePath, positivePatchGeoCenters, 1, windowLengthInMeters, multispectralImage, panchromaticImage)
    window_process.extract(targetNegativePath, negativePatchGeoCenters, 0, windowLengthInMeters, multispectralImage, panchromaticImage)
    # Combine
    return sample_process.combineDatasets(targetPatchPath, [targetPositivePath, targetNegativePath])


def labelPixelCenters(pixelCenters, actualPixelPointMachine):
    # Initialize
    positivePixelCenters = []
    negativePixelCenters = []
    # For each pixelCenter,
    for pixelCenter in pixelCenters:
        # Build frame
        patchWindowFrame = image_store.centerPixelFrame(pixelCenter, *actualPixelPointMachine.getWindowDimensions())
        # If there are points in the frame,
        if actualPixelPointMachine.getPointsInsideFrame(patchWindowFrame):
            # Label it positive
            positivePixelCenters.append(pixelCenter)
        # Otherwise,
        else:
            # Label it negative
            negativePixelCenters.append(pixelCenter)
    # Return
    return positivePixelCenters, negativePixelCenters
