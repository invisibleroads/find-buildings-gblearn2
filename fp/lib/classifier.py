# Import system modules
import os
import numpy
# Import custom modules
import store
import image_store, image_process
import sample_store, sample_process
import window_store


# Core

def build(targetClassifierPath, classifierModule, featureSet, trainingPath, testPath, parameterByName):
    # Save training
    trainingDataset = sample_store.load(trainingPath)
    trainingFeaturePath = classifierModule.saveSamples(trainingDataset, trainingDataset.getSampleIDs(), featureSet)
    # Save test
    testDataset = sample_store.load(testPath)
    testFeaturePath = classifierModule.saveSamples(testDataset, testDataset.getSampleIDs(), featureSet)
    # Train
    return classifierModule.train(targetClassifierPath, trainingFeaturePath, testFeaturePath, parameterByName)

def load(classifierPath):
    classifierInformation = Information(classifierPath)
    classifierModuleName = classifierInformation.getClassifierModuleName()
    classifierModule = store.getLibraryModule(classifierModuleName)
    return classifierModule.load(classifierPath)

@store.recordElapsedTime
def scan(targetProbabilityPath, classifierPath, multispectralImagePath, panchromaticImagePath, scanRatio, regionFrames=None):
    # Initialize
    classify = load(classifierPath)
    classifierInformation = Information(classifierPath)
    windowLengthInMeters = classifierInformation.getWindowLengthInMeters()
    multispectralImage = image_store.load(multispectralImagePath)
    panchromaticImage = image_store.load(panchromaticImagePath)
    # If no regions are defined,
    if not regionFrames: 
        # Use the entire image
        regionFrames = [(0, 0, multispectralImage.width, multispectralImage.height)]
    # Open probabilityFile
    probabilityFile = open(targetProbabilityPath, 'wt')
    # For each window,
    for regionIndex, regionFrame in enumerate(regionFrames):
        print 'Scanning region %s/%s...' % (regionIndex + 1, len(regionFrames))
        for window in image_process.makeWindowGenerator(multispectralImage, panchromaticImage, windowLengthInMeters, scanRatio, regionFrame):
            # Classify
            classification_string = '%s %s' % classify(imageContent=window.extractImage())
            windowLocation_string = '%s %s' % window.multispectralWindowLocation
            probabilityFile.write('%s %s\n' % (windowLocation_string, classification_string))
    # Close probabilityFile
    probabilityFile.close()


class Information(object):

    def __init__(self, informationPath):
        self.information = store.loadInformation(informationPath)

    def getClassifierModuleName(self):
        return self.information['parameters']['classifier module name']

    def getFeatureModuleName(self):
        return self.information['parameters']['feature module name']

    def getFeatureClassName(self):
        return self.information['parameters']['feature class name']

    def getDataset(self):
        return sample_store.load(self.information['dataset']['path'])

    def getTrainingDataset(self):
        return sample_store.load(self.information['windows']['training'])

    def getTestDataset(self):
        return sample_store.load(self.information['windows']['test'])

    def getWindowLengthInMeters(self):
        return float(self.information['windows']['window length in meters'])
