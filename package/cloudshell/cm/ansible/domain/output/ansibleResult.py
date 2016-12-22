import re



class AnsiblePlaybookParser(object):

    def _isfailed(self, raw, playbook_file_name, filesystems_service):
        matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)", raw)
        retryFile = filesystems_service.exists(playbook_file_name + ".retry")
        if matches or retryFile:
            return True
        return False

    def parse(self, raw, playbook_file_name, filesystems_service):
        success = not self._isfailed(raw, playbook_file_name, filesystems_service)
        return AnsibleResult(raw , success)

class AnsibleResult(object):
    def __init__(self, result, success):
        self.Success = success
        self.Result = result


