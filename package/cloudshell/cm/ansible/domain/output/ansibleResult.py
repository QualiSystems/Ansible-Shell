import re

class AnsiblePlaybookParser(object):

    def _isfailed(self, raw):
        matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)", raw)
        if matches:
            return True
        return False

    def parse(self, raw):
        success = not self._isfailed(raw)
        return AnsibleResult(raw , success)

class AnsibleResult(object):
    def __init__(self, result, success):
        self.Success = success
        self.Result = result