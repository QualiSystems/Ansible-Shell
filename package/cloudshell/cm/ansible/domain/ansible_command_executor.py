import subprocess

class AnsibleCommandExecutor(object):
    def __init__(self,outputParser, playbookFile, inventoryFile, pemFile):
        self.playbookFile = playbookFile
        self.inventoryFile = inventoryFile
        self.pemFile = pemFile
        self.outputParser = outputParser



    def executeCommand(self, args = None):
        shellCommand = self._createShellCommand(args)
        #TODO: disable fetch data
        output = subprocess.check_output(shellCommand)
        if self.outputParser:
            output = self.outputParser.parse()
        return output

    def _createShellCommand(self, args):
        command = "ansible"

        if self.playbookFile:
            command += "-playbook " + self.playbookFile
        if self.inventoryFile:
            command += " -i " + self.inventoryFile
        if self.pemFile:
            command += " --private-key " + self.pemFile
        if args:
            command += " " + args
        command += " -v"
        return command
