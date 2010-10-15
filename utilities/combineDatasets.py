#!/usr/bin/python
"""\
Combine datasets.

[parameters]
training size = INTEGER
test size = INTEGER
positive ratio = FLOAT

[regionName1]
window names = NAME LIST
patch names = NAME LIST

[regionName2]
window names = NAME LIST
patch names = NAME LIST

..."""
# Import system modules
import os
# Import custom modules
import script_process
from fp.lib import store, sample_process


def step(taskName, parameterByName, folderStore, options):
    # Get parameters
    trainingSize = parameterByName.get('training size')
    testSize = parameterByName.get('test size')
    positiveFraction = parameterByName.get('positive fraction')
    # Get names
    windowNames = parameterByName.get('window names', [])
    windowPaths = map(folderStore.getWindowPath, windowNames)
    windowFolderPaths = map(os.path.dirname, windowPaths)
    windowInformations = map(folderStore.getWindowInformation, windowNames)
    patchNames = parameterByName.get('patch names', [])
    patchPaths = map(folderStore.getPatchPath, patchNames)
    patchFolderPaths = map(os.path.dirname, patchPaths)
    patchInformations = map(folderStore.getPatchInformation, patchNames)
    # Set
    sourceInformations = windowInformations + patchInformations
    sourceFolderPaths = windowFolderPaths + patchFolderPaths
    # Make sure that each dataset has the same windowGeoLength
    windowLengthInMeters = store.validateSame([x.getWindowLengthInMeters() for x in sourceInformations], 'Datasets must have the same window length in meters: %s' % taskName)
    # Make sure that each dataset has the same spatialReference
    spatialReference = store.validateSame([x.getSpatialReference() for x in sourceInformations], 'Datasets must have the same spatial reference: %s' % taskName)
    # Set
    targetDatasetPath = folderStore.fillDatasetPath(taskName)
    targetDatasetFolderPath = os.path.dirname(targetDatasetPath)
    # Record
    information = {
        'parameters': {
            'training size': trainingSize,
            'test size': testSize,
            'positive fraction': positiveFraction,
        },
        'windows': {
            'spatial reference': spatialReference,
            'window length in meters': windowLengthInMeters,
        },
        'sources': {
            'window names': store.stringifyList(windowNames),
            'window paths': store.stringifyList(windowPaths),
            'patch names': store.stringifyList(patchNames),
            'patch paths': store.stringifyList(patchPaths),
        },
    }
    # Combine training and test sets
    if not options.is_test:
        print 'Combining datasets...\n\ttargetDatasetPath = %s' % targetDatasetPath
        information['training set'] = sample_process.combineDatasets(sample_process.makeTrainingPath(targetDatasetFolderPath), map(sample_process.makeTrainingPath, sourceFolderPaths), trainingSize, positiveFraction).getStatistics()
        information['test set'] = sample_process.combineDatasets(sample_process.makeTestPath(targetDatasetFolderPath), map(sample_process.makeTestPath, sourceFolderPaths), testSize, positiveFraction).getStatistics()
    # Save
    store.saveInformation(targetDatasetPath, information)


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
