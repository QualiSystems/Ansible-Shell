import re



class AnsiblePlaybookParser(object):

    def __init__(self, file_system):
        self.file_system = file_system

    def _isfailed(self, raw, playbook_file_name):
        matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)", raw)
        retryFile = self.file_system.exists(playbook_file_name + ".retry")
        if matches or retryFile:
            return True
        return False

    def parse(self, raw, playbook_file_name):
        success = not self._isfailed(raw, playbook_file_name)
        return AnsibleResult(raw , success)

class AnsibleResult(object):
    def __init__(self, result, success):
        self.Success = success
        self.Result = result


