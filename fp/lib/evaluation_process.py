"""
Methods for evaluating performance
"""


# Import system modules
import numpy
import os
# Import custom modules
import image_store, image_process
import point_store, point_process
import probability_store
import region_store
import view


# Core

def evaluateClassifier(actualLabels, predictedLabels, title):
    # Count
    testSetSize = len(actualLabels)
    # Compute basic
    actualTrue = numpy.array(actualLabels) == 1
    actualFalse = ~actualTrue
    predictedTrue = numpy.array(predictedLabels) == 1
    predictedFalse = ~predictedTrue
    # Compute intermediate
    actualTrue_predictedTrue = sum(actualTrue * predictedTrue)
    actualFalse_predictedFalse = sum(actualFalse * predictedFalse)
    actualTrue_predictedFalse = sum(actualTrue * predictedFalse)
    actualFalse_predictedTrue = sum(actualFalse * predictedTrue)
    # Compute final
    percentError, falsePositiveError, falseNegativeError = computePercentages(actualTrue_predictedFalse, actualFalse_predictedTrue, actualTrue_predictedTrue + actualTrue_predictedFalse, actualFalse_predictedFalse + actualFalse_predictedTrue)
    print '*** %s ***' % title
    print 'testError: %s' % percentError
    print 'falsePositiveTestError: %s' % falsePositiveError
    print 'falseNegativeTestError: %s' % falseNegativeError
    # Return
    return {
        'test error': percentError,
        'false positive test error': falsePositiveError,
        'false negative test error': falseNegativeError,
        'actual true': sum(actualTrue),
        'actual false': sum(actualFalse),
        'predicted true': sum(predictedTrue),
        'predicted false': sum(predictedFalse),
        'actual true predicted true': actualTrue_predictedTrue,
        'actual true predicted false': actualTrue_predictedFalse,
        'actual false predicted false': actualFalse_predictedFalse,
        'actual false predicted true': actualFalse_predictedTrue,
        'test set size': testSetSize,
    }

def evaluateWindows(probabilityPath, actualLocationPath, multispectralImagePath, windowGeoLength):
    # Initialize
    print 'Evaluating windows...'
    multispectralImage = image_store.load(multispectralImagePath)
    # Load
    probabilityPacks = probability_store.load(probabilityPath)
    windowLocations = [(x[0], x[1]) for x in probabilityPacks]
    windowPixelWidth, windowPixelHeight = multispectralImage.convertGeoDimensionsToPixelDimensions(windowGeoLength, windowGeoLength)
    windowCount = len(windowLocations)
    # Load predicted
    predictedWindowLocations = set((x[0], x[1]) for x in probabilityPacks if x[2] == 1)
    # Load actual
    actualGeoLocations = point_store.load(actualLocationPath)[0]
    actualPixelLocations = multispectralImage.convertGeoLocationsToPixelLocations(actualGeoLocations)
    actualPixelPointMachine = point_process.PointMachine(actualPixelLocations, 'INTEGER', windowPixelWidth, windowPixelHeight)
    actualWindowLocations = set(filter(lambda x: actualPixelPointMachine.getPointsInsideWindow(x), windowLocations))
    # Get
    predictedNotActualWindowLocations = predictedWindowLocations - actualWindowLocations
    actualNotPredictedWindowLocations = actualWindowLocations - predictedWindowLocations
    wrongWindowLocations = predictedNotActualWindowLocations.union(actualNotPredictedWindowLocations)
    wrongPixelCenters = [image_store.getWindowCenter(x, windowPixelWidth, windowPixelHeight) for x in wrongWindowLocations]
    # Compute
    actualTrue_predictedFalse = len(actualNotPredictedWindowLocations)
    actualFalse_predictedTrue = len(predictedNotActualWindowLocations)
    actualTrue = len(actualWindowLocations)
    actualFalse = windowCount - actualTrue
    predictedTrue = len(predictedWindowLocations)
    predictedFalse = windowCount - predictedTrue
    percentError, falsePositiveError, falseNegativeError = computePercentages(actualTrue_predictedFalse, actualFalse_predictedTrue, actualTrue, actualFalse)
    # Save
    windowPerformance = {
        'percent error': percentError, 
        'false positive error': falsePositiveError,
        'false negative error': falseNegativeError,
        'actual true': actualTrue,
        'actual false': actualFalse,
        'predicted true': predictedTrue,
        'predicted false': predictedFalse,
        'actual true predicted true': actualTrue - actualTrue_predictedFalse,
        'actual true predicted false': actualTrue_predictedFalse,
        'actual false predicted true': actualFalse_predictedTrue,
        'actual false predicted false': actualFalse - actualFalse_predictedTrue,
        'window count': windowCount,
    }
    return windowPerformance, wrongPixelCenters, actualPixelPointMachine

