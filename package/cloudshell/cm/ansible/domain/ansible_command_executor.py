import subprocess


class AnsibleCommandExecutor(object):
    def __init__(self, outputParser):
        self.outputParser = outputParser

    def execute_playbook(self, playbook_file, inventory_file, args = None):
        shellCommand = self._createShellCommand(playbook_file, inventory_file, args)
        process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE)
        output=''
        CUNK_TO_READ = 512

        while True:
            pOut = process.stdout.read(CUNK_TO_READ)
            if process.poll() is not None:
                break
            output += pOut
            #TODO: write to output window. via api command
        # output = subprocess.check_output(shellCommand)
        return self.outputParser.parse(output)

    def _createShellCommand(self, playbook_file, inventory_file, args):
        command = "ansible"

        if playbook_file:
            command += "-playbook " + playbook_file
        if inventory_file:
            command += " -i " + inventory_file
        if args:
            command += " " + args
        command += " -v"
        return command