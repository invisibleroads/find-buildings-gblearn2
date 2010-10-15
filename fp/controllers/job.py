# Import pylons modules
from pylons import request, response, session, tmpl_context as c, config
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
# Import custom modules
from fp import model
from fp.model import meta
from fp.lib import helpers as h
from fp.lib.base import BaseController, render


class JobController(BaseController):

    def index(self):
        return 'Hello World'

    @jsonify
    def delete(self):
        # If the person is not logged in, return
        if not h.isPerson():
            return dict(isOk=0, message='You must be logged in to perform this action.')
        # Load
        jobID = request.POST.get('jobID')
        # Delete
        meta.Session.execute(model.jobs_table.delete().where(model.Job.id==jobID))
        # Commit
        meta.Session.commit()
        # Return
        return dict(isOk=1)
