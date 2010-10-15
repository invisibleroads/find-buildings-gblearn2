#!/usr/bin/python
"""\
Evaluates a scan.

[parameters]
evaluation radius in meters list = FLOAT RANGE
evaluation length in meters list = FLOAT RANGE

[evaluationName1]
probability name = NAME
"""
# Import system modules
import os
import pylab
# Import custom modules
from script_process
from fp.lib import store, probability_store, evaluation_process


def step(taskName, parameterByName, folderStore, options):
    # Get
    radiusList = parameterByName['evaluation radius in meters list']
    lengthList = parameterByName['evaluation length in meters list']
    # Get probabilityName
    probabilityName = parameterByName['probability name']
    probabilityPath = folderStore.getProbabilityPath(probabilityName)
    expandPath = lambda x: os.path.join(os.path.dirname(probabilityPath), x)
    evaluationPath = expandPath(taskName)
    # Set information
    information = {
        'parameters': {
            'evaluation radius in meters list': radiusList,
            'evaluation length in meters list': lengthList,
        },
    }
    if not options.is_test:
        # Evaluate using radius
        recalls = []
        precisions = []
        for radius in radiusList:
            radiusInfo = evaluation_process.evaluateWindowsByRadius(probabilityPath, radius)
            information['radius %s' % radius] = radiusInfo
            recalls.append(radiusInfo['recall'])
            precisions.append(radiusInfo['precision'])
        # Plot using radius
        pylab.figure()
        pylab.plot(recalls, precisions, '*')
        for x, y, radius in zip(recalls, precisions, radiusList):
            pylab.text(x, y, radius)
        pylab.title('Evaluation of scan using relative circles (circle radius in meters)')
        pylab.ylabel('Precision (Percent of predicted that are actual)')
        pylab.xlabel('Recall (Percent of actual that are predicted)')
        pylab.axis([0, 1, 0, 1])
        pylab.savefig(expandPath('%s-rad.png' % taskName))
        # Evaluate using length
        truePositiveRates = []
        falsePositiveRates = []
        for length in lengthList:
            lengthInfo = evaluation_process.evaluateWindowsByLength(probabilityPath, length)
            truePositiveRates.append(lengthInfo['true positive rate'])
            falsePositiveRates.append(lengthInfo['false positive rate'])
        # Plot using length
        pylab.figure()
        pylab.plot(falsePositiveRates, truePositiveRates, '*')
        for x, y, length in zip(falsePositiveRates, truePositiveRates, lengthList):
            pylab.text(x, y, length)
        pylab.title('Evaluation of scan using absolute rectangles (rectangle length in meters)')
        pylab.ylabel('True positive rate')
        pylab.xlabel('False positive rate')
        pylab.axis([0, 1, 0, 1])
        pylab.savefig(expandPath('%s-roc.png' % taskName))
    # Record
    store.saveInformation(evaluationPath, information)


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
