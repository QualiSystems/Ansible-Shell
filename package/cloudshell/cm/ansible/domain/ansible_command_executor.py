import subprocess

class AnsibleCommandExecutor(object):
    def __init__(self,outputParser, playbookFile, inventoryFile):
        self.playbookFile = playbookFile
        self.inventoryFile = inventoryFile
        self.outputParser = outputParser



    def executeCommand(self, args = None):
        shellCommand = self._createShellCommand(args)
        process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE)
        output=''
        CUNK_TO_READ = 512

        while True:
            pOut = process.stdout.read(CUNK_TO_READ)
            if not pOut and process.poll() != None:
                break
            output += pOut
            #TODO: write to output window. via api command
        # output = subprocess.check_output(shellCommand)
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
