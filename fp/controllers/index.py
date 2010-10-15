# Import pylons modules
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
# Import system modules
import logging; log = logging.getLogger(__name__)
# Import custom modules
from fp.lib.base import BaseController, render
from fp.model import meta
from fp import model


class IndexController(BaseController):

    def index(self):
        c.personCount = meta.Session.query(model.Person).count()
        c.jobCount = meta.Session.query(model.Job).count()
        c.jobPendingCount = meta.Session.query(model.Job).filter(model.Job.pickled_output==None).count()
        return render('/index.mako')
