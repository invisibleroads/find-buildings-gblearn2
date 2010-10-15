# Import system modules
import os
import re
import csv
import glob
import numpy
import shutil
import subprocess
import matplotlib; matplotlib.use('Agg')
import pylab
import tempfile
# Import custom modules
import view
import store
import classifier
import folder_store
import evaluation_process


# Core

relevantParameterNames = (
    'ratio range',
    'kernel range',
    'which layer combination',
    'connection table0 path',
    'connection table1 path',
    'hidden count',
    'iteration count',
    'length0',
    'length1',
    'ratio0',
    'ratio1',
)

def saveSamples(sampleDataset, sampleIDs, featureSet):
    # Initialize
    sampleCount = len(sampleIDs)
    sampleDatasetPath = sampleDataset.getDatasetPath()
    sampleInformation = {
        'source dataset': {
            'path': sampleDatasetPath,
            'sample ids': ' '.join(str(x) for x in sampleIDs),
        },
        'feature': {
            'module name': featureSet.__module__,
            'class name': featureSet.__class__.__name__,
        }
    }
    targetSampleName = '%s-count%s-min%s' % (folder_store.getFolderName(sampleDatasetPath), sampleCount, min(sampleIDs))
    targetSamplePath = os.path.join(store.makeFolderSafely(os.path.join(store.temporaryPath, 'cnn_datasets')), targetSampleName)
    # If targetDatasetPath exists, return
    if store.loadInformation(targetSamplePath) == sampleInformation: 
        print 'Using existing samples...\n\ttargetSamplePath = ' + targetSamplePath
        return targetSamplePath
    # Save
    print 'Saving samples...\n\ttargetSamplePath = ' + targetSamplePath
    sampleGenerator = makeSampleLabelGeneratorFromSampleDataset(sampleDataset, sampleIDs, featureSet)
    sampleFile, labelFile = [open(x, 'wt') for x in makeSampleLabelPaths(targetSamplePath)]
    for sampleIndex, (sample, label) in enumerate(sampleGenerator): 
        # If we are starting, write header
        if sampleIndex == 0:
            sampleFile.write(makeLushMatrixHeaderFromPart(sample, sampleCount))
            labelFile.write(makeLushMatrixHeaderFromPart(label, sampleCount))
        # Write content
        sampleFile.write(makeLushMatrixContent(sample))
        labelFile.write(makeLushMatrixContent(label))
        if sampleIndex % 100 == 0: 
            view.printPercentUpdate(sampleIndex + 1, sampleCount)
    view.printPercentFinal(sampleCount)
    # Return
    labelFile.close(); sampleFile.close()
    store.saveInformation(targetSamplePath, sampleInformation)
    return targetSamplePath

def makeSampleLabelGeneratorFromSampleDataset(sampleDataset, sampleIDs, featureSet):
    for sampleID in sampleIDs:
        hasRoof, geoCenter, multispectralWindow, panchromaticWindow = sampleDataset.getSample(sampleID)
        yield featureSet.extractFeatures(multispectralWindow, panchromaticWindow), hasRoof

def makeSampleGeneratorFromLushDataset(filePath):
    # Set paths
    samplePath = makeSampleLabelPaths(filePath)[0]
    # Initialize
    sampleFile = open(samplePath)
    header = sampleFile.next()
    sampleShape = [int(x) for x in header.split()[3:]]
    sampleSize = numpy.product(sampleShape)
    terms = []
    # For each line,
    for line in sampleFile:
        # Extend terms
        terms.extend(float(x) for x in line.split())
        # If we have enough terms,
        while len(terms) >= sampleSize:
            # Yield sample
            yield numpy.array(terms[:sampleSize]).reshape(sampleShape)
            # Set terms
            terms = terms[sampleSize:]

def makeLabelGeneratorFromLushDataset(filePath):
    # Set paths
    labelPath = makeSampleLabelPaths(filePath)[1]
    # Initialize
    labelFile = open(labelPath)
    header = labelFile.next()
    terms = []
    # For each line,
    for line in labelFile:
        # Extend terms
        terms.extend(int(x) for x in line.split())
        # Pop each term
        for termIndex in xrange(len(terms)):
            yield terms.pop(0)

def loadLabels(filePath):
    return numpy.array([x for x in makeLabelGeneratorFromLushDataset(filePath)])

