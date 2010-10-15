import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from fp.lib.base import BaseController, render

log = logging.getLogger(__name__)
# Import custom modules
from fp import model
from fp.model import meta

class ClassifierController(BaseController):

    def index(self):
        c.regions = meta.Session.query(model.Region).filter_by(is_complete=True).all()
        return render('/classifiers/index.mako')

    def add(self):
        # Load parameters from request.POST
        # Create a job in the database with type job_sampleWindows
        pass
