from unittest import TestCase

from cloudshell.cm.ansible.domain.output.ansibleResult import AnsiblePlaybookParser
from tests.mocks.file_system_service_mock import FileSystemServiceMock


class TestUnixToHtmlColorConverter(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()
        self.parser = AnsiblePlaybookParser(self.file_system)
        self.playbook_file_name = "myPlaybook.yaml"
    def test_result_should_fail_on_unreachable(self):
        resultTxt = """
         PLAY [linux_servers] ***********************************************************

         TASK [setup] *******************************************************************
         ^[[0;32mok: [192.168.85.11]^[[0m

         TASK [geerlingguy.apache : Include OS-specific variables.] *********************
         ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}^[[0m

         TASK [geerlingguy.apache : Define apache_packages.] ****************************
         ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}^[[0m

        PLAY RECAP *********************************************************************
        ^[[0;32m192.168.85.11^[[0m              : ^[[0;32mok=12  ^[[0m changed=0    unreachable=0    failed=2
        """
        result = self.parser.parse(resultTxt,self.playbook_file_name)
        self.assertFalse(result.Success)

    def test_result_should_fail_on_failed(self):
        resultTxt = """
            PLAY [linux_servers] ***********************************************************

            TASK [setup] *******************************************************************
            ^[[0;32mok: [192.168.85.11]^[[0m

            TASK [geerlingguy.apache : Include OS-specific variables.] *********************
            ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}^[[0m

            TASK [geerlingguy.apache : Define apache_packages.] ****************************
            ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}^[[0m

           PLAY RECAP *********************************************************************
           ^[[0;32m192.168.85.11^[[0m              : ^[[0;32mok=12  ^[[0m changed=0    unreachable=1    failed=0
           """
        result = self.parser.parse(resultTxt, self.playbook_file_name)
        self.assertFalse(result.Success)

    def test_result_should_fail_on_retryFile(self):
        resultTxt = """
            PLAY [linux_servers] ***********************************************************

            TASK [setup] *******************************************************************
            ^[[0;32mok: [192.168.85.11]^[[0m

            TASK [geerlingguy.apache : Include OS-specific variables.] *********************
            ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}^[[0m

            TASK [geerlingguy.apache : Define apache_packages.] ****************************
            ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}^[[0m

           PLAY RECAP *********************************************************************
                    to retry, use: --limit @/home/myPlaybook.yaml.retry
           ^[[0;32m192.168.85.11^[[0m              : ^[[0;32mok=12  ^[[0m changed=0    unreachable=0    failed=0
           """
        self.file_system.create_file(self.playbook_file_name + ".retry")
        result = self.parser.parse(resultTxt, self.playbook_file_name)
        self.assertFalse(result.Success)

    def test_result_should_be_true(self):
        resultTxt = """
            PLAY [linux_servers] ***********************************************************

            TASK [setup] *******************************************************************
            ^[[0;32mok: [192.168.85.11]^[[0m

            TASK [geerlingguy.apache : Include OS-specific variables.] *********************
            ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}^[[0m

            TASK [geerlingguy.apache : Define apache_packages.] ****************************
            ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}^[[0m

           PLAY RECAP *********************************************************************
           ^[[0;32m192.168.85.11^[[0m              : ^[[0;32mok=12  ^[[0m changed=1    unreachable=0    failed=0
           """
        result = self.parser.parse(resultTxt, self.playbook_file_name)
        self.assertTrue(result.Success)



        # testing = """Using /tmp/tmpuPFhNB/ansible.cfg as config file
        #
        # PLAY [linux_servers] ***********************************************************
        #
        # TASK [setup] *******************************************************************
        # ^[[0;32mok: [192.168.85.11]^[[0m
        #
        # TASK [geerlingguy.apache : Include OS-specific variables.] *********************
        # ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"__apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "apache_conf_path": "/etc/httpd/conf.d", "apache_daemon": "httpd", "apache_daemon_path": "/usr/sbin/", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}, {"line": "NameVirtualHost {{ apache_listen_ip }}:{{ apache_listen_port }}", "regexp": "^#?NameVirtualHost "}], "apache_server_root": "/etc/httpd", "apache_service": "httpd", "apache_vhosts_version": "2.2"}, "changed": false}^[[0m
        #
        # TASK [geerlingguy.apache : Define apache_packages.] ****************************
        # ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_packages": ["httpd", "httpd-devel", "mod_ssl", "openssh"]}, "changed": false}^[[0m
        #
        # TASK [geerlingguy.apache : include] ********************************************
        # ^[[0;36mincluded: /tmp/tmpuPFhNB/roles/geerlingguy.apache/tasks/setup-RedHat.yml for 192.168.85.11^[[0m
        #
        # TASK [geerlingguy.apache : Ensure Apache is installed on RHEL.] ****************
        # ^[[0;32mok: [192.168.85.11] => (item=[u'httpd', u'httpd-devel', u'mod_ssl', u'openssh']) => {"changed": false, "item": ["httpd", "httpd-devel", "mod_ssl", "openssh"], "msg": "", "rc": 0, "results": ["httpd-2.4.6-45.el7.centos.x86_64 providing httpd is already installed", "httpd-devel-2.4.6-45.el7.centos.x86_64 providing httpd-devel is already installed", "mod_ssl-1:2.4.6-45.el7.centos.x86_64 providing mod_ssl is already installed", "openssh-6.6.1p1-12.el7_1.x86_64 providing openssh is already installed"]}^[[0m
        #
        # TASK [geerlingguy.apache : Get installed version of Apache.] *******************
        # ^[[0;32mok: [192.168.85.11] => {"changed": false, "cmd": "/usr/sbin/httpd -v", "delta": "0:00:00.075278", "end": "2016-12-19 09:20:00.642705", "rc": 0, "start": "2016-12-19 09:20:00.567427", "stderr": "", "stdout": "Server version: Apache/2.4.6 (CentOS)\nServer built:   Nov 14 2016 18:04:44", "stdout_lines": ["Server version: Apache/2.4.6 (CentOS)", "Server built:   Nov 14 2016 18:04:44"], "warnings": []}^[[0m
        #
        # TASK [geerlingguy.apache : Create apache_version variable.] ********************
        # ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_version": "2.4.6"}, "changed": false}^[[0m
        #
        # TASK [geerlingguy.apache : include_vars] ***************************************
        # ^[[0;36mskipping: [192.168.85.11] => {"changed": false, "skip_reason": "Conditional check failed", "skipped": true}^[[0m
        #
        # TASK [geerlingguy.apache : include_vars] ***************************************
        # ^[[0;32mok: [192.168.85.11] => {"ansible_facts": {"apache_default_vhost_filename": "000-default.conf", "apache_ports_configuration_items": [{"line": "Listen {{ apache_listen_port }}", "regexp": "^Listen "}], "apache_vhosts_version": "2.4"}, "changed": false}^[[0m
        #
        # TASK [geerlingguy.apache : include] ********************************************
        # ^[[0;36mincluded: /tmp/tmpuPFhNB/roles/geerlingguy.apache/tasks/configure-RedHat.yml for 192.168.85.11^[[0m
        #
        # TASK [geerlingguy.apache : Configure Apache.] **********************************
        # ^[[0;32mok: [192.168.85.11] => (item={u'regexp': u'^Listen ', u'line': u'Listen 80'}) => {"backup": "", "changed": false, "item": {"line": "Listen 80", "regexp": "^Listen "}, "msg": ""}^[[0m
        #
        # TASK [geerlingguy.apache : Check whether certificates defined in vhosts exist.]
        #
        # TASK [geerlingguy.apache : Add apache vhosts configuration.] *******************
        # ^[[0;32mok: [192.168.85.11] => {"changed": false, "gid": 0, "group": "root", "mode": "0644", "owner": "root", "path": "/etc/httpd/conf.d/vhosts.conf", "secontext": "system_u:object_r:httpd_config_t:s0", "size": 255, "state": "file", "uid": 0}^[[0m
        #
        # TASK [geerlingguy.apache : Ensure Apache has selected state and enabled on boot.] ***
        # ^[[0;32mok: [192.168.85.11] => {"changed": false, "enabled": true, "name": "httpd", "state": "started", "status": {"ActiveEnterTimestamp": "Mon 2016-12-19 05:26:02 EST", "ActiveEnterTimestampMonotonic": "10756839491", "ActiveExitTimestamp": "Mon 2016-12-19 05:26:01 EST", "ActiveExitTimestampMonotonic": "10755607475", "ActiveState": "active", "After": "tmp.mount remote-fs.target nss-lookup.target systemd-journald.socket system.slice basic.target network.target -.mount", "AllowIsolate": "no", "AssertResult": "yes", "AssertTimestamp": "Mon 2016-12-19 05:26:02 EST", "AssertTimestampMonotonic": "10756641461", "Before": "shutdown.target multi-user.target", "BlockIOAccounting": "no", "BlockIOWeight": "18446744073709551615", "CPUAccounting": "no", "CPUQuotaPerSecUSec": "infinity", "CPUSchedulingPolicy": "0", "CPUSchedulingPriority": "0", "CPUSchedulingResetOnFork": "no", "CPUShares": "18446744073709551615", "CanIsolate": "no", "CanReload": "yes", "CanStart": "yes", "CanStop": "yes", "CapabilityBoundingSet": "18446744073709551615", "ConditionResult": "yes", "ConditionTimestamp": "Mon 2016-12-19 05:26:02 EST", "ConditionTimestampMonotonic": "10756641460", "Conflicts": "shutdown.target", "ControlGroup": "/system.slice/httpd.service", "ControlPID": "0", "DefaultDependencies": "yes", "Delegate": "no", "Description": "The Apache HTTP Server", "DevicePolicy": "auto", "Documentation": "man:httpd(8) man:apachectl(8)", "EnvironmentFile": "/etc/sysconfig/httpd (ignore_errors=no)", "ExecMainCode": "0", "ExecMainExitTimestampMonotonic": "0", "ExecMainPID": "7135", "ExecMainStartTimestamp": "Mon 2016-12-19 05:26:02 EST", "ExecMainStartTimestampMonotonic": "10756643632", "ExecMainStatus": "0", "ExecReload": "{ path=/usr/sbin/httpd ; argv[]=/usr/sbin/httpd $OPTIONS -k graceful ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }", "ExecStart": "{ path=/usr/sbin/httpd ; argv[]=/usr/sbin/httpd $OPTIONS -DFOREGROUND ; ignore_errors=no ; start_time=[Mon 2016-12-19 05:26:02 EST] ; stop_time=[n/a] ; pid=7135 ; code=(null) ; status=0/0 }", "ExecStop": "{ path=/bin/kill ; argv[]=/bin/kill -WINCH ${MAINPID} ; ignore_errors=no ; start_time=[Mon 2016-12-19 05:26:01 EST] ; stop_time=[Mon 2016-12-19 05:26:01 EST] ; pid=7130 ; code=exited ; status=0 }", "FailureAction": "none", "FileDescriptorStoreMax": "0", "FragmentPath": "/usr/lib/systemd/system/httpd.service", "GuessMainPID": "yes", "IOScheduling": "0", "Id": "httpd.service", "IgnoreOnIsolate": "no", "IgnoreOnSnapshot": "no", "IgnoreSIGPIPE": "yes", "InactiveEnterTimestamp": "Mon 2016-12-19 05:26:02 EST", "InactiveEnterTimestampMonotonic": "10756639637", "InactiveExitTimestamp": "Mon 2016-12-19 05:26:02 EST", "InactiveExitTimestampMonotonic": "10756643750", "JobTimeoutAction": "none", "JobTimeoutUSec": "0", "KillMode": "control-group", "KillSignal": "18", "LimitAS": "18446744073709551615", "LimitCORE": "18446744073709551615", "LimitCPU": "18446744073709551615", "LimitDATA": "18446744073709551615", "LimitFSIZE": "18446744073709551615", "LimitLOCKS": "18446744073709551615", "LimitMEMLOCK": "65536", "LimitMSGQUEUE": "819200", "LimitNICE": "0", "LimitNOFILE": "4096", "LimitNPROC": "31219", "LimitRSS": "18446744073709551615", "LimitRTPRIO": "0", "LimitRTTIME": "18446744073709551615", "LimitSIGPENDING": "31219", "LimitSTACK": "18446744073709551615", "LoadState": "loaded", "MainPID": "7135", "MemoryAccounting": "no", "MemoryCurrent": "18446744073709551615", "MemoryLimit": "18446744073709551615", "MountFlags": "0", "Names": "httpd.service", "NeedDaemonReload": "no", "Nice": "0", "NoNewPrivileges": "no", "NonBlocking": "no", "NotifyAccess": "main", "OOMScoreAdjust": "0", "OnFailureJobMode": "replace", "PermissionsStartOnly": "no", "PrivateDevices": "no", "PrivateNetwork": "no", "PrivateTmp": "yes", "ProtectHome": "no", "ProtectSystem": "no", "RefuseManualStart": "no", "RefuseManualStop": "no", "RemainAfterExit": "no", "Requires": "basic.target -.mount", "RequiresMountsFor": "/var/tmp", "Restart": "no", "RestartUSec": "100ms", "Result": "success", "RootDirectoryStartOnly": "no", "RuntimeDirectoryMode": "0755", "SameProcessGroup": "no", "SecureBits": "0", "SendSIGHUP": "no", "SendSIGKILL": "yes", "Slice": "system.slice", "StandardError": "inherit", "StandardInput": "null", "StandardOutput": "journal", "StartLimitAction": "none", "StartLimitBurst": "5", "StartLimitInterval": "10000000", "StartupBlockIOWeight": "18446744073709551615", "StartupCPUShares": "18446744073709551615", "StatusErrno": "0", "StatusText": "Total requests: 10; Current requests/sec: 0; Current traffic:   0 B/sec", "StopWhenUnneeded": "no", "SubState": "running", "SyslogLevelPrefix": "yes", "SyslogPriority": "30", "SystemCallErrorNumber": "0", "TTYReset": "no", "TTYVHangup": "no", "TTYVTDisallocate": "no", "TimeoutStartUSec": "1min 30s", "TimeoutStopUSec": "1min 30s", "TimerSlackNSec": "50000", "Transient": "no", "Type": "notify", "UMask": "0022", "UnitFilePreset": "disabled", "UnitFileState": "enabled", "WantedBy": "multi-user.target", "Wants": "system.slice", "WatchdogTimestamp": "Mon 2016-12-19 05:26:02 EST", "WatchdogTimestampMonotonic": "10756839305", "WatchdogUSec": "0"}}^[[0m
        #
        # PLAY RECAP *********************************************************************
        # ^[[0;32m192.168.85.11^[[0m              : ^[[0;32mok=12  ^[[0m changed=0    unreachable=0    failed=0
        #
        # """

