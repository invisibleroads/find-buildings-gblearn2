"""The base Controller API

Provides the BaseController class for subclassing.
"""
# Import pylons modules
from pylons import request, session
from pylons.controllers.util import redirect_to
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
# Import system modules
# Import custom modules
from fp.model import meta
from fp.lib import helpers as h


class BaseController(WSGIController):

    withAuthentication = False

    def __before__(self):
        # If authentication is required and the person is not logged in,
        if self.withAuthentication and not h.isPerson():
            # Remember where to send the user after a successful login
            return redirect_to('person_login', url=h.encodeURL(request.path_info))

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()
