import json
import re


class AnsibleResult(object):
    START = '\033\[\d+\;\d+m'
    END = '\033\[0m'

    def __init__(self, success, output=None, error=None):
        """
        :type result: boolean
        :type success: dict
        """
        self.success = success
        self.error = error
        self.failed_hosts = self._parse_failed_hosts_from_output(output) if output else None

    def to_json(self):
        data = {
            'error': self.error,
            'hosts': self.failed_hosts
        }
        return json.dumps(data)

    def _parse_failed_hosts_from_output(self, output):
        pattern = '^('+self.START+')?fatal: \[(?P<ip>\d+\.\d+\.\d+\.\d+)\]\:.*=>\s*(?P<details>\{.*\})\s*('+self.END+')?$'
        matches = list(re.finditer(pattern, output, re.MULTILINE))
        ip_to_error = dict([(m2.groupdict()['ip'],m2.groupdict()['details']) for m2 in matches])
        return ip_to_error