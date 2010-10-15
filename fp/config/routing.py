"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
# Import pylons modules
from pylons import config
from routes import Mapper


def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # Remove trailing slash
    map.redirect('/{controller}/', '/{controller}')

    # Map custom routes
    map.connect('index', '/', controller='index', action='index')

    map.connect('person_index', '/people', controller='person', action='index')
    map.connect('person_register', '/people/register', controller='person', action='register')
    map.connect('person_register_', '/people/register_', controller='person', action='register_')
    map.connect('person_confirm', '/people/confirm/{ticket}', controller='person', action='confirm')
    map.connect('person_login', '/people/login/{url}', controller='person', action='login')
    map.connect('person_login_plain', '/people/login', controller='person', action='login')
    map.connect('person_login_', '/people/login_', controller='person', action='login_')
    map.connect('person_update', '/people/update', controller='person', action='update')
    map.connect('person_update_', '/people/update_', controller='person', action='update_')
    map.connect('person_logout_plain', '/people/logout', controller='person', action='logout') 
    map.connect('person_logout', '/people/logout/{url}', controller='person', action='logout')
    map.connect('person_reset', '/people/reset', controller='person', action='reset')
    
    map.connect('job_delete', '/jobs', controller='job', action='delete')

    map.connect('image_index', '/images', controller='image', action='index')
    map.connect('image_add', '/images/add/{url}', controller='image', action='add')
    map.connect('image_add_plain', '/images/add', controller='image', action='add')
    map.connect('image_delete', '/images/delete', controller='image', action='delete')
    map.connect('image_analyze', '/images/analyze', controller='image', action='analyze')

    map.connect('region_index', '/regions', controller='region', action='index')
    map.connect('region_add', '/regions/add/{url}', controller='region', action='add')
    map.connect('region_add_plain', '/regions/add', controller='region', action='add')
    map.connect('region_delete', '/regions/delete', controller='region', action='delete')

    map.connect('window_index', '/windows', controller='window', action='index')
    map.connect('window_add', '/windows/add/{url}', controller='window', action='add')
    map.connect('window_add_plain', '/windows/add', controller='window', action='add')
    map.connect('window_delete', '/windows/delete', controller='window', action='delete')

    map.connect('dataset_index', '/datasets', controller='dataset', action='index')
    map.connect('dataset_add', '/datasets/add/{url}', controller='dataset', action='add')
    map.connect('dataset_add_plain', '/datasets/add', controller='dataset', action='add')
    map.connect('dataset_delete', '/datasets/delete', controller='dataset', action='delete')

    map.connect('classifier_index', '/classifiers', controller='classifier', action='index')
    map.connect('classifier_add', '/classifiers/add/{url}', controller='classifier', action='add')
    map.connect('classifier_add_plain', '/classifiers/add', controller='classifier', action='add')
    map.connect('classifier_delete', '/classifiers/delete', controller='classifier', action='delete')

    map.connect('scan_index', '/scans', controller='scan', action='index')
    map.connect('scan_add', '/scans/add/{url}', controller='scan', action='add')
    map.connect('scan_add_plain', '/scans/add', controller='scan', action='add')
    map.connect('scan_delete', '/scans/delete', controller='scan', action='delete')

    map.connect('location_index', '/locations', controller='location', action='index')
    map.connect('location_add', '/locations/add/{url}', controller='location', action='add')
    map.connect('location_add_plain', '/locations/add', controller='location', action='add')
    map.connect('location_delete', '/locations/delete', controller='location', action='delete')

    return map
