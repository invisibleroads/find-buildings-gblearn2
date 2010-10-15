#!/usr/bin/python
"""\
Train classifiers.

[parameters]
classifier module name = NAME
feature module name = NAME
feature class name = NAME
connection table0 path = PATH
connection table1 path = PATH
hidden count = INTEGER
iteration count = INTEGER
ratio range = FLOAT LIST
kernel range = INTEGER LIST
which layer combination = INTEGER
boost count = INTEGER

[classifierName1]
dataset name = NAME

[classifierName2]
dataset name = NAME

..."""
# Import system modules
import os
# Import custom modules
import script_process
from fp.lib import store, classifier, sample_process, dataset_store


def step(taskName, parameterByName, folderStore, options):
    # Get parameters
    datasetName = parameterByName['dataset name']
    datasetPath = folderStore.getDatasetPath(datasetName)
    datasetFolderPath = os.path.dirname(datasetPath)
    # Set
    trainingPath = sample_process.makeTrainingPath(datasetFolderPath)
    testPath = sample_process.makeTestPath(datasetFolderPath)
    datasetInformation = dataset_store.Information(trainingPath)
    if not options.is_test:
        # Make sure that training and test sets are not empty
        if not datasetInformation.getTrainingCount():
            raise script_process.ScriptError('Empty training set: %s' % trainingPath)
        if not datasetInformation.getTestCount():
            raise script_process.ScriptError('Empty test set: %s' % testPath)
    # Pack
    classifierModule = store.getLibraryModule(parameterByName['classifier module name'])
    featureModule = store.getLibraryModule(parameterByName['feature module name'])
    featureClass = getattr(featureModule, parameterByName['feature class name'])
    # Run
    targetClassifierPath = folderStore.fillClassifierPath(taskName)
    if not isTest:
        # Build classifier
        resultByName = classifier.build(targetClassifierPath, classifierModule, featureClass(), trainingPath, testPath, parameterByName)
    else:
        resultByName = {}
    # Record
    makeDictionary = lambda keys: dict((key, parameterByName[key]) for key in keys if key in parameterByName)
    parameterInformation = makeDictionary(['classifier module name', 'feature module name', 'feature class name'])
    parameterInformation.update(makeDictionary(classifierModule.relevantParameterNames))
    store.saveInformation(targetClassifierPath, {
        'parameters': parameterInformation,
        'dataset': {
            'name': datasetName,
            'path': datasetPath,
        },
        'windows': {
            'training': trainingPath,
            'test': testPath,
            'window length in meters': datasetInformation.getWindowLengthInMeters(),
            'spatial reference': datasetInformation.getSpatialReference(),
        },
        'performance': resultByName,
    })


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
