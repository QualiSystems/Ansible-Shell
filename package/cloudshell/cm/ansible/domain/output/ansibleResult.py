import re


class AnsibleTask(object):
    def __init__(self, name):
        self.Success = False
        self.Name = name


class AnsiblePlaybookResult(object):
    failed = ""

    def isfailed(self):
        matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)",self.Raw)
        if matches:
            return True
        return False

    def __init__(self, raw):
        self.Tasks = []
        self.Raw = raw
        self.Success = not self.isfailed();

raw = """Using /etc/ansible/ansible.cfg as config file

PLAY [testing] *****************************************************************

TASK [setup] *******************************************************************
^[[0;32mok: [test1]^[[0m

TASK [Sengind ping] ************************************************************
^[[0;32mok: [test1] => {"changed": false, "ping": "pong"}^[[0m

PLAY RECAP *********************************************************************
^[[0;32mtest1^[[0m                      : ^[[0;32mok=2   ^[[0m changed=0    unreachable=1    failed=1

"""
matches = re.search("(unreachable=[1-9]+|failed=[1-9]+)",raw)
AnsiblePlaybookResult(raw)