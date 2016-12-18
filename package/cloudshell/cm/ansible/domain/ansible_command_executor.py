import subprocess

class AnsibleCommandExecutor(object):
    def __init__(self,outputParser, playbookFile, inventoryFile):
        self.playbookFile = playbookFile
        self.inventoryFile = inventoryFile
        self.outputParser = outputParser



    def executeCommand(self, args = None):
        shellCommand = self._createShellCommand(args)
        output = subprocess.check_output(shellCommand)
        return self.outputParser.parse(output)

    def _createShellCommand(self, args):
        command = "ansible"

        if self.playbookFile:
            command += "-playbook " + self.playbookFile
        if self.inventoryFile:
            command += " -i " + self.inventoryFile
        if args:
            command += " " + args
        command += " -v"
        return command
