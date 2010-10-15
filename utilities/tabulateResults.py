# Import system modules
import glob
import csv
import re
import os
import mako.lookup
import mako.exceptions
import itertools
import numpy
import pylab
# Import custom modules
import script_process
from fp.lib import folder_store, store, classifier_cnn, parameter_store, evaluation_process


# Set patterns
pattern_sourceName = re.compile(r'\d+-window-(.*)')
pattern_probabilityName = re.compile(r'\d+-probability-(.*)')
pattern_locationName = re.compile(r'\d+-location-(.*)')
# Define
def getName(pattern, path):
    return pattern.search(path).group(1)


def loadClassifierResult(scanName, scanPath, expandPath):
    # Get
    scanInformation = loadScanInformation(scanPath, expandPath)
    # Get classifierInformation
    classifierPath = expandPath(scanInformation['probabilities']['classifier']['path'])
    classifierInformation = store.loadInformation(classifierPath)
    # Get datasetInformation
    datasetPath = expandPath(classifierInformation['dataset']['path'])
    datasetInformation = store.loadInformation(datasetPath)
    # Get sourceInformation
    sourceWindowPaths = map(expandPath, store.unstringifyStringList(datasetInformation['sources']['window paths']))
    sourcePatchPatchs = map(expandPath, store.unstringifyStringList(datasetInformation['sources']['patch paths']))
    sourceInformation = {
        'windows': [loadSourceWindowInformation(x, expandPath) for x in sourceWindowPaths],
        'patches': [loadSourcePatchInformation(x, expandPath) for x in sourcePatchPatchs],
    }
    # Get most recent patchInformation using probabilityPath
    folderStore = folder_store.Store(os.path.dirname(expandPath('.')))
    patchInformation = loadPatchInformationFromProbabilityPath(folderStore, scanPath)
    # Append
    return {
        'patches': patchInformation,
        'scans': scanInformation,
        'classifiers': classifierInformation,
        'datasets': datasetInformation,
        'sources': sourceInformation,
        'name': scanName,
    }


def loadResults(path='.'):
    # Initialize
    results = []
    # Try to load locations
    locationInformationByPath = loadInformations('locations', path)
    # If locations exist,
    if locationInformationByPath:
        # For each locationInformation,
        for locationPath, locationInformation in locationInformationByPath.iteritems():
            # Get locationName
            locationName = getName(pattern_locationName, locationPath)
            print locationName
            # Get folderStore
            experimentPath = os.path.dirname(os.path.dirname(locationPath))
            def expandPath(localPath):
                return os.path.join(experimentPath, localPath)
            # Get scanInformation
            scanPath = expandPath(locationInformation['probability']['path'])
            # Load classifierResult
            result = loadClassifierResult(locationName, scanPath, expandPath)
            result['locations'] = locationInformation
            results.append(result)
    # Otherwise,
    else:
        # Load scans
        scanInformationByPath = loadInformations('probabilities', path)
        # For each scanInformation,
        for scanPath, scanInformation in scanInformationByPath.iteritems():
            # Get scanName
            scanName = getName(pattern_probabilityName, scanPath)
            print scanName
            # Get folderStore
            experimentPath = os.path.dirname(os.path.dirname(scanPath))
            def expandPath(localPath):
                return os.path.join(experimentPath, localPath)
            # Load classifierResult
            result = loadClassifierResult(scanName, os.path.join(scanPath, folder_store.fileNameByFolderName['probabilities']), expandPath)
            results.append(result)
    # Sort first by patch percent error and then by scan percent error
    def getPatchPercentError(result):
        patchInformation = result['patches']
        if patchInformation and 'performance' in patchInformation:
            patchPerformance = patchInformation['performance']
            patchPercentCorrect = float(patchPerformance['percent correct'])
            patchPercentError = 1 - patchPercentCorrect
            return patchPercentError
    def getScanPercentError(result):
        scanInformation = result['scans']
        if scanInformation:
            scanProbabilities = scanInformation['probabilities']
            scanProbabilitiesPerformance = scanProbabilities['performance']
            scanPercentError = scanProbabilitiesPerformance['percent error']
            return scanPercentError
    return sorted(results, key=lambda x: (getPatchPercentError(x), getScanPercentError(x)))


def loadPaths():
    # Initialize
    paths = []
    # Walk
    for basePath, folderNames, fileNames in os.walk('.'):
        if '.svn' in basePath: 
            continue
        paths.extend(os.path.join(basePath, x)[2:] for x in fileNames)
    # Return
    return paths


