"""
Handles images
"""
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, config
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
from routes import url_for
import shutil
import os
# Import custom modules
from fp import model
from fp.model import meta
from fp.lib import helpers as h, store, folder_store
from fp.lib.base import BaseController, render


class ImageController(BaseController):
    """
    Defines actions on images
    """

    def index(self):
        """
        Show a list of images
        """
        c.images = meta.Session.query(model.Image).all()
        return render('/images/index.mako')

    def add(self, url=None):
        # If the person is not logged in, return
        if not h.isPerson():
            return
        # Load
        imageName = request.POST.get('imageName')
        imageMultispectral = request.POST.get('imageMultispectral')
        imagePanchromatic = request.POST.get('imagePanchromatic')
        # Verify attributes
        if imageName:
            # Get subfolder name
            image = model.Image(imageName, session['personID'])
            meta.Session.add(image)
            meta.Session.commit()
            # Save images
            imagePath = folder_store.WebStore(config['storage_path']).getImagePath(image.id)
            image.multispectral_path = saveUpload(imagePath, 'multispectral', imageMultispectral)
            image.panchromatic_path = saveUpload(imagePath, 'panchromatic', imagePanchromatic)
            meta.Session.commit()
        # Redirect
        redirect_to(h.decodeURL(url) or url_for('image_index'))

    @jsonify
    def delete(self):
        # If the person is not logged in, return
        if not h.isPerson():
            return dict(isOk=0, message='You must be logged in to perform this action.')
        # Load
        imageID = request.POST.get('imageID')
        imagePath = folder_store.WebStore(config['storage_path']).getImagePath(image.id)
        # Delete
        meta.Session.execute(model.images_table.delete().where(model.Image.id==imageID))
        shutil.rmtree(imagePath)
        # Commit
        meta.Session.commit()
        # Return
        return dict(isOk=1)

    def analyze(self):
        c.images = meta.Session.query(model.Image).all()
        c.classifiers = meta.Session.query(model.Classifier).all()
        return render('/images/analyze.mako')


def saveUpload(targetFolder, targetBaseName, uploadedObject):
    targetExtension = os.path.splitext(uploadedObject.filename)[1]
    targetPath = os.path.join(targetFolder, targetBaseName + targetExtension)
    shutil.copyfileobj(uploadedObject.file, open(targetPath, 'wb'))
    uploadedObject.file.close()
    return targetPath
