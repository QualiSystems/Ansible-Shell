from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict


class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class AnsibleConfig2G(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Ansible Config 2G'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype AnsibleConfig2G
        """
        result = AnsibleConfig2G(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'AnsibleConfig2G'

    @property
    def address(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Address'] if 'Ansible Config 2G.Address' in self.attributes else None

    @address.setter
    def address(self, value):
        """
        (Optional) Address of Script Repo Server
        :type value: str
        """
        self.attributes['Ansible Config 2G.Address'] = value

    @property
    def repo_user(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Repo User'] if 'Ansible Config 2G.Repo User' in self.attributes else None

    @repo_user.setter
    def repo_user(self, value):
        """
        (Optional) Source Control user for private repo authentication. Required for Github Private Repo. For Gitlab user not required, only access token in password field.
        :type value: str
        """
        self.attributes['Ansible Config 2G.Repo User'] = value

    @property
    def repo_password(self):
        """
        :rtype: string
        """
        return self.attributes['Ansible Config 2G.Repo Password'] if 'Ansible Config 2G.Repo Password' in self.attributes else None

    @repo_password.setter
    def repo_password(self, value):
        """
        (Optional) Source Control password for private repo authentication. For GitLab, add private access token here.
        :type value: string
        """
        self.attributes['Ansible Config 2G.Repo Password'] = value

    @property
    def playbook_base_path(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Playbook Base Path'] if 'Ansible Config 2G.Playbook Base Path' in self.attributes else None

    @playbook_base_path.setter
    def playbook_base_path(self, value):
        """
        Base URL to script. This path will join with script path passed to execute playbook command. (Github - https://raw.githubusercontent.com/QualiSystemsLab/App-Configuration-Demo-Scripts/master/, Gitlab - http://<SERVER_IP>/api/v4/projects/<PROJECT_ID>/repository/files)
        :type value: str
        """
        self.attributes['Ansible Config 2G.Playbook Base Path'] = value

    @property
    def playbook_script_path(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Playbook Script Path'] if 'Ansible Config 2G.Playbook Script Path' in self.attributes else None

    @playbook_script_path.setter
    def playbook_script_path(self, value):
        """
        Base URL to script. This path will join with script path passed to execute playbook command. (Github - https://raw.githubusercontent.com/QualiSystemsLab/App-Configuration-Demo-Scripts/master/, Gitlab - http://<SERVER_IP>/api/v4/projects/<PROJECT_ID>/repository/files)
        :type value: str
        """
        self.attributes['Ansible Config 2G.Playbook Script Path'] = value

    @property
    def playbook_url_full(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Playbook URL Full'] if 'Ansible Config 2G.Playbook URL Full' in self.attributes else None

    @playbook_url_full.setter
    def playbook_url_full(self, value):
        """
        Base URL to script. This path will join with script path passed to execute playbook command. (Github - https://raw.githubusercontent.com/QualiSystemsLab/App-Configuration-Demo-Scripts/master/, Gitlab - http://<SERVER_IP>/api/v4/projects/<PROJECT_ID>/repository/files)
        :type value: str
        """
        self.attributes['Ansible Config 2G.Playbook URL Full'] = value

    @property
    def connection_method(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Connection Method'] if 'Ansible Config 2G.Connection Method' in self.attributes else None

    @connection_method.setter
    def connection_method(self, value='SSH'):
        """
        For Linux / Windows connections
        :type value: str
        """
        self.attributes['Ansible Config 2G.Connection Method'] = value

    @property
    def script_parameters(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Script Parameters'] if 'Ansible Config 2G.Script Parameters' in self.attributes else None

    @script_parameters.setter
    def script_parameters(self, value):
        """
        (Optional) key pair values passed playbook VARS file to be accesible in script. Pass in following format - key1,val1;key2,val2.
        :type value: str
        """
        self.attributes['Ansible Config 2G.Script Parameters'] = value

    @property
    def inventory_groups(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Inventory Groups'] if 'Ansible Config 2G.Inventory Groups' in self.attributes else None

    @inventory_groups.setter
    def inventory_groups(self, value):
        """
        (Optional) Designating groups in playbook to be executed
        :type value: str
        """
        self.attributes['Ansible Config 2G.Inventory Groups'] = value

    @property
    def ansible_cmd_args(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Ansible CMD Args'] if 'Ansible Config 2G.Ansible CMD Args' in self.attributes else None

    @ansible_cmd_args.setter
    def ansible_cmd_args(self, value):
        """
        (Optional) Additional arguments passed to ansible-playbook command line execution.
        :type value: str
        """
        self.attributes['Ansible Config 2G.Ansible CMD Args'] = value

    @property
    def timeout_minutes(self):
        """
        :rtype: float
        """
        return self.attributes['Ansible Config 2G.Timeout Minutes'] if 'Ansible Config 2G.Timeout Minutes' in self.attributes else None

    @timeout_minutes.setter
    def timeout_minutes(self, value='10'):
        """
        (Optional) Minutes to wait while polling target hosts
        :type value: float
        """
        self.attributes['Ansible Config 2G.Timeout Minutes'] = value

    @property
    def gitlab_branch(self):
        """
        :rtype: str
        """
        return self.attributes['Ansible Config 2G.Gitlab Branch'] if 'Ansible Config 2G.Gitlab Branch' in self.attributes else None

    @gitlab_branch.setter
    def gitlab_branch(self, value='master'):
        """
        (Optional) Defaults to master branch. This attribute relevant for downloading from non-master branches in Gitlab repos.
        :type value: str
        """
        self.attributes['Ansible Config 2G.Gitlab Branch'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value



