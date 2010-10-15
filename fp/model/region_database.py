# Import system modules
import itertools
# Import custom modules
from fp.lib import store, image_store, region_store, region_process


def run(ownerID, webStore, regionName, imageID, parameterByName):
    """
    Generate region files for the image in the specified directory and return statistics.
    """
    # Import custom modules
    from fp import model
    from fp.model import meta
    # Prepare image
    image = meta.Session.query(model.Image).get(imageID)
    if not image:
        return
    # Create a new region
    region = model.Region(regionName, ownerID, imageID)
    meta.Session.add(region)
    meta.Session.commit()
    targetRegionPath = webStore.getRegionPath(region.id)
    # Define regions
    defineRegions(targetRegionPath, image.multispectral_path, image.panchromatic_path, parameterByName)
    # Mark it complete
    region.is_complete = True
    meta.Session.commit()


def step(taskName, parameterByName, folderStore, options):
    # Prepare
    targetRegionPath = folderStore.fillRegionPath(taskName)
    imageName = parameterByName['image name']
    imagePath = folderStore.getImagePath(imageName)
    imageInformation = image_store.Information(imagePath)
    multispectralImagePath = imageInformation.getMultispectralImagePath()
    panchromaticImagePath = imageInformation.getPanchromaticImagePath()
    # Define regions
    information = defineRegions(targetRegionPath, multispectralImagePath, panchromaticImagePath, parameterByName, options)


def defineRegions(targetRegionPath, multispectralImagePath, panchromaticImagePath, parameterByName, options=None):
    # Load
    targetTestRegionPath = targetRegionPath + '-test'
    multispectralImage = image_store.load(str(multispectralImagePath))
    panchromaticImage = image_store.load(str(panchromaticImagePath))
    regionPath = parameterByName.get('region path')
    multispectralRegionFrames = parameterByName.get('multispectral region frames')
    windowLengthInMeters = parameterByName.get('window length in meters')
    regionLengthInWindows = parameterByName.get('region length in windows')
    testFractionPerRegion = parameterByName['test fraction per region']
    coverageFraction = parameterByName.get('coverage fraction', 1)
    coverageFrequency = int(1 / coverageFraction)
    coverageOffset = parameterByName.get('coverage offset', 0)
    # If regionPath is defined, use it
    if regionPath:
        regionGenerator = (x for x in region_store.loadShapefile(regionPath, multispectralImage))
    # If multispectralRegionFrames are defined, use them
    elif multispectralRegionFrames:
        regionGenerator = (x for x in multispectralRegionFrames)
    # Otherwise, prepare regionGenerator
    else:
        regionGenerator = region_store.makeRegionGenerator(multispectralImage, panchromaticImage, regionLengthInWindows, windowLengthInMeters)
    # Save regions
    regionDataset = region_store.create(targetRegionPath)
    testRegionDataset = region_store.create(targetTestRegionPath)
    if options and not options.is_test:
        for regionIndex, regionWindow in itertools.izip(itertools.count(1), regionGenerator):
            if (regionIndex + coverageOffset) % coverageFrequency == 0:
                regionDataset.addRegion(regionWindow)
                regionFrame = region_store.getMultispectralPixelFrame(regionWindow)
                testRegionDataset.addFrame(region_process.placeTestRegion(regionFrame, testFractionPerRegion))
    # Save as shapefiles
    regionDataset.saveShapefile(targetRegionPath, multispectralImage)
    testRegionDataset.saveShapefile(targetTestRegionPath, multispectralImage)
    # Prepare information
    information = {
        'parameters': {
            'multispectral image path': multispectralImagePath,
            'panchromatic image path': panchromaticImagePath,
            'test fraction per region': testFractionPerRegion,
            'window length in meters': windowLengthInMeters,
        },
        'regions': {
            'path': regionDataset.getPath(),
            'count': regionDataset.count(),
        },
        'test regions': {
            'path': testRegionDataset.getPath(),
            'count': testRegionDataset.count(),
        },
    }
    if regionPath:
        information['parameters'].update({
            'region path': regionPath,
        })
    elif multispectralRegionFrames: 
        information['parameters'].update({
            'multispectral region frames': store.stringifyNestedList(multispectralRegionFrames),
        })
    else:
        information['parameters'].update({
            'region length in windows': regionLengthInWindows,
            'coverage fraction': coverageFraction,
            'coverage offset': coverageOffset,
        })
    # Save information
    store.saveInformation(targetRegionPath, information)