def loadInformations(informationName, path):
    # Initialize
    informationByPath = {}
    folderName = folder_store.folderNameByName[informationName]
    fileName = folder_store.fileNameByFolderName[informationName]
    # For each folder,
    for basePath, folderNames, fileNames in os.walk(path):
        # Skip Subversion files
        if '.svn' in basePath: 
            continue
        # Only pay attention a specific folder
        if '%s/' % folderName in basePath:
            # Get information
            informationPath = os.path.join(basePath, fileName)
            information = store.loadInformation(informationPath)
            # If we have information,
            if information:
                # Store
                informationByPath[basePath] = information
    # Return
    return informationByPath


def loadPatchInformationFromProbabilityPath(folderStore, probabilityPath):
    'Load most recent patchInformation corresponding to the given probabilityPath'
    probabilityPath = os.path.abspath(probabilityPath)
    patchPaths = folderStore.getPatchPaths('*')
    patchInformations = map(store.loadInformation, patchPaths)
    for patchInformation in patchInformations:
        if patchInformation:
            if os.path.abspath(patchInformation['patches']['probability path']) == probabilityPath:
                return patchInformation
    return {}


def loadSourceWindowInformation(sourcePath, expandPath):
    # Get windowInformation
    windowInformation = store.loadInformation(sourcePath)
    if not windowInformation: 
        return {}
    # Add extra information
    sourceName = getName(pattern_sourceName, os.path.dirname(sourcePath))
    windowInformation['parameters'] = queueReader.getInformation_sampleWindows(sourceName)
    # Initialize
    sourceWindowInformation = {
        'windows': windowInformation,
    }
    # Get regionInformation
    regionPath = expandPath(windowInformation['regions']['path'])
    regionInformation = store.loadInformation(regionPath)
    if regionInformation:
        # Get imageInformation
        imagePath = expandPath(regionInformation['parameters']['image path'])
        imageInformation = store.loadInformation(imagePath)
        # Store
        sourceWindowInformation['regions'] = regionInformation
        sourceWindowInformation['images'] = imageInformation
    # Return
    return sourceWindowInformation


def loadSourcePatchInformation(sourcePath, expandPath):
    # Get patchInformation
    patchInformation = store.loadInformation(sourcePath)
    if not patchInformation:
        return {}
    # Get scanInformation
    probabilityPath = patchInformation['patches']['probability path']
    scanInformation = loadScanInformation(probabilityPath, expandPath)
    # Assemble
    scanInformation['patches'] = patchInformation
    # Return
    return scanInformation


def loadScanInformation(probabilityPath, expandPath):
    # Initialize
    information = store.loadInformation(probabilityPath)
    scanInformation = {
        'probabilities': information,
    }
    imagePath = expandPath(information['probability']['image path'])
    regionPath = expandPath(information['probability']['region path'])
    regionInformation = store.loadInformation(regionPath)
    if regionInformation:
        scanInformation['regions'] = regionInformation
    scanInformation['images'] = store.loadInformation(imagePath)
    # Return
    return scanInformation


class QueueReader(object):

    def __init__(self):
        self.queues = [store.loadQueue(x, parameter_store.convertByName) for x in glob.glob('*.queue')]
        self.queues_sampleWindows = self.filterQueues('example count per region')

    def filterQueues(self, key):
        method = lambda queue: True if key in set(sum((x.keys() for x in queue.values()), [])) else False
        return filter(method, self.queues)

    def getInformation_sampleWindows(self, name):
        for queue in self.queues_sampleWindows:
            if name in queue:
                return queue[name]
        return {}


def plotPatchPerformanceHistogram(targetPath, information):
    # Plot patch performance histogram
    if 'performance by region' in information:
        patchPerformanceByRegion = information['performance by region']
        windowPercentCorrects = patchPerformanceByRegion.values()
        pylab.figure()
        pylab.hist(windowPercentCorrects, bins=20, range=(0, 1))
        pylab.title('Patch performance histogram')
        pylab.ylabel('Region count')
        pylab.xlabel('Percent correct over windows inside region')
        pylab.savefig(targetPath)


