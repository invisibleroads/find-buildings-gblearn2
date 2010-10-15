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


class RegionController(BaseController):

    def index(self):
        c.images = meta.Session.query(model.Image).all()
        c.regions = meta.Session.query(model.Region).filter_by(is_complete=True).all()
        c.region_jobs = meta.Session.query(model.Job).filter_by(type=model.job_defineRegions).all()
        return render('/regions/index.mako')

    def add(self, url=None):
        'Add a job to define regions'
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

    @jsonify
    def delete(self):
        # If the person is not logged in, return
        if not h.isPerson():
            return dict(isOk=0, message='You must be logged in to perform this action.')
        # !!! Assert ownership
        # Load
        regionID = request.POST.get('regionID')
        # Delete from database
        meta.Session.execute(model.regions_table.delete().where(model.Region.id==regionID))
        # Delete from file system 
        shutil.rmtree(folder_store.WebStore(config['storage_path']).getRegionPath(regionID))
        # Commit
        meta.Session.commit()
        # Return
        return dict(isOk=1)
