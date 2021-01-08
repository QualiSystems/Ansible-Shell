from cloudshell.api.cloudshell_api import ResourceAttribute


def get_resource_attribute_gen_agostic(attribute_key, resource_attributes):
    """
    :param str attribute_key:
    :param list[ResourceAttribute] resource_attributes:
    :return:
    :rtype ResourceAttribute:
    """
    for attr in resource_attributes:
        match_conditions = [attr.Name.lower() == attribute_key.lower(),
                            attr.Name.lower().endswith("." + attribute_key.lower())]
        if any(match_conditions):
            return attr
    return None