def evaluateWindowsByRadius(probabilityPath, geoRadius):
    # Initialize
    print 'Evaluating windows with %s meter radius...' % geoRadius
    scanInformation = probability_store.Information(probabilityPath)
    multispectralImage, panchromaticImage, actualGeoCenters, windowPixelDimensions = scanInformation.getPackage()
    geoDiameter = float(geoRadius) * 2
    # Get predictedGeoCenters
    predictedPixelCenters = probability_store.loadPredictedPixelCenters(probabilityPath, windowPixelDimensions)
    predictedGeoCenters = multispectralImage.convertPixelLocationsToGeoLocations(predictedPixelCenters)
    # Get
    actualNotPredictedCenters = point_process.extractBadLocations(geoDiameter, actualGeoCenters, predictedGeoCenters)
    predictedNotActualCenters = point_process.extractBadLocations(geoDiameter, predictedGeoCenters, actualGeoCenters)
    # Count
    actual = len(actualGeoCenters)
    predicted = len(predictedGeoCenters)
    actualNotPredicted = len(actualNotPredictedCenters)
    predictedNotActual = len(predictedNotActualCenters)
    actualAndPredicted = len(actualGeoCenters) - actualNotPredicted
    predictedAndActual = len(predictedGeoCenters) - predictedNotActual
    return {
        'evaluation radius in meters': geoRadius,
        'actual count': actual,
        'predicted count': predicted,
        'actual not predicted count': actualNotPredicted,
        'predicted not actual count': predictedNotActual,
        'predicted and actual count': predictedAndActual,
        'actual and predicted count': actualAndPredicted,
        'pNa/p': predictedNotActual / float(predicted) if predicted else None,
        'aNp/a': actualNotPredicted / float(actual) if actual else None,
        'precision': predictedAndActual / float(predicted) if predicted else None,
        'recall': actualAndPredicted / float(actual) if actual else None,
    }

def evaluateWindowsByLength(probabilityPath, geoLength):
    # Load information
    probabilityInformation = probability_store.Information(probabilityPath)
    multispectralImage, panchromaticImage = probabilityInformation.getImagePack()
    # Load regions
    regionGenerator = image_process.makeWindowGenerator(multispectralImage, panchromaticImage, geoLength, 1)
    regionPixelFrames = map(region_store.getMultispectralPixelFrame, regionGenerator)
    # Return
    return evaluateWindowsByRegions(probabilityPath, regionPixelFrames)

def evaluateWindowsByRegions(probabilityPath, regionPixelFrames):
    # Load
    scanInformation = probability_store.Information(probabilityPath)
    # Initialize
    multispectralImage, panchromaticImage, actualGeoCenters, windowPixelDimensions = scanInformation.getPackage()
    regionCount = len(regionPixelFrames)
    regionLabels_actual = numpy.zeros(regionCount)
    pixelCenters_actual = multispectralImage.convertGeoLocationsToPixelLocations(actualGeoCenters)
    regionLabels_predicted = numpy.zeros(len(regionPixelFrames))
    pixelCenters_predicted = probability_store.loadPredictedPixelCenters(probabilityPath, windowPixelDimensions)
    # Build machines
    pointMachine_actual = point_process.PointMachine(pixelCenters_actual, 'INTEGER')
    pointMachine_predicted = point_process.PointMachine(pixelCenters_predicted, 'INTEGER')
    # For each region,
    print 'Evaluating windows by region...'
    for regionIndex, regionPixelFrame in enumerate(regionPixelFrames):
        # Determine actual label
        regionLabels_actual[regionIndex] = 1 if pointMachine_actual.getPointsInsideFrame(regionPixelFrame) else 0
        # Determine predicted label
        regionLabels_predicted[regionIndex] = 1 if pointMachine_predicted.getPointsInsideFrame(regionPixelFrame) else 0
        # Show feedback
        if regionIndex % 100 == 0:
            view.printPercentUpdate(regionIndex, len(regionPixelFrames))
    # Show feedback
    view.printPercentFinal(len(regionPixelFrames))
    # Compute
    truePositive = sum((regionLabels_actual == 1) * (regionLabels_predicted == 1))
    trueNegative = sum((regionLabels_actual == 0) * (regionLabels_predicted == 0))
    falsePositive = sum((regionLabels_actual == 0) * (regionLabels_predicted == 1))
    falseNegative = sum((regionLabels_actual == 1) * (regionLabels_predicted == 0))
    actualPositive = sum(regionLabels_actual == 1)
    actualNegative = sum(regionLabels_actual == 0)
    # Count
    actualCount = sum(regionLabels_actual)
    predictedCount = sum(regionLabels_predicted)
    # Return
    return {
        'region count': regionCount,
        'true positive count': truePositive,
        'true positive rate': truePositive / float(actualPositive) if actualPositive else None,
        'true negative count': trueNegative,
        'false positive count': falsePositive,
        'false positive rate': falsePositive / float(actualNegative) if actualNegative else None,
        'false negative count': falseNegative,
        'actual positive count': actualCount,
        'predicted positive count': predictedCount,
        'precision': truePositive / float(predictedCount) if predictedCount else None,
        'recall': truePositive / float(actualCount) if actualCount else None,
    }

