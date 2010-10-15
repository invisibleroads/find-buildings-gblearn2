# Import system modules
import os
import sys
import shutil


# Set
extensions = '.queue', '.info', '.shp', '.shx', '.dbf', '.prj', '.png', '.map', '.html', '.csv'


if __name__ == '__main__':
    # Check arguments
    if len(sys.argv) < 2:
        print 'Please specify a target folder'
        sys.exit()
    withReportsOnly = False if len(sys.argv) == 2 else True
    # Prepare targetFolder
    targetFolderPath = sys.argv[1]
    if not os.path.exists(targetFolderPath):
        os.mkdir(targetFolderPath)
    # Walk
    for basePath, folderNames, fileNames in os.walk('.'):
        if '.svn' in basePath: 
            continue
        targetSubFolderPath = os.path.join(targetFolderPath, basePath)
        if not os.path.exists(targetSubFolderPath):
            os.mkdir(targetSubFolderPath)
        if withReportsOnly and '9-results' not in basePath:
            continue
        for fileName in fileNames:
            extension = os.path.splitext(fileName)[1]
            if extension in extensions:
                sourcePath = os.path.join(basePath, fileName)
                targetPath = os.path.join(targetFolderPath, sourcePath)
                shutil.copy(sourcePath, targetPath)
                print sourcePath
