#!/usr/bin/python
"""\
Analyze scanned results by region and generate a shapefile sampling regions with poor performance.

[parameters]
patch count per region = INTEGER
minimum percent correct = FLOAT

[patchName1]
probability name = NAME

..."""
# Import system modules
import os
import itertools
# Import custom modules
import script_process
from fp.lib import store, point_store, point_process, sample_process, classifier, region_store, probability_store, patch_process, view


def step(taskName, parameterByName, folderStore, options):
    # Get
    patchCountPerRegion = parameterByName['patch count per region']
    minimumPercentCorrect = parameterByName['minimum percent correct']
    probabilityName = parameterByName['probability name']
    probabilityPath = folderStore.getProbabilityPath(probabilityName)
    probabilityInformation = probability_store.Information(probabilityPath)
    imageName = probabilityInformation.getImageName()
    imageInformation = folderStore.getImageInformation(imageName)
    multispectralImage = imageInformation.getMultispectralImage()
    panchromaticImage = imageInformation.getPanchromaticImage()
    positiveLocationPath = imageInformation.getPositiveLocationPath()
    positiveGeoLocations, spatialReference = point_store.load(positiveLocationPath)
    # If the probability is from scanning the entire image,
    if not probabilityInformation.hasRegionName():
        regionPath = folderStore.getRegionPath(parameterByName['region name'])
    # Get regionDataset
    else:
        regionPath = probabilityInformation.getRegionPath()
    regionInformation = region_store.Information(regionPath)
    regionFrames = regionInformation.getRegionDataset().getRegionFrames()
    regionCount = len(regionFrames)
    testRegionDataset = regionInformation.getTestRegionDataset()
    # Get windowPixelDimensions
    windowLengthInMeters = probabilityInformation.getWindowLengthInMeters()
    windowPixelDimensions = multispectralImage.convertGeoDimensionsToPixelDimensions(windowLengthInMeters, windowLengthInMeters)
    # Get classifierInformation
    classifierPath = probabilityInformation.getClassifierPath()
    classifierInformation = classifier.Information(classifierPath)
    # Record
    information = {
        'patches': {
            'patch count per region': patchCountPerRegion,
            'minimum percent correct': minimumPercentCorrect,
            'probability name': probabilityName,
            'probability path': probabilityPath,
        },
        'windows': {
            'window length in meters': windowLengthInMeters,
            'spatial reference': spatialReference,
        },
    }
    # Set
    targetPatchPath = folderStore.fillPatchPath(taskName)
    targetPatchFolderPath = os.path.dirname(targetPatchPath)
    if not options.is_test:
        # Make pixelPointMachines
        trainingPixelPointMachine = point_process.makePixelPointMachine(classifierInformation.getTrainingDataset().getGeoCenters(), windowLengthInMeters, multispectralImage)
        testPixelPointMachine = point_process.makePixelPointMachine(classifierInformation.getTestDataset().getGeoCenters(), windowLengthInMeters, multispectralImage)
        actualPixelPointMachine = point_process.makePixelPointMachine(positiveGeoLocations, windowLengthInMeters, multispectralImage)
        # Get badRegionFrames
        print 'Finding regions with poor performance...'
        isGoodWindow = actualPixelPointMachine.getPointsInsideWindow
        probabilityPacks = probability_store.load(probabilityPath)
        performances = analyzeRegions(regionFrames, probabilityPacks, isGoodWindow)
        badRegionFrames = [x[0] for x in itertools.izip(regionFrames, performances) if x[1] < minimumPercentCorrect]
        badRegionCount = len(badRegionFrames)
        # Save badRegionFrames
        badRegionDataset = region_store.save(targetPatchPath, badRegionFrames)
        badRegionDataset.saveShapefile(targetPatchPath, multispectralImage)
        # Make patch window centers
        print 'Sampling from regions with poor performance...'
        testPatchPixelCenters = []
        trainingPatchPixelCenters = []
        for regionFrame in badRegionFrames:
            # Load badCenters
            testRegionFrame = testRegionDataset.getFrameInsideFrame(regionFrame)
            regionalTrainingPixelCenters = trainingPixelPointMachine.getPointsInsideFrame(regionFrame)
            regionalTestPixelCenters = testPixelPointMachine.getPointsInsideFrame(testRegionFrame)
            badCenters = regionalTrainingPixelCenters + regionalTestPixelCenters
            # Generate patch window centers
            centerMachine = sample_process.CenterMachine(regionFrame, windowPixelDimensions, badCenters)
            for patchWindowPixelCenter in centerMachine.makeCenters(patchCountPerRegion):
                if point_process.isInsideRegion(patchWindowPixelCenter, testRegionFrame):
                    testPatchPixelCenters.append(patchWindowPixelCenter)
                else:
                    trainingPatchPixelCenters.append(patchWindowPixelCenter)
        # Define
        buildPatch = lambda makePath, pixelCenters: patch_process.buildPatch(makePath(targetPatchFolderPath), pixelCenters, actualPixelPointMachine, multispectralImage, panchromaticImage, windowLengthInMeters)
        # Produce training and test sets
        information['training set'] = buildPatch(sample_process.makeTrainingPath, trainingPatchPixelCenters).getStatistics()
        information['test set'] = buildPatch(sample_process.makeTestPath, testPatchPixelCenters).getStatistics()
        # Record
        information['performance'] = {
            'bad region count': badRegionCount,
            'region count': regionCount,
            'percent correct': (regionCount - badRegionCount) / float(regionCount),
        }
        information['performance by region'] = dict(('%s %s %s %s' % x[0], x[1]) for x in itertools.izip(regionFrames, performances))
    # Save
    store.saveInformation(targetPatchPath, information)


def analyzeRegions(frames, probabilityPacks, isGoodWindow):
    # Initialize
    frameCount = len(frames)
    performances = []
    # Get
    for frameIndex, frame in enumerate(frames):
        # Load
        regionalPacks = filter(lambda x: point_process.isInsideRegion(x, frame), probabilityPacks)
        # Evaluate
        correctVector = []
        for probabilityPack in regionalPacks:
            windowX, windowY, predictedLabel = probabilityPack[:3]
            actualLabel = True if isGoodWindow((windowX, windowY)) else False
            correctVector.append(predictedLabel == actualLabel)
        # Compute performance
        performances.append(sum(correctVector) / float(len(correctVector)))
        # Show feedback
        if frameIndex % 100 == 0:
            view.printPercentUpdate(frameIndex + 1, frameCount)
    view.printPercentFinal(frameCount)
    # Return
    return performances


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
