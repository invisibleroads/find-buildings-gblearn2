# Import system modules
import os
# Import custom modules
import folder_store
import store


class Information(object):

    # Constructor

    def __init__(self, informationPath):
        informationPath = os.path.join(os.path.dirname(informationPath), folder_store.fileNameByFolderName['datasets'])
        self.information = store.loadInformation(informationPath)

    def getSpatialReference(self):
        return self.information['windows']['spatial reference']

    def getWindowLengthInMeters(self):
        return float(self.information['windows']['window length in meters'])

    def getTrainingCount(self):
        return int(self.information['training set']['total'])

    def getTestCount(self):
        return int(self.information['test set']['total'])
