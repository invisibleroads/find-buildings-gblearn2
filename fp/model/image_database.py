"""
Routines for adding an image to a database
"""
# Import custom modules
from fp import model
from fp.model import meta
from fp.lib import store, image_store


def add(imageName, ownerID, parameterByName):
    """
    Add an image to a database
    """
    # Show feedback
    print 'Registering image: ' + imageName
    # Check whether the image has already been registered
    image = meta.Session.query(model.Image).filter_by(name=imageName).first()
    # If the image does not exist,
    if not image:
        # Register the image in the database
        image = model.Image(imageName, ownerID)
        meta.Session.add(image)
    # Prepare path
    basePath = parameterByName.get('path', '')
    # Load multispectral image
    multispectralImagePath = store.fillPath(basePath, parameterByName['multispectral image'])
    multispectralImage = image_store.load(multispectralImagePath)
    multispectralSpatialReference = multispectralImage.getSpatialReference()
    # Load panchromatic image
    panchromaticImagePath = store.fillPath(basePath, parameterByName['panchromatic image'])
    panchromaticImage = image_store.load(panchromaticImagePath)
    panchromaticSpatialReference = panchromaticImage.getSpatialReference()
    # Validate
    spatialReference = store.validateSame([multispectralSpatialReference, panchromaticSpatialReference], 'Spatial references do not match: %s' % imageName)
    # Update image
    image.multispectral_path = multispectralImagePath
    image.panchromatic_path = panchromaticImagePath
    image.spatial_reference = spatialReference
    image.is_complete = True
    meta.Session.commit()
