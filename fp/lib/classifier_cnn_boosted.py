# Import system modules
import os
import glob
import numpy
import shutil
import itertools
import tempfile
# Import custom modules
import view
import store
import evaluation_process
import classifier_cnn as classifier


# Core

relevantParameterNames = classifier.relevantParameterNames + ('boost count',)

def saveSamples(sampleDatabase, sampleIDs, featureSet):
    return classifier.saveSamples(sampleDatabase, sampleIDs, featureSet)

@store.recordElapsedTime
def train(targetClassifierPath, trainingPath, testPath, parameterByName):
    # Set paths
    store.makeFolderSafely(targetClassifierPath)
    # Count the number of training samples
    trainingCount = classifier.getSampleCount(trainingPath)
    # Initialize weights uniformly over training samples
    sampleWeights = numpy.array([1 / float(trainingCount)] * trainingCount)
    # Initialize
    alphas = []; boostCount = parameterByName['boost count']
    # For each boost,
    for boostIndex in xrange(boostCount):
        # Show feedback
        print '--- Boosting %d/%d ---' % (boostIndex + 1, boostCount)
        # Normalize sampleWeights
        sampleWeights = sampleWeights / float(sum(sampleWeights))
        # Weight samples
        weightedTrainingPath, sampleMultipliers = weightSamples(trainingPath, sampleWeights)
        # Train weak classifier
        weakClassifierPath = os.path.join(targetClassifierPath, 'weak%d' % boostIndex)
        weakResultByName = classifier.train(weakClassifierPath, weightedTrainingPath, testPath, parameterByName)
        shutil.rmtree(os.path.split(weightedTrainingPath)[0])
        # Test weak classifier on training set
        predictedLabels = classifier.test(weakClassifierPath, trainingPath)
        actualLabels = classifier.loadLabels(trainingPath)
        errorDistribution = predictedLabels != actualLabels
        # Compute training error weighted according to sampleWeights
        weightedError = numpy.dot(sampleWeights, errorDistribution)
        # Prevent zero division or zero log
        if weightedError == 0: weightedError = 1e-9
        elif weightedError == 1: weightedError = 1 - 1e-9
        # Get alpha from training error
        alpha = 0.5 * numpy.log(float(1 - weightedError) / weightedError)
        coefficients = [numpy.exp(alpha) if isWrong else numpy.exp(-alpha) for isWrong in errorDistribution]
        # Save weakClassifier performance
        print 'weighted training error = %s' % (100 * weightedError)
        print 'alpha = %s' % alpha
        weakResultByName['alpha'] = alpha
        weakResultByName['weighted training error'] = weightedError
        weakResultByName['sample multipliers'] = ' '.join(str(x) for x in sampleMultipliers)
        weakResultByName['error distribution'] = ''.join(str(int(x)) for x in errorDistribution)
        saveWeakClassifierInformation(weakClassifierPath, trainingPath, testPath, parameterByName, {'performance': weakResultByName})
        # Update sampleWeights
        sampleWeights = coefficients * sampleWeights
        # Append
        alphas.append(alpha)
    # Save classifier
    save(targetClassifierPath, alphas)
    # Return evaluation
    return evaluate(targetClassifierPath, testPath)

def evaluate(classifierPath, testPath):
    # Evaluate whole
    actualLabels = classifier.loadLabels(testPath)
    predictedLabels = test(classifierPath, testPath)
    resultByName = evaluation_process.evaluateClassifier(actualLabels, predictedLabels, 'Boosted convolutional neural network')
    # Evaluate parts
    for weakClassifierPath in glob.glob(os.path.join(classifierPath, 'weak*.info')):
        weakName = store.extractFileBaseName(weakClassifierPath)
        weakClassifierInformation = store.loadInformation(weakClassifierPath)
        resultByName[weakName] = weakClassifierInformation['performance']
    # Return
    return resultByName

def test(classifierPath, testPath):
    # Initialize
    alphas, weakClassifierPaths = loadAlphaPaths(classifierPath)
    # Get results so that each row corresponds to a weak classifier
    classifierResults = [classifier.test(x, testPath) for x in weakClassifierPaths]
    # Rearrange results so that each row corresponds to a sample
    sampleResults = numpy.array(classifierResults).transpose()
    # Decide labels
    predictedLabels = [decideLabel(alphas, predictedLabels) for predictedLabels in sampleResults]
    # Return
    return numpy.array(predictedLabels)

