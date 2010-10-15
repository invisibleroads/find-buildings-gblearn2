import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from fp.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ScanController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/scan.mako')
        # or, return a response
        return render('/scans/index.mako')



