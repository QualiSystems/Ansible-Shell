"""
Module for storing convenience functions that wrap up automation_api functionality
"""

from cloudshell.api.cloudshell_api import CloudShellAPISession


def get_reservation_resources(api, reservation_id):
    """
    :param CloudShellAPISession api:
    :param str reservation_id: id of current sandbox
    :return:
    """
    reservation_details = api.GetReservationDetails(reservationId=reservation_id)
    resources = reservation_details.ReservationDescription.Resources
    return resources


def get_reservation_resources_by_family(api, reservation_id, family_name):
    """
    :param CloudShellAPISession api:
    :param str reservation_id: id of current sandbox
    :param str family_name:
    :return:
    """
    resources = get_reservation_resources(api, reservation_id)
    target_resources = [resource for resource in resources
                        if resource.ResourceFamilyName == family_name]
    return target_resources


def get_reservation_resources_by_model(api, reservation_id, model_name):
    """
    :param CloudShellAPISession api:
    :param str reservation_id: id of current sandbox
    :param str model_name:
    :return:
    """
    resources = get_reservation_resources(api, reservation_id)
    target_resources = [resource for resource in resources
                        if resource.ResourceModelName == model_name]
    return target_resources


def _get_target_attr_obj(api, resource_name, target_attr_name):
    """
    get attribute object, includes validation for 2nd gen shell namespace
    :param CloudShellAPISession api:
    :param str resource_name:
    :param str target_attr_name: the name of target attribute. Do not include the prefixed-namespace
    :return attribute object or empty list:
    """
    res_details = api.GetResourceDetails(resource_name)
    res_model = res_details.ResourceModelName
    res_family = res_details.ResourceFamilyName

    # Attribute names with 2nd gen name space (using family or model)
    target_model_attr = "{model}.{attr}".format(model=res_model, attr=target_attr_name)
    target_family_attr = "{family}.{attr}".format(family=res_family, attr=target_attr_name)

    # check against all 3 possibilities
    target_res_attr_filter = [attr for attr in res_details.ResourceAttributes if attr.Name == target_attr_name
                              or attr.Name == target_model_attr
                              or attr.Name == target_family_attr]
    if target_res_attr_filter:
        return target_res_attr_filter[0]
    else:
        return None


def get_res_attr_val(api, resource_name, target_attr_name):
    """
    Get value of attribute if it exists
    :param CloudShellAPISession api:
    :param resource_name:
    :param target_attr_name:
    :return:
    """
    target_attr_obj = _get_target_attr_obj(api, resource_name, target_attr_name)
    if target_attr_obj:
        return target_attr_obj.Value
    else:
        return None


def does_attr_exist(api, resource_name, target_attr_name):
    """
    Check if attribute exists and return a boolean
    :param CloudShellAPISession api:
    :param str resource_name:
    :param str target_attr_name:
    :return:
    """
    target_attr_obj = _get_target_attr_obj(api, resource_name, target_attr_name)
    return bool(target_attr_obj)


def evaluate_boolean_attr(api, resource_name, target_attr_name):
    """
    get a python boolean from the attribute string boolean
    :param CloudShellAPISession api:
    :param str resource_name:
    :param str target_attr_name:
    :return:
    """
    target_attr_obj = _get_target_attr_obj(api, resource_name, target_attr_name)
    if target_attr_obj and target_attr_obj.Type == "Boolean":
        if target_attr_obj.Value == "True":
            return True
        else:
            return False


def get_resources_matching_bool_attr(api, reservation_id, target_attr_name):
    """
    get all sandbox resources matching your target boolean flag
    :param CloudShellAPISession api:
    :param str reservation_id:
    :param str target_attr_name:
    :return:
    """
    resources = get_reservation_resources(api, reservation_id)

    filtered_resources = [vm for vm in resources
                          if
                          evaluate_boolean_attr(api=api, resource_name=vm.Name, target_attr_name=target_attr_name)]
    return filtered_resources


def get_decrypted_res_password(api, resource_name):
    """
    get the decrypted password of a resource
    :param CloudShellAPISession api:
    :param resource_name:
    :return:
    """
    encrypted_pw = get_res_attr_val(api, resource_name, "Password")
    if encrypted_pw:
        decrypted_pw = api.DecryptPassword(encrypted_pw)
        return decrypted_pw.Value
    else:
        return None


def get_resource_credentials(api, res_name):
    """
    Get Resource User and Decrypted Password Credentials as a dict {User, Password}
    :param CloudShellAPISession api:
    :param res_name:
    :return:
    """
    user = get_res_attr_val(api=api, resource_name=res_name, target_attr_name="User")
    pw = get_decrypted_res_password(api=api, resource_name=res_name)
    return {"User": user, "Password": pw}


def offset_resources(api, res_id, resource_list, position="top_left", align="horizontal", horizontal_offset=300,
                     vertical_offset=150, x_axis=100, y_axis=50):
    """
    add resources to sandbox in different quadrants. choose stacking order
    :param CloudShellAPISession api:
    :param resource_list:
    :param align: how to stack, "horizontal" or "vertical"
    :param position: "top_left", "middle_center", "bottom_right", etc.
    :return:
    """
    # set alternate x
    if "center" in position:
        x_axis = 700
    elif "right" in position:
        x_axis = 1300

    # set alternate y
    if "middle" in position:
        y_axis = 200
    elif "bottom" in position:
        y_axis = 450

    for resource in resource_list:
        api.SetReservationResourcePosition(reservationId=res_id, resourceFullName=resource, x=x_axis, y=y_axis)
        if align == "vertical":
            if "bottom" in position:
                y_axis -= vertical_offset
            else:
                y_axis += vertical_offset
        else:
            if "right" in position:
                x_axis -= horizontal_offset
            else:
                x_axis += horizontal_offset


def get_missing_resources(api, res_id, target_resources):
    """
    compare requested resources to existing
    :param CloudShellAPISession api:
    :param res_id:
    :param target_resources:
    :return:
    """
    reservation_resources = get_reservation_resources(api, res_id)
    reservation_resource_names = [res.Name for res in reservation_resources]
    target_resource_set = set(target_resources)
    resources_to_add = target_resource_set.difference(reservation_resource_names)
    resources_to_add = list(resources_to_add)
    return resources_to_add