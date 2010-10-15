#!/usr/bin/env python2.6
"""
Finish jobs one at a time
"""
# Import system modules
import socket
# Import custom modules
import script_process
from fp import model
from fp.model import meta
from fp.lib import folder_store
import defineRegions
import sampleWindows
import combineDatasets
import trainClassifiers
import scanRegions
import clusterProbabilities
import analyzeScans


methodByType = {
    model.job_defineRegions: defineRegions.run,
    # model.job_sampleWindows: sampleWindows.run,
    # model.job_combineDatasets: combineDatasets.run,
    # model.job_trainClassifiers: trainClassifiers.run,
    # model.job_scanRegions: scanRegions.run,
    # model.job_clusterProbabilities: clusterProbabilities.run,
    # model.job_analyzeScans: analyzeScans.run,
}


def run():
    """
    Finish jobs one at a time
    """
    # Make sure that no other instance is running
    servicePort = int(options.configuration.get('server:main', 'port')) + 1
    localSocket = socket.socket()
    try:
        localSocket.bind(('', servicePort))
    except socket.error:
        return 'Either another instance of %s is running or port %s is in use' % (__file__, servicePort)
    # Initialize
    folderStore = folder_store.WebStore(options.configuration.get('app:main', 'storage_path'))
    jobCount = 0
    # Run each unfinished job
    for job in meta.Session.query(model.Job).filter(model.Job.pickled_output==None):
        # Prepare
        jobInput = job.getInput()
        jobMethod = methodByType[job.type]
        # Run
        jobMethod(job.owner_id, folderStore, **jobInput)
        # Delete job
        meta.Session.execute(model.jobs_table.delete().where(model.Job.id==job.id))
        meta.Session.commit()
        # Increment count
        jobCount += 1
    # Return
    return '%s jobs done' % jobCount


if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, arguments = optionParser.parse_args()
    # Initialize
    script_process.connect(options)
    # Run
    print run()
    meta.Session.commit()
