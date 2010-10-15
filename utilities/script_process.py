"""
Define common functions for command-line utilities
"""
# Import context modules
import os; basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.append(basePath)
# Import system modules
import ConfigParser
import sqlalchemy as sa
import optparse
# Import custom modules
from fp import model
from fp.lib import store


def buildOptionParser():
    """
    Enable the user to specify a paster server configuration path
    """
    optionParser = optparse.OptionParser()
    optionParser.add_option('-c', '--configurationPath', dest='configurationPath', help='use the specified configuration file', metavar='PATH', default=os.path.join(basePath, 'development.ini'))
    return optionParser


def connect(options):
    """
    Connect to the database
    """
    # Show feedback
    print 'Using %s' % options.configurationPath
    # Load
    configuration = ConfigParser.ConfigParser({'here': basePath})
    configuration.read(options.configurationPath)
    # Connect
    model.init_model(sa.create_engine(configuration.get('app:main', 'sqlalchemy.url')))
    # Save
    options.configuration = configuration


def feedQueue(step, scriptPath, optionParser=None):
    """
    Process a queue file
    """
    # Import custom modules
    from fp.lib import parameter_store, folder_store
    # If there is no option parser, build one
    if not optionParser:
        optionParser = buildOptionParser()
    # Add usage
    optionParser.usage = '%prog [options] queuePath'
    # Add options
    optionParser.add_option('-0', '--database', dest='via_database', action='store_true',
        help='use the database', default=False)
    optionParser.add_option('-d', '--directory', dest='directory', metavar='DIRECTORY',
        help='save results in DIRECTORY', default='.')
    optionParser.add_option('-t', '--test', dest='is_test', action='store_true',
        help='test the queuePath without running it', default=False)
    # Parse
    options, arguments = optionParser.parse_args()
    # If the user did not supply the right number of arguments,
    if len(arguments) != 1:
        # Show help and exit
        return optionParser.print_help()
    # Connect
    if options.via_database:
        connect(options)
    # Extract
    queuePath = arguments[0]
    try: 
        # Load information
        parameterByTaskByName = store.loadQueue(queuePath, parameter_store.convertByName)
        # Initialize
        testFolderPath = os.path.join(options.directory, 'test')
        if options.is_test: 
            options.directory = store.makeFolderSafely(testFolderPath)
        folderStore = folder_store.Store(options.directory)
        # Step through each task
        for taskName, parameterByName in parameterByTaskByName.iteritems():
            step(taskName, parameterByName, folderStore, options)
    except (store.QueueError, folder_store.FolderError, ScriptError), scriptError:
        return '%s %s\n%s' % (store.extractFileBaseName(scriptPath), queuePath, scriptError)


class ScriptError(Exception):
    pass
