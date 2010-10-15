#!/usr/bin/python
"""\
Cluster probabilities.  Evaluate locations if given the complete set 
of positive locations for an image.

[parameters]
iteration count per burst = INTEGER
maximum diameter in meters = FLOAT
minimum diameter in meters = FLOAT
evaluation radius in meters = FLOAT

[locationName1]
probability name = NAME

[locationName2]
probability name = NAME

..."""
# Import system modules
import os
# Import custom modules
import script_process
from fp.lib import store, probability_store, probability_process, evaluation_process, region_store


def step(taskName, parameterByName, folderStore, options):
    # Get probabilityInformation
    probabilityName = parameterByName['probability name']
    probabilityPath = folderStore.getProbabilityPath(probabilityName)
    probabilityInformation = probability_store.Information(probabilityPath)
    # Get imageInformation
    imageName = probabilityInformation.getImageName()
    imageInformation = folderStore.getImageInformation(imageName)
    # Get parameters
    positiveLocationPath = imageInformation.getPositiveLocationPath()
    multispectralImage = imageInformation.getMultispectralImage()
    spatialReference = multispectralImage.getSpatialReference()
    evaluationRadiusInMeters = parameterByName['evaluation radius in meters']
    evaluationDiameterInMeters = evaluationRadiusInMeters * 2
    iterationCountPerBurst = parameterByName['iteration count per burst']
    maximumDiameterInMeters = parameterByName['maximum diameter in meters']
    minimumDiameterInMeters = parameterByName['minimum diameter in meters']
    # Run
    targetLocationPath = folderStore.fillLocationPath(taskName)
    targetFolderPath = os.path.dirname(targetLocationPath)
    locationInformation = {
        'location': {
            'path': targetLocationPath, 
            'spatial reference': spatialReference,
        },
        'probability': {
            'name': probabilityName,
            'path': probabilityPath,
        },
        'parameters': {
            'iteration count per burst': iterationCountPerBurst, 
            'maximum diameter in meters': maximumDiameterInMeters,
            'minimum diameter in meters': minimumDiameterInMeters,
            'evaluation radius in meters': evaluationRadiusInMeters,
        },
    }
    if not options.is_test:
        # Cluster
        print 'Clustering locations...'
        probability_process.cluster(targetLocationPath, probabilityPath, iterationCountPerBurst, maximumDiameterInMeters, minimumDiameterInMeters)
        # If scanning has finished,
        if probabilityInformation.hasPerformance():
            print 'Evaluating locations...'
            # Load regions
            regionPath = probabilityInformation.getRegionPath()
            regionGeoFrames = region_store.loadShapefile(regionPath, multispectralImage, withGeoToPixelConversion=False)
            # Evaluate locations
            locationInformation['performance'] = evaluation_process.evaluateLocations(targetFolderPath, evaluationDiameterInMeters, positiveLocationPath, targetLocationPath, regionGeoFrames)
    # Record
    store.saveInformation(targetLocationPath, locationInformation)


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
