import json
import os
import re

from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter


class AnsibleResult(object):
    START = '\033\[\d+\;\d+m'
    END = '\033\[0m'
    DID_NOT_RUN_ERROR = 'Did not run / no information for this host.'

    def __init__(self, output, error, ips):
        """
        :type result: boolean
        :type success: dict
        """
        self.error = str(error)
        self.output = output
        self.ips = ips
        self.host_results = self._load()
        self.success = not [h for h in self.host_results if not h.success]

    def to_json(self):
        arr = [{'host':h.ip,'success':h.success,'error':h.error} for h in self.host_results]
        return json.dumps(arr)

    def _load(self):
        host_results = []
        recap_table = self._get_final_table()
        error_by_host = self._get_failing_hosts_errors()
        general_error = self._get_parsed_error()
        for ip in self.ips:
            # Success
            if recap_table.get(ip) == True:
                host_results.append(HostResult(ip, True))
            # Failed with error
            elif error_by_host.get(ip):
                host_results.append(HostResult(ip, False, error_by_host.get(ip)))
            # Failed without error
            elif recap_table.get(ip) == False:
                host_results.append(HostResult(ip, False, self.error))
            # Didn't run at all (no information for this ip)
            else:
                host_results.append(HostResult(ip, False, self.DID_NOT_RUN_ERROR+os.linesep+general_error))
        return host_results

    def _get_final_table(self):
        table = {}
        pattern = '^('+self.START+')?(?P<ip>\d+\.\d+\.\d+\.\d+)('+self.END+')?\s*\\t*\:.+unreachable=(?P<unreachable>\d+).+failed=(?P<failed>\d+)'
        matches = self._scan_for_groups(pattern)
        for m in matches:
            table[m['ip']] = True if int(m['unreachable'])+int(m['failed']) == 0 else False
        return table

    def _get_failing_hosts_errors(self):
        pattern = '^('+self.START+')?fatal: \[(?P<ip>\d+\.\d+\.\d+\.\d+)\]\:.*=>\s*(?P<details>\{.*\})\s*('+self.END+')?$'
        matches = self._scan_for_groups(pattern)
        ip_to_error = dict([(m['ip'], UnixToHtmlColorConverter().remove_strike(m['details'])) for m in matches])
        return ip_to_error

    def _scan_for_groups(self, pattern):
        matches = list(re.finditer(pattern, self.output, re.MULTILINE))
        matches = [m.groupdict() for m in matches]
        return matches

    def _get_parsed_error(self):
        pattern = '^('+self.START+')(\[ERROR\]\:|ERROR\!)\s*(?P<txt>.*)\s*('+self.END+')\s*'
        minimized_error = self.error.replace(os.linesep + os.linesep, os.linesep)
        matches = list(re.finditer(pattern, minimized_error, re.MULTILINE|re.DOTALL))
        if(matches):
            return '\n'.join([m.groupdict()['txt'] for m in matches])
        else:
            return self.error


class HostResult(object):
    def __init__(self, ip, success, error = None):
        self.ip = ip
        self.success = success
        self.error = error