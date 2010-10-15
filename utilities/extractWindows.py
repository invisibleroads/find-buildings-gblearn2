#!/usr/bin/python
"""\
Extract windows from image using shapefiles.

[parameters]
window length in meters = FLOAT

[windowName1]
window label = INTEGER
window center path = PATH
image name = NAME

[windowName2]
window label = INTEGER
window center path = PATH
image name = NAME

..."""
# Import system modules
# Import custom modules
import script_process
from fp.lib import store, window_process, point_store, image_store


def step(taskName, parameterByName, folderStore, options):
    # Get
    windowGeoLength = parameterByName['window length in meters']
    windowLabel = parameterByName['window label']
    windowCenterPath = parameterByName['window center path']
    imageName = parameterByName['image name']
    imagePath = folderStore.getImagePath(imageName)
    imageInformation = folderStore.getImageInformation(imageName)
    # Prepare
    geoCenters, spatialReference = point_store.load(windowCenterPath)
    multispectralImage = imageInformation.getMultispectralImage()
    panchromaticImage = imageInformation.getPanchromaticImage()
    # Set
    targetWindowPath = folderStore.fillWindowPath(taskName)
    exampleInformation = {}
    # Extract
    if not options.is_test:
        dataset = window_process.extract(targetWindowPath, geoCenters, windowLabel, windowGeoLength, multispectralImage, panchromaticImage)
        exampleInformation['count'] = dataset.countSamples()
    # Save
    store.saveInformation(targetWindowPath, {
        'windows': {
            'window length in meters': windowGeoLength,
            'spatial reference': spatialReference,
        },
        'parameters': {
            'window label': windowLabel,
            'window center path': windowCenterPath,
            'image name': imageName,
            'image path': imagePath,
        },
        'examples': exampleInformation,
    })


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(step, __file__)