@store.recordElapsedTime
def train(targetClassifierPath, trainingPath, testPath, parameterByName):
    # Set paths
    temporaryFolder = tempfile.mkdtemp()
    trainingSamplePath, trainingLabelPath = makeSampleLabelPaths(trainingPath)
    testSamplePath, testLabelPath = makeSampleLabelPaths(testPath)
    # Make layer combinations
    ratioRange = store.unstringifyFloatList(parameterByName['ratio range'])
    kernelRange = store.unstringifyIntegerList(parameterByName['kernel range'])
    samplePixelLength = getSamplePixelLength(testPath)
    layerCombinations = makeLayerCombinations(samplePixelLength, ratioRange, kernelRange)
    length0, ratio0, length1, ratio1 = layerCombinations[parameterByName['which layer combination']]
    # Convert connection tables if necessary
    connectionTable0Path = verifyConnectionTable(parameterByName['connection table0 path'])
    connectionTable1Path = verifyConnectionTable(parameterByName['connection table1 path'])
    # Run
    timestamp = store.makeTimestamp()
    runLush('trainClassifier', trainingSamplePath, trainingLabelPath, testSamplePath, testLabelPath,
        length0, ratio0, connectionTable0Path,
        length1, ratio1, connectionTable1Path,
        parameterByName['hidden count'], parameterByName['iteration count'], 
        os.path.join(temporaryFolder, timestamp))
    errorPacks = getClassifierPacksByTimestamp(temporaryFolder, timestamp)
    # Save the best classifier
    bestTestPercentError, bestTrainingPercentError, bestIterationIndex, bestClassifierPath = errorPacks[0]
    parameterByName.update(length0=length0, ratio0=ratio0, length1=length1, ratio1=ratio1)
    shutil.copy(bestClassifierPath, targetClassifierPath)
    shutil.rmtree(temporaryFolder)
    # Evaluate
    resultByName = evaluate(targetClassifierPath, testPath)
    resultByName['iteration index'] = bestIterationIndex
    resultByName['iteration history'] = errorPacks
    resultByName['sample pixel length'] = samplePixelLength
    resultByName['layer combinations'] = layerCombinations
    resultByName['layer combination count'] = len(layerCombinations)
    # Plot
    plotIterationHistory(targetClassifierPath, errorPacks)
    # Return
    return resultByName

def evaluate(classifierPath, testPath):
    actualLabels = loadLabels(testPath)
    predictedLabels = test(classifierPath, testPath)
    resultByName = evaluation_process.evaluateClassifier(actualLabels, predictedLabels, 'Convolutional neural network')
    return resultByName

def test(classifierPath, testPath):
    # Set paths
    testSamplePath = makeSampleLabelPaths(testPath)[0]
    # Run
    standardOutput = runLushWithPipes('classifyFile', classifierPath, testSamplePath)
    # Load predictedLabels
    lines = str(standardOutput).splitlines()
    predictedLabels = numpy.array([int(pattern_classifierOutput.match(x).group(1)) for x in lines])
    # Return
    return numpy.array(predictedLabels)

def load(classifierPath):
    # Load featureSet
    classifierInformation = classifier.Information(classifierPath)
    featureModuleName = classifierInformation.getFeatureModuleName()
    featureModule = store.getLibraryModule(featureModuleName)
    featureClassName = classifierInformation.getFeatureClassName()
    featureClass = getattr(featureModule, featureClassName)
    featureSet = featureClass()
    # Start classifierProcess
    classifierProcess = runLushProcess('classifyStream', classifierPath)
    # Define
    def classify(imageContent=None, matrixContent=None):
        if imageContent and not matrixContent:
            # Extract matrix
            multispectralWindow, panchromaticWindow = imageContent
            matrix = featureSet.extractFeatures(multispectralWindow, panchromaticWindow)
            matrixContent = makeLushMatrixDirectly(matrix)
        # Classify
        classifierProcess.stdin.write(matrixContent + '\n')
        line = classifierProcess.stdout.readline().rstrip()
        label, probability = pattern_classifierOutput.match(line).groups()
        # Return
        return int(label), float(probability)
    # Return
    return classify


# Set

pattern_classifierOutput = re.compile('([^\s]+) ([^\s]+)')


# Get

