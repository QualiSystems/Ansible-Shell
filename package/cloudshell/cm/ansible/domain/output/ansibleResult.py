import re

class AnsiblePlaybookParser(object):

    def _isfailed(self):
        matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)", self.Raw)
        if matches:
            return True
        return False

    def parse(self, raw):
        success = not self._isfailed()
        return AnsibleResult(raw , self.Success)

class AnsibleResult(object):
    def __init__(self, result, success):
        self.Success = success
        self.Result = result
