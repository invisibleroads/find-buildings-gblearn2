#!/usr/bin/env python
"""
Command-line script to register images into a database

[parameters]
path = PATH

[imageName1]
multispectral image = PATH
panchromatic image = PATH

[imageName2]
multispectral image = PATH
panchromatic image = PATH

..."""
# Import custom modules
import script_process
from fp.model import image_database


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(image_database.add, __file__)