def plotResults(results, expandPath):
    # Initialize
    plotPathByIndexByName = {}
    # For each result,
    for resultIndex, result in itertools.izip(itertools.count(1), results):
        # Initialize
        plotPathByIndexByName[resultIndex] = {}
        # If patches exist,
        if result['patches']:
            targetName = '%s_patchPerformanceHistogram.png' % resultIndex
            plotPatchPerformanceHistogram(expandPath(targetName), result['patches'])
            plotPathByIndexByName[resultIndex]['patchPerformanceByRegion'] = targetName
        # For each source patch,
        for sourceIndex, patchInformation in itertools.izip(itertools.count(1), result['sources']['patches']):
            targetName = '%s_%s_patchPerformanceHistogram.png' % (resultIndex, sourceIndex)
            plotPatchPerformanceHistogram(expandPath(targetName), patchInformation['patches'])
            plotPathByIndexByName[resultIndex]['%s_patchPerformanceByRegion' % sourceIndex] = targetName
        # Plot iteration history
        errorPacks = eval(result['classifiers']['performance']['iteration history'])
        targetName = '%s_classifierIterationHistory.png' % resultIndex
        classifier_cnn.plotIterationHistory(expandPath(targetName), errorPacks)
        plotPathByIndexByName[resultIndex]['classifierIterationHistory'] = targetName
    # Return
    return plotPathByIndexByName


