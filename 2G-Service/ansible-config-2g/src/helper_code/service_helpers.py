from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.cloudshell_api import ServiceInstance


def _get_target_service_attr_obj(service_instance, target_attr_name):
    """
    get attribute object, includes validation for 2nd gen shell namespace
    :param ServiceInstance service_instance:
    :param str target_attr_name: the name of target attribute. Do not include the prefixed-namespace
    :return ServiceAttribute:
    """
    # Attribute names with 2nd gen name space (using ServiceName)
    target_namespaced_attr = "{service_name}.{attr}".format(service_name=service_instance.ServiceName,
                                                            attr=target_attr_name)

    # check against all possibilities
    target_service_attr_filter = [attr for attr in service_instance.Attributes if attr.Name == target_attr_name
                                  or attr.Name == target_namespaced_attr]
    if target_service_attr_filter:
        return target_service_attr_filter[0]
    else:
        raise AttributeError("'{}' has no attribute '{}'".format(service_instance, target_attr_name))


def get_service_attr_val(service_instance, target_attr_name):
    """
    Get value of attribute if it exists
    :param ServiceInstance service_instance:
    :param str target_attr_name:
    :return:
    """
    target_attr_obj = _get_target_service_attr_obj(service_instance, target_attr_name)
    if target_attr_obj:
        return target_attr_obj.Value
    else:
        raise AttributeError("'{}' attribute does not exist on {}".format(target_attr_name, service_instance.Alias))


def is_service_attr_existing(service_instance, target_attr_name):
    """
    Check if attribute exists and returns a boolean
    :param ServiceInstance service_instance:
    :param str target_attr_name:
    :return:
    """
    try:
        _get_target_service_attr_obj(service_instance, target_attr_name)
    except AttributeError:
        return False
    return True


def is_service_attr_populated(service_instance, target_attr_name):
    """
    Check if attribute exists and returns a boolean
    :param ServiceInstance service_instance:
    :param str target_attr_name:
    :return:
    """
    try:
        target_attr_obj = _get_target_service_attr_obj(service_instance, target_attr_name)
    except AttributeError:
        return False
    value = target_attr_obj.Value
    if value:
        return True
    else:
        return False


def is_boolean_attr_true(service_instance, target_attr_name):
    """
    get a python boolean from a boolean service attribute
    :param ServiceInstance service_instance:
    :param str target_attr_name:
    :return:
    """
    try:
        target_attr_obj = _get_target_service_attr_obj(service_instance, target_attr_name)
    except AttributeError:
        return False

    if target_attr_obj.Value == "True":
        return True
    elif target_attr_obj.Value == "False":
        return False
    else:
        raise Exception("'{}' attribute on {} is not a boolean".format(target_attr_name, service_instance.Alias))


def get_service_instances(api, reservation_id):
    """
    Get the service instances
    :param CloudShellAPISession api:
    :param str reservation_id:
    :return:
    """
    service_instances = api.GetReservationDetails(reservation_id).ReservationDescription.Services
    return service_instances


def get_services_matching_bool_attr(api, reservation_id, target_attr_name):
    """
    get a list of services matching the target attribute
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str target_attr_name: put the non-namespaced attribute name
    :return:
    """
    services = get_service_instances(api, reservation_id)
    filtered_services = [service for service in services
                         if is_boolean_attr_true(service_instance=service,
                                                 target_attr_name=target_attr_name)]
    return filtered_services


def get_services_with_populated_attr(api, reservation_id, target_attr_name):
    """
    get a list of services matching the target attribute
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str target_attr_name: put the non-namespaced attribute name
    :return:
    """
    services = get_service_instances(api, reservation_id)
    filtered_services = [service for service in services
                         if is_service_attr_populated(service_instance=service,
                                                      target_attr_name=target_attr_name)]
    return filtered_services
