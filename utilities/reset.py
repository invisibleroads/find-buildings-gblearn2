#!/usr/bin/env python2.6
"""
Reset database
"""
# Import custom modules
import script_process
from fp.model import meta


def run():
    'Reset database'
    # Connect
    meta.metadata.bind = meta.engine
    # Reflect
    meta.metadata.reflect()
    # Clear database
    meta.metadata.drop_all()
    meta.metadata.create_all()
    # Return
    return 'Reset'


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, arguments = optionParser.parse_args()
    # Initialize
    script_process.connect(options)
    # Run
    print run()
