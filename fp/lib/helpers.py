"""
Helpers
"""
# Import pylons modules
from pylons import session
# Import system modules
from webhelpers.html.tags import *
from routes import url_for
# Import custom modules
from fp.config.parameter import *


def encodeURL(url):
    return url.replace('/', '~')

def decodeURL(url):
    return str(url.replace('~', '/'))

def isPerson():
    return 'personID' in session

def isPersonSuper():
    return 'personID' in session and session['is_super']