# If we are running the script from the command-line,
if __name__ == '__main__':
    # Load
    hasLocations = False
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    resultFolderPath = store.makeFolderSafely('9-results')
    def expandPath(path):
        return os.path.join(resultFolderPath, path)
    print 'Loading queues...'
    queueReader = QueueReader()
    print 'Loading results...'
    results = loadResults()
    print 'Loading paths...'
    paths = loadPaths()
    print 'Plotting results...'
    plotPathByIndexByName = plotResults(results, expandPath)
    lookup = mako.lookup.TemplateLookup(directories=[os.path.join(scriptPath, 'templates')])
    def renderTemplate(templateName):
        template = lookup.get_template(templateName + '.mako')
        if templateName.startswith('multiple'):
            open(expandPath('%s.html' % templateName), 'wt').write(template.render(
                results=results, 
                plotPathByIndexByName=plotPathByIndexByName,
            ))
        else:
            for resultIndex, result in itertools.izip(itertools.count(1), results):
                open(expandPath('%s%s.html' % (templateName, resultIndex)), 'wt').write(template.render(
                    result=result, 
                    plotPathByName=plotPathByIndexByName[resultIndex],
                ))
    # Generate CSV and tables
    print 'Generating spreadsheets...'
    csvWriter = csv.writer(open(expandPath('multiple.csv'), 'wt'))
    csvWriter.writerow([
        'Result name',
        '',
        'Region performance mean',
        'Region performance standard deviation',
        'Region performance threshold',
        'Region count (scanned)',
        'Region count (bad)',
        'Region percent error',
        '',
        'Maximum diameter threshold',
        'Minimum diameter threshold',
        'Iterations per burst',
        'Evaluation radius',
        'Actual',
        'Actual not predicted',
        'Predicted',
        'Predicted not actual',
        'AnP/A',
        'PnA/P',
        '',
        'Window count',
        'Actual true',
        'Actual true predicted false',
        'Predicted true',
        'Predicted true actual false',
        'False positive error',
        'False negative error',
        'Percent error',
        'Scanning time in minutes',
        'Window length',
        'Window interval',
        'Image name',
        'Image percent coverage',
        'Region name',
        'Region percent coverage',
        'Region offset',
        'Classifier name',
        '',
        'Test set size',
        'Actual true',
        'Actual true predicted false',
        'Predicted true',
        'Predicted true actual false',
        'Test error',
        'False positive test error',
        'False negative test error',
        'Training time in minutes',
        'Feature module name',
        'Feature class name',
        'Connection table0',
        'Connection table1',
        'Classifier module name',
        'Length0',
        'Ratio0',
        'Length1',
        'Ratio1',
        'Hidden count',
        'Dataset name',
        '',
        'Positive fraction',
        'Maximum training size',
        'Maximum test size',
        'Training positive',
        'Training negative',
        'Training total',
        'Test positive',
        'Test negative',
        'Test total',
        'Window length',
        'Window names',
        'Patch names',
        '',
        'Mean shift count',
        'Mean multispectral pixel shift value',
    ])
    preparedResults = []
    for result in results:
        # Initialize
        resultName = result['name']
        # Prepare patches
        patchInformation = result['patches']
        if patchInformation and 'performance by region' in patchInformation:
            patchPerformance = patchInformation['performance']
            patchParameters = patchInformation['patches']
            patchPerformanceByRegion = patchInformation['performance by region']
            patchRegionPerformances = [float(x) for x in patchPerformanceByRegion.values()]

            patch_performanceMean = numpy.mean(patchRegionPerformances) * 100
            patch_performanceStandardDeviation = numpy.std(patchRegionPerformances) * 100
            patch_performanceThreshold = float(patchParameters['minimum percent correct']) * 100
            patch_scannedRegionCount = patchPerformance['region count']
            patch_badRegionCount = patchPerformance['bad region count']
            patch_percentError = (1 - float(patchPerformance['percent correct'])) * 100
        else:
            patch_performanceMean = None
            patch_performanceStandardDeviation = None
            patch_performanceThreshold = None
            patch_scannedRegionCount = None
            patch_badRegionCount = None
            patch_percentError = None
        # Prepare locations
        if 'locations' in result and 'performance' in result['locations']:
            locationInformation = result['locations']
            locationPerformance = locationInformation['performance']
            locationParameters = locationInformation['parameters']
            actual = int(locationPerformance['actual count'])
            actualNotPredicted = int(locationPerformance['actual not predicted count'])
            predicted = int(locationPerformance['predicted count'])
            predictedNotActual = int(locationPerformance['predicted not actual count'])

            location_maximumDiameterThreshold = locationParameters['maximum diameter in meters']
            location_minimumDiameterThreshold = locationParameters['minimum diameter in meters']
            location_iterationsPerBurst = locationParameters['iteration count per burst']
            location_evaluationRadius = locationParameters['evaluation radius in meters']
            location_actual = actual
            location_actualNotPredicted = actualNotPredicted
            location_predicted = predicted
            location_predictedNotActual = predictedNotActual
            location_actualNotPredictedOverActual = 100 * actualNotPredicted / float(actual) if actual else 0
            location_predictedNotActualOverPredicted = 100 * predictedNotActual / float(predicted) if predicted else 0
            hasLocations = True
        else:
            location_maximumDiameterThreshold = None
            location_minimumDiameterThreshold = None
            location_iterationsPerBurst = None
            location_evaluationRadius = None
            location_actual = None
            location_actualNotPredicted = None
            location_predicted = None
            location_predictedNotActual = None
            location_actualNotPredictedOverActual = None
            location_predictedNotActualOverPredicted = None
        # Prepare scans
        scanInformation = result['scans']
        scanProbabilities = scanInformation['probabilities']
        scanProbabilitiesPerformance = scanProbabilities['performance']
        scanProbabilitiesParameters = scanProbabilities['parameters']
        scanProbabilitiesClassifier = scanProbabilities['classifier']
        scanProbabilitiesProbability = scanProbabilities['probability']

        scan_windowCount = scanProbabilitiesPerformance['window count']
        scan_actualTrue = scanProbabilitiesPerformance['actual true']
        scan_actualTruePredictedFalse = scanProbabilitiesPerformance['actual true predicted false']
        scan_actualTruePredictedTrue = scanProbabilitiesPerformance['actual true predicted true']
        scan_actualFalse = scanProbabilitiesPerformance['actual false']
        scan_predictedTrue = scanProbabilitiesPerformance['predicted true']
        scan_predictedTrueActualFalse = scanProbabilitiesPerformance['actual false predicted true']
        scan_falsePositiveError = scanProbabilitiesPerformance['false positive error']
        scan_falseNegativeError = scanProbabilitiesPerformance['false negative error']
        scan_percentError = scanProbabilitiesPerformance['percent error']
        scan_elapsedTimeInMinutes = float(scanProbabilitiesPerformance.get('elapsed time in seconds', 0)) / 60

        scanWindowLength = float(scanProbabilitiesParameters['window length in meters'])
        if 'region name' in scanProbabilitiesProbability:
            scanRegions = scanInformation['regions']
            scanRegionsParameters = scanRegions['parameters']
            scanRegionName = scanProbabilitiesProbability['region name']
            scanRegionCoverage = float(scanRegionsParameters['coverage fraction']) * 100
            scanRegionOffset = scanRegionsParameters['coverage offset']
        else:
            scanRegionName = None
            scanRegionCoverage = None
            scanRegionOffset = None

        scan_windowLength = scanWindowLength
        scan_windowInterval = scanWindowLength / float(scanProbabilitiesParameters['scan ratio'])
        scan_imageName = scanProbabilitiesProbability['image name']
        scan_imageCoverage = scanProbabilitiesParameters.get('coverage fraction')
        scan_regionName = scanRegionName
        scan_regionCoverage = scanRegionCoverage
        scan_regionOffset = scanRegionOffset
        scan_classifierName = scanProbabilitiesClassifier['name']
        # Prepare classifiers
        classifierInformation = result['classifiers']
        classifierWindows = classifierInformation['windows']
        classifierPerformance = classifierInformation['performance']
        classifierParameters = classifierInformation['parameters']
        classifierDataset = classifierInformation['dataset']

        classifier_testSetSize = classifierPerformance['test set size']
        classifier_actualTrue = classifierPerformance['actual true']
        classifier_actualTruePredictedFalse = classifierPerformance['actual true predicted false']
        classifier_predictedTrue = classifierPerformance['predicted true']
        classifier_predictedTrueActualFalse = classifierPerformance['actual false predicted true']
        classifier_testError = classifierPerformance['test error']
        classifier_falsePositiveTestError = classifierPerformance['false positive test error']
        classifier_falseNegativeTestError = classifierPerformance['false negative test error']
        classifier_elapsedTimeInMinutes = float(classifierPerformance.get('elapsed time in seconds', 0)) / 60
        classifier_featureModuleName = classifierParameters['feature module name']
        classifier_featureClassName = classifierParameters['feature class name']
        classifier_connectionTable0Path = classifierParameters['connection table0 path']
        classifier_connectionTable1Path = classifierParameters['connection table1 path']
        classifier_classifierModuleName = classifierParameters['classifier module name']
        classifier_length0 = classifierParameters['length0']
        classifier_ratio0 = classifierParameters['ratio0']
        classifier_length1 = classifierParameters['length1']
        classifier_ratio1 = classifierParameters['ratio1']
        classifier_hiddenCount = classifierParameters['hidden count']
        classifier_datasetName = classifierDataset['name']
        # Prepare datasets
        datasetInformation = result['datasets']
        datasetTrainingSet = datasetInformation['training set']
        datasetTestSet = datasetInformation['test set']
        datasetParameters = datasetInformation['parameters']
        datasetWindows = datasetInformation['windows']
        datasetSources = datasetInformation['sources']

        dataset_positiveFraction = datasetParameters['positive fraction']
        dataset_maximumTrainingSize = datasetParameters['training size']
        dataset_maximumTestSize = datasetParameters['test size']
        dataset_trainingPositive = datasetTrainingSet['positive']
        dataset_trainingNegative = datasetTrainingSet['negative']
        dataset_trainingTotal = datasetTrainingSet['total']
        dataset_testPositive = datasetTestSet['positive']
        dataset_testNegative = datasetTestSet['negative']
        dataset_testTotal = datasetTestSet['total']
        dataset_windowLength = datasetWindows['window length in meters']
        dataset_windowNames = ', '.join(filter(lambda x: x.strip(), datasetSources['window names'].splitlines()))
        dataset_patchNames = ', '.join(filter(lambda x: x.strip(), datasetSources['patch names'].splitlines()))
        # Prepare sources
        sources = result['sources']['windows']

        source_meanShiftCount = numpy.mean([x['windows']['parameters'].get('shift count', 0) for x in sources])
        source_meanMultispectralPixelShiftValue = numpy.mean([x['windows']['parameters'].get('multispectral pixel shift value', 0) for x in sources])
        # Assemble
        row = [
            resultName,
            '',
            patch_performanceMean,
            patch_performanceStandardDeviation,
            patch_performanceThreshold,
            patch_scannedRegionCount,
            patch_badRegionCount,
            patch_percentError,
            '',
            location_maximumDiameterThreshold,
            location_minimumDiameterThreshold,
            location_iterationsPerBurst,
            location_evaluationRadius,
            location_actual,
            location_actualNotPredicted,
            location_predicted,
            location_predictedNotActual,
            location_actualNotPredictedOverActual,
            location_predictedNotActualOverPredicted,
            '',
            scan_windowCount,
            scan_actualTrue,
            scan_actualTruePredictedFalse,
            scan_predictedTrue,
            scan_predictedTrueActualFalse,
            scan_falsePositiveError,
            scan_falseNegativeError,
            scan_percentError,
            scan_elapsedTimeInMinutes,
            scan_windowLength,
            scan_windowInterval,
            scan_imageName,
            scan_imageCoverage,
            scan_regionName,
            scan_regionCoverage,
            scan_regionOffset,
            scan_classifierName,
            '',
            classifier_testSetSize,
            classifier_actualTrue,
            classifier_actualTruePredictedFalse,
            classifier_predictedTrue,
            classifier_predictedTrueActualFalse,
            classifier_testError,
            classifier_falsePositiveTestError,
            classifier_falseNegativeTestError,
            classifier_elapsedTimeInMinutes,
            classifier_featureModuleName,
            classifier_featureClassName,
            classifier_connectionTable0Path,
            classifier_connectionTable1Path,
            classifier_classifierModuleName,
            classifier_length0,
            classifier_ratio0,
            classifier_length1,
            classifier_ratio1,
            classifier_hiddenCount,
            classifier_datasetName,
            '',
            dataset_positiveFraction,
            dataset_maximumTrainingSize,
            dataset_maximumTestSize,
            dataset_trainingPositive,
            dataset_trainingNegative,
            dataset_trainingTotal,
            dataset_testPositive,
            dataset_testNegative,
            dataset_testTotal,
            dataset_windowLength,
            dataset_windowNames,
            dataset_patchNames,
            '',
            source_meanShiftCount,
            source_meanMultispectralPixelShiftValue,
        ]
        # Store
        preparedResults.append({
            'resultName': resultName,
            'patch_performanceMean': patch_performanceMean,
            'patch_performanceStandardDeviation': patch_performanceStandardDeviation,
            'patch_performanceThreshold': patch_performanceThreshold,
            'patch_scannedRegionCount': patch_scannedRegionCount,
            'patch_badRegionCount': patch_badRegionCount,
            'patch_percentError': patch_percentError,
            'location_maximumDiameterThreshold': location_maximumDiameterThreshold,
            'location_minimumDiameterThreshold': location_minimumDiameterThreshold,
            'location_iterationsPerBurst': location_iterationsPerBurst,
            'location_evaluationRadius': location_evaluationRadius,
            'location_actual': location_actual,
            'location_actualNotPredicted': location_actualNotPredicted,
            'location_predicted': location_predicted,
            'location_predictedNotActual': location_predictedNotActual,
            'location_actualNotPredictedOverActual': location_actualNotPredictedOverActual,
            'location_predictedNotActualOverPredicted': location_predictedNotActualOverPredicted,
            'scan_windowCount': scan_windowCount,
            'scan_actualTrue': scan_actualTrue,
            'scan_actualTruePredictedFalse': scan_actualTruePredictedFalse,
            'scan_actualFalse': scan_actualFalse,
            'scan_actualTruePredictedTrue': scan_actualTruePredictedTrue,
            'scan_predictedTrue': scan_predictedTrue,
            'scan_predictedTrueActualFalse': scan_predictedTrueActualFalse,
            'scan_falsePositiveError': scan_falsePositiveError,
            'scan_falseNegativeError': scan_falseNegativeError,
            'scan_percentError': scan_percentError,
            'scan_elapsedTimeInMinutes': scan_elapsedTimeInMinutes,
            'scan_windowLength': scan_windowLength,
            'scan_windowInterval': scan_windowInterval,
            'scan_imageName': scan_imageName,
            'scan_imageCoverage': scan_imageCoverage,
            'scan_regionName': scan_regionName,
            'scan_regionCoverage': scan_regionCoverage,
            'scan_regionOffset': scan_regionOffset,
            'scan_classifierName': scan_classifierName,
            'classifier_testSetSize': classifier_testSetSize,
            'classifier_actualTrue': classifier_actualTrue,
            'classifier_actualTruePredictedFalse': classifier_actualTruePredictedFalse,
            'classifier_predictedTrue': classifier_predictedTrue,
            'classifier_predictedTrueActualFalse': classifier_predictedTrueActualFalse,
            'classifier_testError': classifier_testError,
            'classifier_falsePositiveTestError': classifier_falsePositiveTestError,
            'classifier_falseNegativeTestError': classifier_falseNegativeTestError,
            'classifier_elapsedTimeInMinutes': classifier_elapsedTimeInMinutes,
            'classifier_featureModuleName': classifier_featureModuleName,
            'classifier_featureClassName': classifier_featureClassName,
            'classifier_connectionTable0Path': classifier_connectionTable0Path,
            'classifier_connectionTable1Path': classifier_connectionTable1Path,
            'classifier_classifierModuleName': classifier_classifierModuleName,
            'classifier_length0': classifier_length0,
            'classifier_ratio0': classifier_ratio0,
            'classifier_length1': classifier_length1,
            'classifier_ratio1': classifier_ratio1,
            'classifier_hiddenCount': classifier_hiddenCount,
            'classifier_datasetName': classifier_datasetName,
            'dataset_positiveFraction': dataset_positiveFraction,
            'dataset_maximumTrainingSize': dataset_maximumTrainingSize,
            'dataset_maximumTestSize': dataset_maximumTestSize,
            'dataset_trainingPositive': dataset_trainingPositive,
            'dataset_trainingNegative': dataset_trainingNegative,
            'dataset_trainingTotal': dataset_trainingTotal,
            'dataset_testPositive': dataset_testPositive,
            'dataset_testNegative': dataset_testNegative,
            'dataset_testTotal': dataset_testTotal,
            'dataset_windowLength': dataset_windowLength,
            'dataset_windowNames': dataset_windowNames,
            'dataset_patchNames': dataset_patchNames,
            'source_meanShiftCount': source_meanShiftCount,
            'source_meanMultispectralPixelShiftValue': source_meanMultispectralPixelShiftValue,
        })
        # Write
        csvWriter.writerow(row)
    # Render tables
    open(expandPath('latex_scan.tex'), 'wt').write(lookup.get_template('latex_scan.mako').render(preparedResults=preparedResults))
    if hasLocations:
        open(expandPath('latex_location.tex'), 'wt').write(lookup.get_template('latex_location.mako').render(preparedResults=preparedResults))
    # Render templates
    print 'Rendering templates...'
    try:
        renderTemplate('single_ugly')
        renderTemplate('single_pretty')
        # renderTemplate('multiple_ugly')
        renderTemplate('multiple_pretty')
        open(expandPath('paths.html'), 'wt').write(lookup.get_template('paths.mako').render(paths=paths))
    except:
        print mako.exceptions.text_error_template().render()
    # Plot roc curves
    # pylab.figure()
    # scan_tprs = [int(x['scan_actualTruePredictedTrue']) / float(x['scan_actualTrue']) for x in preparedResults]
    # scan_fprs = [int(x['scan_predictedTrueActualFalse']) / float(x['scan_actualFalse']) for x in preparedResults]
    # pylab.plot(scan_fprs, scan_tprs, '*')
    # pylab.title('Window ROC curve')
    # pylab.ylabel('True positive rate')
    # pylab.xlabel('False positive rate')
    # pylab.axis([0, 1, 0, 1])
    # pylab.savefig('9-results/roc.png')
    # Initialize
    radius = 25
    radiusInfos = []
    length = 50
    lengthInfos = []
    scanInformationByPath = loadInformations('probabilities', '.')
    # For each scanInformation,
    for scanFolderPath, scanInformation in scanInformationByPath.iteritems():
        # Initialize
        scanPath = os.path.join(scanFolderPath, folder_store.fileNameByFolderName['probabilities'])
        # Evaluate with radius
        radiusInfos.append(evaluation_process.evaluateWindowsByRadius(scanPath, radius))
        # Evaluate with length
        lengthInfos.append(evaluation_process.evaluateWindowsByLength(scanPath, length))
    # Plot with radius
    pylab.figure()
    pylab.plot([x['recall'] for x in radiusInfos], [x['precision'] for x in radiusInfos], '*')
    pylab.title('Evaluation of scan using relative circles (circle radius of %s meters)' % radius)
    pylab.ylabel('Precision (Percent of predicted that are actual)')
    pylab.xlabel('Recall (Percent of actual that are predicted)')
    pylab.axis([0, 1, 0, 1])
    pylab.savefig(expandPath('scanEvaluationByRadius.png'))
    # Plot with length
    pylab.figure()
    pylab.plot([x['false positive rate'] for x in lengthInfos], [x['true positive rate'] for x in lengthInfos], '*')
    pylab.title('Evaluation of scan using absolute rectangles (rectangle length of %s meters)' % length)
    pylab.ylabel('True positive rate')
    pylab.xlabel('False positive rate')
    pylab.axis([0, 1, 0, 1])
    pylab.savefig(expandPath('scanEvaluationByLength.png'))
