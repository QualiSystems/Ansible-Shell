from unittest import TestCase

from cloudshell.api.cloudshell_api import AttributeValueInfo
from mock import Mock

from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfigurationParser


class TestAnsibleConfigurationParser(TestCase):

    def setUp(self):
        self.api = Mock()
        self.parser = AnsibleConfigurationParser(self.api)

    def test_cannot_parse_json_without_repository_details(self):
        json = '{}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('Missing "repositoryDetails" node.', str(context.exception))

    def test_cannot_parse_json_without_repository_url(self):
        json = '{"repositoryDetails":{}}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('Missing "repositoryDetails.url" node.', str(context.exception))

    def test_cannot_parse_json_with_an_empty_repository_url(self):
        json = '{"repositoryDetails":{"url":""}}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('"repositoryDetails.url" node cannot be empty.', str(context.exception))

    def test_cannot_parse_json_without_hosts_detalis(self):
        json = '{"repositoryDetails":{"url":"someurl"}}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('Missing "hostsDetails" node.', str(context.exception))

    def test_cannot_parse_json_with_an_empty_hosts_detalis(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostsDetails":[]}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('"hostsDetails" node cannot be empty.', str(context.exception))

    def test_cannot_parse_json_with_host_with_an_empty_address(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostsDetails":[{}]}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('Missing "ip" node in 1 hosts', str(context.exception))

    def test_cannot_parse_json_with_host_with_an_empty_connection_method(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostsDetails":[{"ip":"x.x.x.x"}]}'
        with self.assertRaises(SyntaxError) as context:
            self.parser.json_to_object(json)
        self.assertIn('Missing "connectionMethod" node in 1 hosts', str(context.exception))

    def test_sanity(self):
        def wrapIt(x):
            m = Mock()
            m.Value = 'decrypted-' + x
            return m
        self.api.DecryptPassword.side_effect = lambda x: wrapIt(x)
        json = """
{
    "additionalArgs": "A",
    "repositoryDetails" : {
        "url": "B",
        "username": "C",
        "password": "D"
    },
    "hostsDetails": [
    {
        "ip": "E",
        "username": "F",
        "password": "G",
        "accessKey": "H",
        "connectionMethod": "IiIiI",
        "groups": ["J1","J2"],
        "parameters": [{"name":"K11","value":"K12"}, {"name":"K21","value":"K22"}]
    },
    {
        "ip": "E2",
        "connectionMethod": "I2"
    }]
}"""
        conf = self.parser.json_to_object(json)
        self.assertEqual("A", conf.additional_cmd_args)
        self.assertEqual("B", conf.playbook_repo.url)
        self.assertEqual("C", conf.playbook_repo.username)
        self.assertEqual("D", conf.playbook_repo.password)
        host1 = next((h for h in conf.hosts_conf if h.ip == 'E'), None)
        self.assertEqual("F", host1.username)
        self.assertEqual("decrypted-G", host1.password)
        self.assertEqual("decrypted-H", host1.access_key)
        self.assertEqual("iiiii", host1.connection_method)
        self.assertEqual(False, host1.connection_secured)
        self.assertEquals(['J1','J2'], host1.groups)
        self.assertEquals('K12', host1.parameters['K11'])
        self.assertEquals('K22', host1.parameters['K21'])
        host1 = next((h for h in conf.hosts_conf if h.ip == 'E2'), None)
        self.assertIsNotNone(host1)
        self.api.DecryptPassword.assert_any_call('G')
        self.api.DecryptPassword.assert_any_call('H')