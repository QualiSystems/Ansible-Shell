from unittest import TestCase

from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfigurationParser


class TestAnsibleConfigurationParser(TestCase):

    def test_cannot_parse_json_without_repository_details(self):
        json = '{}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('Missing "repositoryDetails" node.', context.exception.message)

    def test_cannot_parse_json_without_repository_url(self):
        json = '{"repositoryDetails":{}}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('Missing "repositoryDetails.url" node.', context.exception.message)

    def test_cannot_parse_json_with_an_empty_repository_url(self):
        json = '{"repositoryDetails":{"url":""}}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('"repositoryDetails.url" node cannot be empty.', context.exception.message)

    def test_cannot_parse_json_without_hosts_detalis(self):
        json = '{"repositoryDetails":{"url":"someurl"}}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('Missing "hostsDetails" node.', context.exception.message)

    def test_cannot_parse_json_with_an_empty_hosts_detalis(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostsDetails":[]}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('"hostsDetails" node cannot be empty.', context.exception.message)

    def test_cannot_parse_json_with_host_with_an_empty_address(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostsDetails":[{}]}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('Missing "ip" node in 1 hosts', context.exception.message)

    def test_cannot_parse_json_with_host_with_an_empty_connection_method(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostsDetails":[{"ip":"x.x.x.x"}]}'
        with self.assertRaises(SyntaxError) as context:
            AnsibleConfigurationParser.json_to_object(json)
        self.assertIn('Missing "connectionMethod" node in 1 hosts', context.exception.message)

    def test_sanity(self):
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
        conf = AnsibleConfigurationParser.json_to_object(json)
        self.assertEquals("A", conf.additional_cmd_args)
        self.assertEquals("B", conf.playbook_repo.url)
        self.assertEquals("C", conf.playbook_repo.username)
        self.assertEquals("D", conf.playbook_repo.password)
        host1 = next((h for h in conf.hosts_conf if h.ip == 'E'), None)
        self.assertEquals("F", host1.username)
        self.assertEquals("G", host1.password)
        self.assertEquals("H", host1.access_key)
        self.assertEquals("iiiii", host1.connection_method)
        self.assertItemsEqual(['J1','J2'], host1.groups)
        self.assertItemsEqual('K12', host1.parameters['K11'])
        self.assertItemsEqual('K22', host1.parameters['K21'])
        host1 = next((h for h in conf.hosts_conf if h.ip == 'E2'), None)
        self.assertIsNotNone(host1)