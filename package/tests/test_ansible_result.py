import json
import os
from unittest import TestCase

from cloudshell.cm.ansible.domain.output.ansible_result import AnsibleResult
from tests.mocks.file_system_service_mock import FileSystemServiceMock

def get_error_for(result, ip):
    return next((h.error for h in result.host_results if h.ip == ip))

class TestAnsibleResult(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_result_should_fail_on_general_ansible_error(self):
        resultTxt = """
\033[0;31mERROR! 'tasks_SFSDFEG' is not a valid attribute for a Play"""+os.linesep+"""The error appears to have\033[0m"""
        result = AnsibleResult('', resultTxt, ['192.168.85.11'])
        self.assertFalse(result.success)
        self.assertEqual('Did not run / no information for this host.'+os.linesep+'\'tasks_SFSDFEG\' is not a valid attribute for a Play'+os.linesep+'The error appears to have',
                          get_error_for(result, '192.168.85.11'))

    def test_result_should_fail_on_unreachable(self):
        resultTxt = """
PLAY [linux_servers] ***********************************************************

TASK [setup] *******************************************************************
\033[1;31mfatal: [192.168.85.11]: UNREACHABLE! => {"changed": false, "msg": "Authentication failure.", "unreachable": true}\033[0m
    to retry, use: --limit @.:/playbook2.retry

PLAY RECAP *********************************************************************
\033[0;31m192.168.85.11\033[0m              : ok=0    changed=0    \033[1;31munreachable=1   \033[0m failed=0"""
        result = AnsibleResult(resultTxt, '', ['192.168.85.11'])
        self.assertFalse(result.success)
        self.assertEqual('{"changed": false, "msg": "Authentication failure.", "unreachable": true}',
                          get_error_for(result, '192.168.85.11'))

    def test_result_should_fail_on_failed(self):
        resultTxt = """
PLAY [linux_servers] ***********************************************************

TASK [setup] *******************************************************************
\033[0;32mok: [192.168.85.11]\033[0m

TASK [Do something stupid] *****************************************************
\033[0;31mfatal: [192.168.85.11]: FAILED! => {"changed": false, "cmd": "tauch /tmp/f", "failed": true, "msg": "[Errno 2] No such file or directory", "rc": 2}\033[0m
	to retry, use: --limit @.:/playbook2.retry

PLAY RECAP *********************************************************************
\033[0;31m192.168.85.11\033[0m              : \033[0;32mok=1   \033[0m changed=0    unreachable=0    \033[0;31mfailed=1   \033[0m"""
        result = AnsibleResult(resultTxt, '', ['192.168.85.11'])
        self.assertFalse(result.success)
        self.assertEqual('{"changed": false, "cmd": "tauch /tmp/f", "failed": true, "msg": "[Errno 2] No such file or directory", "rc": 2}',
                          get_error_for(result, '192.168.85.11'))

    def test_result_should_be_true(self):
        resultTxt = """
PLAY [linux_servers] ***********************************************************

TASK [setup] *******************************************************************
\033[0;32mok: [192.168.85.11]\033[0m

TASK [geerlingguy.apache : Include OS-specific variables.] *********************
\033[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}\033[0m

TASK [geerlingguy.apache : Define apache_packages.] ****************************
\033[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}\033[0m

PLAY RECAP *********************************************************************
\033[0;32m192.168.85.11\033[0m              : \033[0;32mok=12  \033[0m changed=1    unreachable=0    failed=0
           """
        result = AnsibleResult(resultTxt, '', ['192.168.85.11'])
        self.assertTrue(result.success)

        def test_result_should_contain_stderr_in_no_error_msg_found(self):
            resultTxt = """
PLAY [linux_servers] ***********************************************************

TASK [setup] *******************************************************************
\033[0;32mok: [192.168.85.11]\033[0m

TASK [Do something stupid] *****************************************************

PLAY RECAP *********************************************************************
\033[0;31m192.168.85.11\033[0m              : \033[0;32mok=1   \033[0m changed=0    unreachable=0    \033[0;31mfailed=1   \033[0m"""
            result = AnsibleResult(resultTxt, 'general error', ['192.168.85.11'])
            self.assertFalse(result.success)
            self.assertEqual('general error',
                              get_error_for(result, '192.168.85.11'))

        def test_result_should_contain_error_for_unrun_hosts(self):
            resultTxt = """
PLAY [linux_servers] ***********************************************************

TASK [setup] *******************************************************************

TASK [Do something stupid] *****************************************************

PLAY RECAP *********************************************************************"""
            result = AnsibleResult(resultTxt, 'general error', ['192.168.85.11'])
            self.assertFalse(result.success)
            self.assertIn(AnsibleResult.DID_NOT_RUN_ERROR,
                          get_error_for(result, '192.168.85.11'))

    def test_result_to_json(self):
        result = AnsibleResult('', 'error', ['192.168.85.11','192.168.85.12'])
        json_str = result.to_json()
        escapted_linesep = json.dumps(os.linesep).strip('"')
        self.assertEqual('[{"host": "192.168.85.11", "success": false, "error": "'+AnsibleResult.DID_NOT_RUN_ERROR+escapted_linesep+'error"}, \
{"host": "192.168.85.12", "success": false, "error": "'+AnsibleResult.DID_NOT_RUN_ERROR+escapted_linesep+'error"}]', json_str)

        # testing = """Using /tmp/tmpuPFhNB/ansible.cfg as config file
        #
        # PLAY [linux_servers] ***********************************************************
        #
        # TASK [setup] *******************************************************************
        # \033[0;32mok: [192.168.85.11]\033[0m
        #
        # TASK [geerlingguy.apache : Include OS-specific variables.] *********************
        # \033[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}\033[0m
        #
        # TASK [geerlingguy.apache : Define apache_packages.] ****************************
        # \033[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}\033[0m
        #
        # TASK [geerlingguy.apache : include] ********************************************
        # \033[0;36mincluded: /tmp/tmpuPFhNB/roles/geerlingguy.apache/tasks/setup-RedHat.yml for 192.168.85.11\033[0m
        #
        # TASK [geerlingguy.apache : Ensure Apache is installed on RHEL.] ****************
        # \033[0;32mok: [192.168.85.11] => (item=[u'httpd', u'httpd-devel', u'mod_ssl', u'openssh']) => {"changed": false, "item": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "msg": "", "rc": 0, "results": ["httpd-2.4.6-45.el7.centos.x86_64 providing httpd is already installed", "httpd-devel-2.4.6-45.el7.centos.x86_64 providing httpd-devel is already installed", "mod_ssl-1:2.4.6-45.el7.centos.x86_64 providing mod_ssl is already installed", "openssh-6.6.1p1-12.el7_1.x86_64 providing openssh is already installed"]}\033[0m
        #
        # TASK [geerlingguy.apache : Get installed version of Apache.] *******************
        # \033[0;32mok: [192.168.85.11] => {"changed": false, "cmd": "/usr/sbin/httpd -v", "delta": "0:00:00.075278", "END": "2016-12-19 09:20:00.642705", "rc": 0, "START": "2016-12-19 09:20:00.567427", "stderr": "", "stdout": "Server version: Apache/2.4.6 (CentOS)\nServer built:   Nov 14 2016 18:04:44", "stdout_lines": ["Server version: Apache/2.4.6 (CentOS)", "Server built:   Nov 14 2016 18:04:44"], "warnings": []}\033[0m
        #
        # TASK [geerlingguy.apache : Create apache_version variable.] ********************
        # \033[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_version": "2.4.6"}, "changed": false}\033[0m
        #
        # TASK [geerlingguy.apache : include_vars] ***************************************
        # \033[0;36mskipping: [192.168.85.11] => {"changed": false, "skip_reason": "Conditional check failed", "skipped": true}\033[0m
        #
        # TASK [geerlingguy.apache : include_vars] ***************************************
        # \033[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_default_vhost_filename": "000-default.conf", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}], "apache_vhosts_version": "2.4"}, "changed": false}\033[0m
        #
        # TASK [geerlingguy.apache : include] ********************************************
        # \033[0;36mincluded: /tmp/tmpuPFhNB/roles/geerlingguy.apache/tasks/configure-RedHat.yml for 192.168.85.11\033[0m
        #
        # TASK [geerlingguy.apache : Configure Apache.] **********************************
        # \033[0;32mok: [192.168.85.11] => (item={u'regexp': u'^Listen ', u'line': u'Listen 80'}) => {"backup": "", "changed": false, "item": {"line": "Listen 80", "regexp": "^Listen "}, "msg": ""}\033[0m
        #
        # TASK [geerlingguy.apache : Check whether certificates defined in vhosts exist.]
        #
        # TASK [geerlingguy.apache : Add apache vhosts configuration.] *******************
        # \033[0;32mok: [192.168.85.11] => {"changed": false, "gid": 0, "group": "root", "mode": "0644", "owner": "root", "path": "/etc/httpd/conf.d/vhosts.conf", "secontext": "system_u:object_r:httpd_config_t:s0", "size": 255, "state": "file", "uid": 0}\033[0m
        #
        # TASK [geerlingguy.apache : Ensure Apache has selected state and enabled on boot.] ***
        # \033[0;32mok: [192.168.85.11] => {"changed": false, "enabled": true, "name": "httpd", "state": "started", "status": {"ActiveEnterTimestamp": "Mon 2016-12-19 05:26:02 EST", "ActiveEnterTimestampMonotonic": "10756839491", "ActiveExitTimestamp": "Mon 2016-12-19 05:26:01 EST", "ActiveExitTimestampMonotonic": "10755607475", "ActiveState": "active", "After": "tmp.mount remote-fs.target nss-lookup.target systemd-journald.socket system.slice basic.target network.target -.mount", "AllowIsolate": "no", "AssertResult": "yes", "AssertTimestamp": "Mon 2016-12-19 05:26:02 EST", "AssertTimestampMonotonic": "10756641461", "Before": "shutdown.target multi-user.target", "BlockIOAccounting": "no", "BlockIOWeight": "18446744073709551615", "CPUAccounting": "no", "CPUQuotaPerSecUSec": "infinity", "CPUSchedulingPolicy": "0", "CPUSchedulingPriority": "0", "CPUSchedulingResetOnFork": "no", "CPUShares": "18446744073709551615", "CanIsolate": "no", "CanReload": "yes", "CanStart": "yes", "CanStop": "yes", "CapabilityBoundingSet": "18446744073709551615", "ConditionResult": "yes", "ConditionTimestamp": "Mon 2016-12-19 05:26:02 EST", "ConditionTimestampMonotonic": "10756641460", "Conflicts": "shutdown.target", "ControlGroup": "/system.slice/httpd.service", "ControlPID": "0", "DefaultDependencies": "yes", "Delegate": "no", "Description": "The Apache HTTP Server", "DevicePolicy": "auto", "Documentation": "man:httpd(8) man:apachectl(8)", "EnvironmentFile": "/etc/sysconfig/httpd (ignore_errors=no)", "ExecMainCode": "0", "ExecMainExitTimestampMonotonic": "0", "ExecMainPID": "7135", "ExecMainStartTimestamp": "Mon 2016-12-19 05:26:02 EST", "ExecMainStartTimestampMonotonic": "10756643632", "ExecMainStatus": "0", "ExecReload": "{ path=/usr/sbin/httpd ; argv[]=/usr/sbin/httpd $OPTIONS -k graceful ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }", "ExecStart": "{ path=/usr/sbin/httpd ; argv[]=/usr/sbin/httpd $OPTIONS -DFOREGROUND ; ignore_errors=no ; start_time=[Mon 2016-12-19 05:26:02 EST] ; stop_time=[n/a] ; pid=7135 ; code=(null) ; status=0/0 }", "ExecStop": "{ path=/bin/kill ; argv[]=/bin/kill -WINCH ${MAINPID} ; ignore_errors=no ; start_time=[Mon 2016-12-19 05:26:01 EST] ; stop_time=[Mon 2016-12-19 05:26:01 EST] ; pid=7130 ; code=exited ; status=0 }", "FailureAction": "none", "FileDescriptorStoreMax": "0", "FragmentPath": "/usr/lib/systemd/system/httpd.service", "GuessMainPID": "yes", "IOScheduling": "0", "Id": "httpd.service", "IgnoreOnIsolate": "no", "IgnoreOnSnapshot": "no", "IgnoreSIGPIPE": "yes", "InactiveEnterTimestamp": "Mon 2016-12-19 05:26:02 EST", "InactiveEnterTimestampMonotonic": "10756639637", "InactiveExitTimestamp": "Mon 2016-12-19 05:26:02 EST", "InactiveExitTimestampMonotonic": "10756643750", "JobTimeoutAction": "none", "JobTimeoutUSec": "0", "KillMode": "control-group", "KillSignal": "18", "LimitAS": "18446744073709551615", "LimitCORE": "18446744073709551615", "LimitCPU": "18446744073709551615", "LimitDATA": "18446744073709551615", "LimitFSIZE": "18446744073709551615", "LimitLOCKS": "18446744073709551615", "LimitMEMLOCK": "65536", "LimitMSGQUEUE": "819200", "LimitNICE": "0", "LimitNOFILE": "4096", "LimitNPROC": "31219", "LimitRSS": "18446744073709551615", "LimitRTPRIO": "0", "LimitRTTIME": "18446744073709551615", "LimitSIGPENDING": "31219", "LimitSTACK": "18446744073709551615", "LoadState": "loaded", "MainPID": "7135", "MemoryAccounting": "no", "MemoryCurrent": "18446744073709551615", "MemoryLimit": "18446744073709551615", "MountFlags": "0", "Names": "httpd.service", "NeedDaemonReload": "no", "Nice": "0", "NoNewPrivileges": "no", "NonBlocking": "no", "NotifyAccess": "main", "OOMScoreAdjust": "0", "OnFailureJobMode": "replace", "PermissionsStartOnly": "no", "PrivateDevices": "no", "PrivateNetwork": "no", "PrivateTmp": "yes", "ProtectHome": "no", "ProtectSystem": "no", "RefuseManualStart": "no", "RefuseManualStop": "no", "RemainAfterExit": "no", "Requires": "basic.target -.mount", "RequiresMountsFor": "/var/tmp", "Restart": "no", "RestartUSec": "100ms", "Result": "success", "RootDirectoryStartOnly": "no", "RuntimeDirectoryMode": "0755", "SameProcessGroup": "no", "SecureBits": "0", "SendSIGHUP": "no", "SendSIGKILL": "yes", "Slice": "system.slice", "StandardError": "inherit", "StandardInput": "null", "StandardOutput": "journal", "StartLimitAction": "none", "StartLimitBurst": "5", "StartLimitInterval": "10000000", "StartupBlockIOWeight": "18446744073709551615", "StartupCPUShares": "18446744073709551615", "StatusErrno": "0", "StatusText": "Total requests: 10; Current requests/sec: 0; Current traffic:   0 B/sec", "StopWhenUnneeded": "no", "SubState": "running", "SyslogLevelPrefix": "yes", "SyslogPriority": "30", "SystemCallErrorNumber": "0", "TTYReset": "no", "TTYVHangup": "no", "TTYVTDisallocate": "no", "TimeoutStartUSec": "1min 30s", "TimeoutStopUSec": "1min 30s", "TimerSlackNSec": "50000", "Transient": "no", "Type": "notify", "UMask": "0022", "UnitFilePreset": "disabled", "UnitFileState": "enabled", "WantedBy": "multi-user.target", "Wants": "system.slice", "WatchdogTimestamp": "Mon 2016-12-19 05:26:02 EST", "WatchdogTimestampMonotonic": "10756839305", "WatchdogUSec": "0"}}\033[0m
        #
        # PLAY RECAP *********************************************************************
        # \033[0;32m192.168.85.11\033[0m              : \033[0;32mok=12  \033[0m changed=0    unreachable=0    failed=0
        #
        # """

