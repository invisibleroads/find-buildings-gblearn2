# Import pylons modules
from pylons import request, response, session, tmpl_context as c, config
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
import shutil
# Import custom modules
from fp import model
from fp.model import meta
from fp.lib import helpers as h, folder_store
from fp.lib.base import BaseController, render

class DatasetController(BaseController):

    def index(self):
        c.windows = meta.Session.query(model.Window).all()
        c.datasets = meta.Session.query(model.Dataset).filter_by(is_complete=True).all()
        c.datasets_jobs = meta.Session.query(model.Job).filter_by(type=model.job_combineDatasets).all()
        return render('/datasets/index.mako')

    def add(self):
        'Add a job to define datasets'
        # If the user is not logged in, return
        if not h.isPerson():
            return 'Please log in to perform this action.'
        # Initialize
        parameterByName = {
            'test fraction per region': float(request.POST['testFractionPerRegion']),
        }
        # Extract
        regionMethod = request.POST['regionMethod']
        # If the user wants to specify regions via coverage fraction,
        if regionMethod == 'viaCoverageFraction':
            parameterByName.update({
                'window length in meters': float(request.POST['windowLengthInMeters']),
                'region length in windows': int(request.POST['regionLengthInWindows']),
                'coverage fraction': float(request.POST['coverageFraction']),
                'coverage offset': int(request.POST['coverageOffset']),
            })
        # If the user wants to specify regions via rectangles,
        elif regionMethod == 'viaRectangles':
            parameterByName.update({
                'multispectral region frames': request.POST['multispectralRegionFrames'],
            })
        # If the user wants to specify regions via shapefile,
        elif regionMethod == 'viaShapefile':
            # Save upload into a temporary file
            # !!!! not finished
            # region
            parameterByName.update({'region path': ''})
        # Add job
        job = model.Job(model.job_defineRegions, session['personID'])
        job.setInput(dict(
            regionName=request.POST['regionName'],
            imageID=request.POST['imageID'],
            parameterByName=parameterByName,
        ))
        meta.Session.add(job)
        meta.Session.commit()
        # Redirect
        redirect_to(h.decodeURL(url) or url_for('image_index'))
        pass

    def delete(self):
        pass