def load(classifierPath):
    # Initialize
    alphas, weakClassifierPaths = loadAlphaPaths(classifierPath)
    weakClassifyMethods = map(classifier.load, weakClassifierPaths)
    # Define
    def classify(imageContent=None, matrixContent=None):
        # Initialize
        weakLabels = []
        weakProbabilities = []
        # For each weakClassifyMethod,
        for weakClassifyMethod in weakClassifyMethods:
            weakLabel, weakProbability = weakClassifyMethod(imageContent, matrixContent)
            weakLabels.append(weakLabel)
            weakProbabilities.append(weakProbability)
        # Compute
        label = decideLabel(alphas, weakLabels)
        probability = decideProbability(alphas, weakProbabilities)
        # Return
        return int(label), float(probability)
    # Return
    return classify


# Helpers

def save(classifierPath, alphas):
    lines = map(str, alphas)
    content = '\n'.join(lines)
    alphaPath = os.path.join(classifierPath, 'alphas')
    open(alphaPath, 'wt').write(content)

def loadLabels(filePath):
    return classifier.loadLabels(filePath)

def loadAlphaPaths(classifierPath):
    # Load alphas
    alphaPath = os.path.join(classifierPath, 'alphas')
    alphas = map(float, open(alphaPath))
    # Load weakClassifierPaths
    weakClassifierPaths = [os.path.join(classifierPath, 'weak%d' % boostIndex) for boostIndex in xrange(len(alphas))]
    # Return
    return alphas, weakClassifierPaths

def decideLabel(alphas, weakLabels):
    # Convert weakLabels from 1/0 to +1/-1
    convertedWeakLabels = [1 if x == 1 else -1 for x in weakLabels]
    # Compute strongLabel in +1/-1
    strongLabel = numpy.sign(numpy.dot(alphas, convertedWeakLabels))
    # Convert strongLabel to 1/0
    return 1 if strongLabel == 1 else 0

def decideProbability(alphas, weakProbabilities):
    return numpy.dot(alphas, weakProbabilities) / float(sum(alphas))

def computeSampleMultipliers_divideByMinimum(sampleWeights):
    return map(int, sampleWeights / numpy.min(sampleWeights))

def computeSampleMultipliers_multiplyBySampleCount(sampleWeights):
    return map(int, numpy.ceil(sampleWeights * len(sampleWeights)))

def weightSamples(lushDatasetPath, sampleWeights):
    # Compute sampleMultipliers
    # sampleMultipliers = computeSampleMultipliers_multiplyBySampleCount(sampleWeights)
    sampleMultipliers = computeSampleMultipliers_divideByMinimum(sampleWeights)
    print 'max(sampleMultipliers) = %s' % max(sampleMultipliers)
    print 'sum(sampleMultipliers) = %s' % sum(sampleMultipliers)
    # Set paths
    temporaryFolderPath = tempfile.mkdtemp()
    weightedTrainingPath = os.path.join(temporaryFolderPath, 'training')
    sampleFile, labelFile = [open(x, 'wt') for x in classifier.makeSampleLabelPaths(weightedTrainingPath)]
    # Write header
    sampleCount = sum(sampleMultipliers)
    firstSample = classifier.makeSampleGeneratorFromLushDataset(lushDatasetPath).next()
    firstLabel = classifier.makeLabelGeneratorFromLushDataset(lushDatasetPath).next()
    sampleFile.write(classifier.makeLushMatrixHeaderFromPart(firstSample, sampleCount))
    labelFile.write(classifier.makeLushMatrixHeaderFromPart(firstLabel, sampleCount))
    # For each sample and label,
    for sampleIndex, sampleMultiplier, sample, label in itertools.izip(itertools.count(1), sampleMultipliers, classifier.makeSampleGeneratorFromLushDataset(lushDatasetPath), classifier.makeLabelGeneratorFromLushDataset(lushDatasetPath)):
        for index in xrange(sampleMultiplier): 
            sampleFile.write(classifier.makeLushMatrixContent(sample))
            labelFile.write(classifier.makeLushMatrixContent(label))
        if sampleIndex % 100 == 0: 
            view.printPercentUpdate(sampleIndex, sampleCount)
    view.printPercentFinal(sampleCount)
    # Close
    labelFile.close()
    sampleFile.close()
    # Return
    return weightedTrainingPath, sampleMultipliers

def saveWeakClassifierInformation(targetPath, trainingPath, testPath, parameterByName, extraBySectionByOption):
    # Assemble
    valueBySectionByOption = {
        'classifierModule': {'moduleName': classifier.__name__},
        'classifier': parameterByName,
        'trainingSet': {'sampleCount': classifier.getSampleCount(trainingPath)},
        'testSet': {'sampleCount': classifier.getSampleCount(testPath)},
    }
    valueBySectionByOption.update(extraBySectionByOption)
    # Save
    store.saveInformation(targetPath, valueBySectionByOption)

def getSampleCount(filePath):
    return classifier.getSampleCount(filePath)
