import json

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.cm.ansible.ansible_shell import AnsibleShell
from helper_code.sandbox_reporter import SandboxReporter
from helper_code.shell_connector_helpers import get_connector_endpoints
from helper_code.resource_helpers import get_resource_attribute_gen_agostic
from helper_code.parse_script_params import get_params_list_from_semicolon_sep_str
from helper_code.gitlab_api_url_validator import is_base_path_gitlab_api
from cloudshell.core.logger.qs_logger import get_qs_logger
from ansible_configuration import AnsibleConfiguration, HostConfiguration


# HOST OVERRIDE PARAMS - IF PRESENT ON RESOURCE THEY WILL OVERRIDE THE SERVICE DEFAULT
# TO BE CREATED IN SYSTEM AS GLOBAL ATTRIBUTE
ACCESS_KEY_PARAM = "Access Key"
CONNECTION_METHOD_PARAM = "Connection Method"
SCRIPT_PARAMS_PARAM = "Script Parameters"
INVENTORY_GROUP_PARAM = "Inventory Groups"
CONNECTION_SECURED_PARAM = "Connection Secured"


class AnsibleConfig2GDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.first_gen_ansible_shell = AnsibleShell()
        self.supported_protocols = ["http", "https"]
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def execute_playbook(self, context, cancellation_context, playbook_path):
        """
        :param ResourceCommandContext context:
        :param CancellationContext cancellation_context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        reporter = self._get_sandbox_reporter(context, api)
        ansible_config_json = self._get_ansible_config_json(context, api, reporter, playbook_path)

        reporter.info_out("Service '{}' is Executing Ansible Playbook...".format(context.resource.name))
        self.first_gen_ansible_shell.execute_playbook(context, ansible_config_json, cancellation_context)
        completed_msg = "Ansible Flow Completed for '{}'.".format(context.resource.name)
        reporter.info_out(completed_msg, log_only=True)
        return completed_msg

    def _is_path_supported_protocol(self, path):
        return any(path.startswith(protocol) for protocol in self.supported_protocols)

    @staticmethod
    def _append_gitlab_url_suffix(url, branch):
        """
        :param str url:
        :param str branch:
        :return:
        """
        raw_url_suffix = "/raw?"
        if raw_url_suffix not in url.lower():
            url += "/raw?ref={}".format(branch)
        return url

    def _build_repo_url(self, resource, playbook_path_input, reporter):
        """
        build URL based on hierarchy of inputs.
        1. Command inputs take precedence over service values
        2. full url on service takes precedence over base path
        3. base path concatenation last
        4. if input is not full url, then tries to concatenate with base bath on service
        :param AnsibleConfig2G resource:
        :param str playbook_path:
        :param SandboxReporter reporter:
        :return:
        """
        service_name = resource.name
        service_full_url = resource.playbook_url_full
        gitlab_branch = resource.gitlab_branch if resource.gitlab_branch else "master"
        base_path = resource.playbook_base_path
        service_playbook_path = resource.playbook_script_path

        # if no playbook input look for fallback values on service
        if not playbook_path_input:

            # FALLBACK TO FULL URL
            if service_full_url:
                is_gitlab_api = is_base_path_gitlab_api(service_full_url)
                if is_gitlab_api:
                    return self._append_gitlab_url_suffix(service_full_url, gitlab_branch)
                return service_full_url

            # FALLBACK TO BASE PATH
            if not base_path or not service_playbook_path:
                err_msg = "Input Error on Service '{}': No valid playbook inputs found".format(
                    service_name)
                reporter.err_out(err_msg)
                raise ValueError(err_msg)

            if base_path.endswith("/"):
                url = base_path + service_playbook_path
            else:
                url = base_path + "/" + service_playbook_path

            is_gitlab_api = is_base_path_gitlab_api(base_path)
            if is_gitlab_api:
                return self._append_gitlab_url_suffix(url, gitlab_branch)
            return url

        # COMMAND INPUT EXISTS

        # if playbook path input begins with a protocol then treat as full url
        if self._is_path_supported_protocol(playbook_path_input):
            is_gitlab_api = is_base_path_gitlab_api(playbook_path_input)
            if is_gitlab_api:
                return self._append_gitlab_url_suffix(playbook_path_input, gitlab_branch)
            return playbook_path_input

        # check that base path is populated
        if not base_path:
            err_msg = "Input Error on Service '{}': Repo Base Path not populated when using short path input".format(service_name)
            reporter.err_out(err_msg)
            raise ValueError(err_msg)

        # validate base path includes protocol
        if not self._is_path_supported_protocol(base_path):
            err_msg = "Input Error on Service '{}': Base Path does not begin with valid protocol. Currently supported: {}".format(service_name, self.supported_protocols)
            reporter.err_out(err_msg)
            raise ValueError(err_msg)

        if base_path.endswith("/"):
            url = base_path + playbook_path_input
        else:
            url = base_path + "/" + playbook_path_input

        is_gitlab_api = is_base_path_gitlab_api(url)
        if is_gitlab_api:
            return url + "/raw?ref={}".format(gitlab_branch)

        return url

    def _get_ansible_config_json(self, context, api, reporter, playbook_path):
        """
        :param ResourceCommandContext context:
        :param SandboxReporter reporter:
        :return:
        """
        resource = AnsibleConfig2G.create_from_context(context)
        service_connection_method = resource.connection_method
        service_inventory_groups = resource.inventory_groups
        service_script_parameters = resource.script_parameters
        service_additional_args = resource.ansible_cmd_args
        service_timeout_minutes = resource.timeout_minutes

        # initialize empty object
        ansi_conf = AnsibleConfiguration()

        # start populating
        ansi_conf.additionalArgs = service_additional_args if service_additional_args else None
        ansi_conf.timeoutMinutes = int(service_timeout_minutes) if service_timeout_minutes else 0

        # default host inputs
        if service_script_parameters:
            default_script_params = get_params_list_from_semicolon_sep_str(service_script_parameters)
        else:
            default_script_params = []

        # repo details
        ansi_conf.repositoryDetails.url = self._build_repo_url(resource, playbook_path, reporter)
        ansi_conf.repositoryDetails.username = resource.repo_user

        password_val = api.DecryptPassword(resource.repo_password).Value
        ansi_conf.repositoryDetails.password = password_val if password_val else None

        # get host details from connectors
        connectors = context.connectors
        if not connectors:
            no_connector_msg = "No Connectors On Ansible Service '{}'".format(resource.name)
            reporter.err_out(no_connector_msg)
            raise Exception(no_connector_msg)

        connector_endpoints = get_connector_endpoints(resource.name, connectors)

        # get details of endpoint resources
        resource_detail_objects = []
        for resource_name in connector_endpoints:
            try:
                resource_details = api.GetResourceDetails(resource_name)
            except Exception as e:
                err_msg = "Connected component '{}' is not a resource: {}".format(resource_name, str(e))
                reporter.err_out(err_msg)
            else:
                resource_detail_objects.append(resource_details)

        for curr_resource_obj in resource_detail_objects:
            host_conf = HostConfiguration()
            host_conf.ip = curr_resource_obj.Address

            attrs = curr_resource_obj.ResourceAttributes

            user_attr = get_resource_attribute_gen_agostic("User", attrs)
            host_conf.username = user_attr.Value if user_attr else ""

            password_attr = get_resource_attribute_gen_agostic("Password", attrs)
            host_conf.password = password_attr.Value if password_attr else None

            # OVERRIDE SERVICE ATTRIBUTES IF ATTRIBUTES EXIST ON RESOURCE

            # GROUPS
            ansible_group_attr = get_resource_attribute_gen_agostic(INVENTORY_GROUP_PARAM, attrs)
            host_conf.groups = ansible_group_attr.Value if ansible_group_attr else service_inventory_groups

            # ACCESS KEY
            access_key_attr = get_resource_attribute_gen_agostic(ACCESS_KEY_PARAM, attrs)
            host_conf.accessKey = access_key_attr.Value if access_key_attr else None

            # CONNECTION METHOD
            connection_method_attr = get_resource_attribute_gen_agostic(CONNECTION_METHOD_PARAM, attrs)
            host_conf.connectionMethod = connection_method_attr.Value if connection_method_attr else service_connection_method

            # CONNECTION SECURED
            connection_secured_attr = get_resource_attribute_gen_agostic(CONNECTION_SECURED_PARAM, attrs)
            if connection_secured_attr:
                host_conf.connectionSecured = True if connection_secured_attr.Value.lower() == "true" else False
            else:
                host_conf.connectionSecured = False

            # SCRIPT PARAMS
            script_params_attr = get_resource_attribute_gen_agostic(SCRIPT_PARAMS_PARAM, attrs)
            if script_params_attr:
                if script_params_attr.Value:
                    host_conf.parameters = get_params_list_from_semicolon_sep_str(script_params_attr.Value)
                else:
                    host_conf.parameters = default_script_params
            else:
                host_conf.parameters = default_script_params

            ansi_conf.hostsDetails.append(host_conf)

        ansi_conf_json = ansi_conf.get_pretty_json()

        # hide repo password in json printout
        new_obj = json.loads(ansi_conf_json)
        curr_password = new_obj["repositoryDetails"]["password"]
        if curr_password:
            new_obj["repositoryDetails"]["password"] = "*******"
        json_copy = json.dumps(new_obj, indent=4)
        reporter.debug_out("=== Ansible Configuration JSON ===\n{}".format(json_copy), log_only=True)

        return ansi_conf_json

    @staticmethod
    def _get_sandbox_reporter(context, api):
        """
        helper method to get sandbox reporter instance
        :param ResourceCommandContext context:
        :param CloudShellAPISession api:
        :return:
        """
        res_id = context.reservation.reservation_id
        model = context.resource.model
        service_name = context.resource.name
        logger = get_qs_logger(log_group=res_id, log_category=model, log_file_prefix=service_name)
        reporter = SandboxReporter(api, res_id, logger)
        return reporter

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass