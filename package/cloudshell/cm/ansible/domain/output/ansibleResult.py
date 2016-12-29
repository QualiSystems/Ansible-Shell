import json
import re


class AnsiblePlaybookParser(object):
    START = '\033\[\d+\;\d+m'
    END = '\033\[0m'

    def __init__(self, file_system):
        self.file_system = file_system

    def parse(self, output):
        details_by_ip = self._get_failures_details_by_ips(output)
        if not details_by_ip:
            return AnsibleResult.ok()
        else:
            return AnsibleResult.error(details_by_ip)

    def _get_failures_details_by_ips(self, output):
        pattern = '^('+self.START+')?fatal: \[(?P<ip>\d+\.\d+\.\d+\.\d+)\]\:.*=>\s*(?P<details>\{.*\})\s*('+self.END+')?$'
        matches = list(re.finditer(pattern, output, re.MULTILINE))
        ip_to_error = dict([(m2.groupdict()['ip'],m2.groupdict()['details']) for m2 in matches])
        return ip_to_error

    # def _isfailed(self, raw, playbook_file_name):
    #     matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)", raw)
    #     retryFile = self.file_system.exists(playbook_file_name + ".retry")
    #     if matches or retryFile:
    #         return True
    #     return False

    # def parse(self, raw, playbook_file_name):
    #     success = not self._isfailed(raw, playbook_file_name)
    #     return AnsibleResult(raw , success)

    # def _get_failed_ips_from_summary(self, output):
    #     ips = []
    #     pattern = '^('+self.START+')?(?P<ip>\d+\.\d+\.\d+\.\d+).*(unreachable=[1-9]+|failed=[1-9]+).*$'
    #     matches = list(re.finditer(pattern, output, re.MULTILINE))
    #     for m in [m.groupdict() for m in matches]:
    #         ips.append(m['ip'])
    #     return ips

class AnsibleResult(object):
    def __init__(self, success, failed_hosts=None):
        """
        :type result: boolean
        :type success: dict
        """
        self.success = success
        self.failed_hosts = failed_hosts

    @staticmethod
    def ok():
        return AnsibleResult(True)

    @staticmethod
    def error(data):
        return AnsibleResult(False, data)

    def failure_to_json(self):
        return json.dumps(self.failed_hosts)