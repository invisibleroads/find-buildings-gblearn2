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


class WindowController(BaseController):

    def index(self):
        c.regions = meta.Session.query(model.Region).filter_by(is_complete=True).all()
        c.windows = meta.Session.query(model.Window).filter_by(is_complete=True).all()
        c.window_jobs = meta.Session.query(model.Job).filter_by(type=model.job_sampleWindows)
        return render('/windows/index.mako')

    def add(self, url=None):
        """
        Add a job to define windows
        """
        # If the user is not logged in, return
        if not h.isPerson():
            return 'Please log in to perform this action.'
        # Load parameters from request.POST
        parameterByName = {
            'example count per region': int(request.POST['exampleCountPerRegion']),
            'multispectral pixel shift value': int(request.POST['multispectralPixelShiftValue']),
            'shift count': int(request.POST['shiftCount']),
        }
        # Create a job in the database with type job_sampleWindows
        job = model.Job(model.job_sampleWindows, session['personID'])
        job.setInput(dict(
            windowName=request.POST['windowName'],
            regionID=request.POST['regionID'],
            parameterByName=parameterByName,
        ))
        meta.Session.add(job)
        meta.Session.commit()
        # Redirect
        redirect_to(h.decodeURL(url) or url_for('window_index'))

    @jsonify
    def delete(self):
        # If the person is not logged in, return
        if not h.isPerson():
            return dict(isOk=0, message='You must be logged in to perform this action.')
        # !!! Assert ownership
        # Load
        windowID = request.POST.get('windowID')
        # Delete from database
        meta.Session.execute(model.windows_table.delete().where(model.Window.id==windowID))
        # Delete from file system 
        shutil.rmtree(folder_store.WebStore(config['storage_path']).getWindowPath(windowID))
        # Commit
        meta.Session.commit()
        # Return
        return dict(isOk=1)