def evaluateLocations(targetFolderPath, geoDiameter, actualLocationPath, predictedLocationPath, regionGeoFrames):
    # Load
    rawActualLocations, spatialReference1 = point_store.load(actualLocationPath)
    rawPredictedLocations, spatialReference2 = point_store.load(predictedLocationPath)
    # Make sure the points have the same spatial reference
    if spatialReference1 != spatialReference2:
        raise point_store.ShapeDataError(point_store.x_differentSpatialReferences)
    spatialReference = spatialReference1
    # Compare
    heap, information = compareLocations(geoDiameter, rawActualLocations, rawPredictedLocations, regionGeoFrames)
    # Define
    def save(fileName, points):
        targetPath = os.path.join(targetFolderPath, fileName)
        point_store.save(targetPath, points, spatialReference)
    # Save
    save('actual', heap['actual'])
    save('predicted', heap['predicted'])
    save('actualNotPredicted', heap['actualNotPredicted'])
    save('predictedNotActual', heap['predictedNotActual'])
    # Return
    return information


# Helpers

def computePercentages(actualTrue_predictedFalse, actualFalse_predictedTrue, actualTrue, actualFalse):
    percentError = 100 * (actualTrue_predictedFalse + actualFalse_predictedTrue) / float(actualFalse + actualTrue)
    falsePositiveError = 100 * actualFalse_predictedTrue / float(actualFalse)
    falseNegativeError = 100 * actualTrue_predictedFalse / float(actualTrue)
    return percentError, falsePositiveError, falseNegativeError

def compareLocations(geoDiameter, rawActualLocations, rawPredictedLocations, regionGeoFrames):
    # Prepare
    actualPointMachine = point_process.PointMachine(rawActualLocations, 'REAL')
    predictedPointMachine = point_process.PointMachine(rawPredictedLocations, 'REAL')
    heap = {
        'actual': set(),
        'predicted': set(),
        'actualNotPredicted': set(),
        'predictedNotActual': set(),
    }
    # For each regionGeoFrame,
    for regionIndex, regionGeoFrame in enumerate(regionGeoFrames):
        # Filter
        actualLocations = actualPointMachine.getPointsInsideFrame(regionGeoFrame)
        predictedLocations = predictedPointMachine.getPointsInsideFrame(regionGeoFrame)
        # Get
        actualNotPredictedLocations = point_process.extractBadLocations(geoDiameter, actualLocations, rawPredictedLocations)
        predictedNotActualLocations = point_process.extractBadLocations(geoDiameter, predictedLocations, rawActualLocations)
        # Store
        heap['actual'].update(actualLocations)
        heap['predicted'].update(predictedLocations)
        heap['actualNotPredicted'].update(actualNotPredictedLocations)
        heap['predictedNotActual'].update(predictedNotActualLocations)
        # Show feedback
        view.printPercentUpdate(regionIndex, len(regionGeoFrames))
    # Show feedback
    view.printPercentFinal(len(regionGeoFrames))
    # Return
    return heap, {
        'actual count': len(heap['actual']),
        'predicted count': len(heap['predicted']),
        'actual not predicted count': len(heap['actualNotPredicted']),
        'predicted not actual count': len(heap['predictedNotActual']),
    }
