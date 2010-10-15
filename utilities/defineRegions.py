#!/usr/bin/env python
"""\
Define regions from images.

[parameters]
test fraction per region = FLOAT
image name = NAME

[regionName1]
window length in meters = FLOAT
region length in windows = INTEGER
coverage fraction = FLOAT
coverage offset = INTEGER

[regionName2]
multispectral region frames = FRAME LIST

[regionName3]
region path = PATH

..."""
# Import custom modules
import script_process
from fp.model import region_database


# If we are running the script,
if __name__ == '__main__':
    # Feed
    script_process.feedQueue(region_database.add, __file__)
