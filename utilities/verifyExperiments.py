# Import system modules
import optparse
import subprocess
import re


pattern_comment = re.compile(r'#.*')


def run():
    # Parse options and arguments
    optionParser = optparse.OptionParser(usage='%prog masterScriptPath')
    options, arguments = optionParser.parse_args()
    if len(arguments) == 0:
        optionParser.print_help()
        return
    # Verify
    for masterScriptPath in arguments:
        verifyExperiment(masterScriptPath)


def verifyExperiment(masterScriptPath):
    # Initialize
    content = open(masterScriptPath).read()
    # Strip comments
    content = pattern_comment.sub('', content)
    # For each line,
    for line in content.splitlines():
        # If the line is empty, skip it
        if not line.strip(): continue
        # Unpack
        commandName, scriptPath = line.split()[:2]
        # Test
        subprocess.call('%s %s -t' % (commandName, scriptPath), shell=True)


if __name__ == '__main__':
    run()