def getConnectionMap(connectionMapPath):
    # Open
    connectionMapFile = open(connectionMapPath, 'rt')
    # Ignore the first line
    line = connectionMapFile.next()
    # Get everything else
    terms = []
    for line in connectionMapFile:
        terms.extend(int(float(x)) for x in line.split())
    # Store every two numbers as a connection
    firsts = [terms[x] for x in xrange(0, len(terms), 2)]
    seconds = [terms[x] for x in xrange(1, len(terms), 2)]
    # Get information
    inputMapCount = max(firsts) + 1
    outputMapCount = max(seconds) + 1
    # Return
    return inputMapCount, outputMapCount, zip(firsts, seconds)

def getSamplePixelLength(stumpPath):
    # Set paths
    samplePath = makeSampleLabelPaths(stumpPath)[0]
    # Get the first line
    terms = open(samplePath, 'rt').readline().split()
    # Get dimensions
    datasetPixelHeight = int(terms[-2])
    datasetPixelWidth = int(terms[-1])
    # Make sure that we have a square
    assert datasetPixelHeight == datasetPixelWidth
    # Return
    return datasetPixelHeight

def getSampleCount(stumpPath):
    # Set paths
    samplePath = makeSampleLabelPaths(stumpPath)[0]
    # Get the first line
    terms = open(samplePath, 'rt').readline().split()
    # Return
    return int(terms[2])

def getClassifierPacksByTimestamp(classifierFolderPath, timestamp):
    # Initialize
    pattern_classifierName = re.compile('x_TRAIN_AGx_SZx_ENx_PCx_PEx_PRx_TEST_AGx_SZx_ENx_PCx_PEx_PRx.net'.replace('x', '([.\d]+)'))
    errorPacks = []
    # Get classifierNames with the given timestamp
    classifierPaths = glob.glob(os.path.join(classifierFolderPath, timestamp + '*.net'))
    # For each classifierPath,
    for classifierPath in classifierPaths:
        # Extract information
        match = pattern_classifierName.match(store.extractFileName(classifierPath))
        # Extract
        classifierTimestamp, trainingAge, trainingSize, trainingEnergy, trainingPercentCorrect, trainingPercentError, trainingPercentRejected, testAge, testSize, testEnergy, testPercentCorrect, testPercentError, testPercentRejected = match.groups()
        iterationIndex = int(trainingAge) / int(trainingSize)
        trainingPercentError = float(trainingPercentError)
        testPercentError = float(testPercentError)
        # Append
        errorPacks.append((testPercentError, trainingPercentError, iterationIndex, classifierPath))
    # Return
    return sorted(errorPacks)


# Plot

def plotIterationHistory(targetPath, iterationHistoryVsTestError):
    # Sort by iterationIndex
    iterationHistoryVsIndex = [(iterationIndex, testError, trainingError) for testError, trainingError, iterationIndex, classifierPath in iterationHistoryVsTestError]
    iterationHistoryVsIndex.sort()
    # Assemble
    testErrors = [x[1] for x in iterationHistoryVsIndex]
    trainingErrors = [x[2] for x in iterationHistoryVsIndex]
    iterationIndices = [x[0] for x in iterationHistoryVsIndex]
    # Plot
    pylab.figure()
    pylab.hold(True)
    pylab.plot(iterationIndices, testErrors, 'r')
    pylab.plot(iterationIndices, trainingErrors, 'b')
    pylab.legend(['Validation Test Error', 'Validation Training Error'])
    pylab.title('Iteration History')
    pylab.xlabel('Iteration Index')
    pylab.ylabel('Percent Error')
    pylab.savefig(store.replaceFileExtension(targetPath, 'png'))


# Make

def makeSampleLabelPaths(basePath):
    return basePath + '-samples', basePath + '-labels'

def makeLushMatrixDirectly(matrix):
    return '[%s]' % ' '.join('[%s]' % ' '.join(str(column) for column in row) for row in matrix)

def makeLushMatrix(matrix):
    return makeLushMatrixHeaderFromWhole(matrix) + makeLushMatrixContent(matrix)

def makeLushMatrixHeaderFromWhole(wholeMatrix):
    wholeMatrix = numpy.array(wholeMatrix)
    return '.MAT %s %s\n' % (wholeMatrix.ndim, ' '.join([str(x) for x in wholeMatrix.shape]))

def makeLushMatrixHeaderFromPart(partMatrix, partCount):
    partMatrix = numpy.array(partMatrix)
    return '.MAT %s %s %s\n' % (partMatrix.ndim + 1, partCount, ' '.join([str(x) for x in partMatrix.shape]))

