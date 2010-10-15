"""
Pylons environment configuration
"""
# Import pylons modules
from pylons import config
from pylons.error import handle_mako_error
# Import system modules
from mako.lookup import TemplateLookup
from sqlalchemy import engine_from_config
import logging; log = logging.getLogger(__name__)
import ConfigParser
import os
# Import custom modules
import fp.lib.app_globals as app_globals
import fp.lib.helpers
from fp.config.routing import make_map
from fp.model import init_model


def load_environment(global_conf, app_conf):
    """
    Configure the Pylons environment via the ``pylons.config`` object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
        controllers=os.path.join(root, 'controllers'),
        static_files=os.path.join(root, 'public'),
        templates=[os.path.join(root, 'templates')])
    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='fp', paths=paths)
    config['routes.map'] = make_map()
    config['pylons.app_globals'] = app_globals.Globals()
    config['pylons.h'] = fp.lib.helpers
    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])
    # Set up the SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)
    # Load sensitive information
    config['extra'] = loadSensitiveInformation(config['extra_path'])


def loadSensitiveInformation(sensitivePath):
    # Validate
    if not os.path.exists(sensitivePath):
        log.warn('Missing extra configuration: ' + sensitivePath)
        sensitivePath = os.path.join(config['here'], 'default.cfg')
    # Initialize
    valueByName = {}
    # Set up sensitive information 
    configuration = ConfigParser.ConfigParser() 
    configuration.read(sensitivePath)
    for sectionName in configuration.sections(): 
        valueByName[sectionName] = dict(configuration.items(sectionName)) 
    # Return
    return valueByName
