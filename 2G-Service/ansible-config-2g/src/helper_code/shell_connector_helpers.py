"""
when handling reservation Connector type
warning: Connector in shell driver_context is a different Class
"""

from cloudshell.shell.core.driver_context import Connector


def get_connector_endpoints(resource_name, resource_connectors):
    """
    get back a list of connector endpoints
    :param resource_name:
    :param list[Connector] resource_connectors:
    :return list[str]:
    """
    connector_endpoints = []
    for connector in resource_connectors:
        if connector.source not in resource_name:
            connector_endpoints.append(connector.source)
        else:
            connector_endpoints.append(connector.target)
    return connector_endpoints