def makeLushMatrixContent(matrix):
    matrix = numpy.array(matrix)
    return ' '.join([str(x) for x in matrix.flatten()]) + '\n'

def makeLayerCombinations(pixelLength, ratioRange, kernelRange):
    # Initialize
    combinations = []
    # Show feedback
    for ratio0 in ratioRange:
        for ratio1 in ratioRange:
            for length0 in kernelRange:
                for length1 in kernelRange:
                    sum0 = pixelLength - length0 + 1
                    if sum0 % ratio0 == 0:
                        layer0 = sum0 / ratio0
                        if layer0 > 0:
                            sum1 = layer0 - length1 + 1
                            if sum1 % ratio1 == 0:
                                layer1 = sum1 / ratio1
                                if layer1 > 0: 
                                    combinations.append((length0, ratio0, length1, ratio1))
    # Return
    return combinations


# Run

DIRECTORY = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lush')
PIPE = subprocess.PIPE

def runLush(scriptName, *arguments):
    scriptPath = os.path.join(DIRECTORY, store.replaceFileExtension(scriptName, 'lsh'))
    terms = ['lush', scriptPath, DIRECTORY] + [str(x) for x in arguments]
    returnCode = subprocess.call(terms)
    if returnCode != 1: 
        raise ClassifierError(scriptPath)

def runLushProcess(scriptName, *arguments):
    scriptPath = os.path.join(DIRECTORY, store.replaceFileExtension(scriptName, 'lsh'))
    terms = ['lush', scriptPath, DIRECTORY] + [str(x) for x in arguments]
    return subprocess.Popen(terms, stdin=PIPE, stdout=PIPE)

def runLushWithPipes(scriptName, *arguments, **keywordArguments):
    # Initialize
    scriptPath = os.path.join(DIRECTORY, store.replaceFileExtension(scriptName, 'lsh'))
    terms = ['lush', scriptPath, DIRECTORY] + [str(x) for x in arguments]
    standardError = True
    errorCount = 0
    errorLimit = 5
    standardInput = keywordArguments.get('standardInput')
    # While there is standardError,
    while standardError:
        # Try again
        if standardInput: 
            process = subprocess.Popen(terms, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            standardOutput, standardError = process.communicate(standardInput)
        else:
            process = subprocess.Popen(terms, stdout=PIPE, stderr=PIPE)
            standardOutput, standardError = process.communicate()
        # If we have an error,
        if standardError:
            # Count
            errorCount += 1
            print 'Failed (%d/%d): %s' % (errorCount, errorLimit, store.extractFileBaseName(scriptPath))
            if errorCount >= errorLimit: raise ClassifierError(standardError)
    # Return
    return standardOutput


# Verify

def verifyConnectionTable(connectionTablePath):
    # Get extension
    extension = os.path.splitext(connectionTablePath)[1]
    # If it is a CSV,
    if extension == '.csv':
        # Read connections from CSV
        connections = []
        for rowIndex, row in enumerate(csv.reader(open(connectionTablePath))):
            for columnIndex, column in enumerate(row):
                if column.strip():
                    connections.append((rowIndex, columnIndex))
        # Save matrix for Lush
        connectionTablePath = store.replaceFileExtension(connectionTablePath, 'map')
        open(connectionTablePath, 'wt').write(makeLushMatrix(connections))
    # Return
    return connectionTablePath

def makeLushMatrixDirectly(matrix):
    return '[%s]' % ' '.join('[%s]' % ' '.join(str(column) for column in row) for row in matrix)

def makeLushMatrix(matrix):
    return makeLushMatrixHeaderFromWhole(matrix) + makeLushMatrixContent(matrix)

def makeLushMatrixHeaderFromWhole(wholeMatrix):
    wholeMatrix = numpy.array(wholeMatrix)
    return '.MAT %s %s\n' % (wholeMatrix.ndim, ' '.join([str(x) for x in wholeMatrix.shape]))

def makeLushMatrixHeaderFromPart(partMatrix, partCount):
    partMatrix = numpy.array(partMatrix)
    return '.MAT %s %s %s\n' % (partMatrix.ndim + 1, partCount, ' '.join([str(x) for x in partMatrix.shape]))

# Error

class ClassifierError(Exception): 
    pass
