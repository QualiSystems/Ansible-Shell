import re
import socket
from io import StringIO
from abc import ABCMeta, abstractmethod
from multiprocessing.pool import ThreadPool
from uuid import uuid4

import time

import requests
import winrm
from paramiko.ssh_exception import NoValidConnectionsError
from winrm.exceptions import WinRMTransportError

from paramiko import SSHClient, AutoAddPolicy, RSAKey


class IVMConnectionService(object, metaclass=ABCMeta):
    @abstractmethod
    def check_connection(self, target_host, logger, ansible_port):
        pass


class ExcutorConnectionError(EnvironmentError):
    def __init__(self, error_code, inner_error):
        self.errno = error_code
        self.inner_error = inner_error


class WindowsConnectionService(IVMConnectionService):
    def check_connection(self, target_host, logger, ansible_port):

        ip = target_host.ip + ":" + ansible_port if ansible_port else target_host.ip
        logger.info("Session IP: " + ip)

        logger.info("Creating a session.")
        if target_host.connection_secured:
            logger.info("session connection_secured=True")
            session = winrm.Session(ip, auth=(target_host.username, target_host.password), transport='ssl')
        else:
            logger.info("session connection_secured=False")
            session = winrm.Session(ip, auth=(target_host.username, target_host.password))

        logger.info("Session created.")

        try:
            logger.info("test connection")
            uid = str(uuid4())
            result = session.run_cmd('@echo ' + uid)
            assert uid in result.std_out
        except requests.ConnectionError as e:
            match = re.search(r'\[Errno (?P<errno>\d+)\]', str(e.message))
            error_code = int(match.group('errno')) if match else 0
            raise ExcutorConnectionError(error_code, e)
        except WinRMTransportError as e:
            match = re.search(r'Code (?P<errno>\d+)', str(e.message))
            error_code = int(match.group('errno')) if match else 0
            raise ExcutorConnectionError(error_code, e)
        except Exception as e:
            raise ExcutorConnectionError(0, e)


class LinuxConnectionService(IVMConnectionService):
    def check_connection(self, target_host, logger, ansible_port):
        """

        :param target_host:
        :param logger Logger:
        :return:
        """
        try:
            logger.info("Creating a session.")

            session = SSHClient()
            session.set_missing_host_key_policy(AutoAddPolicy())
            logger.info("Test connection")
            if target_host.password:
                session.connect(target_host.ip, port=ansible_port, username=target_host.username,
                                password=target_host.password)
            elif target_host.access_key:
                key_stream = StringIO(target_host.access_key)
                key_obj = RSAKey.from_private_key(key_stream)
                session.connect(target_host.ip, port=ansible_port, username=target_host.username, pkey=key_obj)
            else:
                raise Exception('Both password and access key are empty.')
            logger.info("Done testing connection")
        except NoValidConnectionsError as e:
            error_code = next(iter(e.errors.values()), type('e', (object,), {'errno': 0})).errno
            raise ExcutorConnectionError(error_code, e)
        except socket.error as e:
            raise ExcutorConnectionError(e.errno, e)
        except Exception as e:
            raise ExcutorConnectionError(0, e)


class ConnectionService(object):
    def __init__(self):
        self.valid_errnos = [10060, 10061, 10064, 10065, 500, 113, 111, 110]
        self.linuxConnectionService = LinuxConnectionService()
        self.windowsConnectionService = WindowsConnectionService()

    def check_connection(self, logger, target_host, ansible_port=None, timeout_minutes=10):
        """

        :param timeout_minutes:
        :param ansible_port:
        :param Logger logger:
        :param cloudshell.cm.ansible.domain.ansible_configuration.HostConfiguration target_host:
        :return:
        """
        # 10060  ETIMEDOUT                      Operation timed out
        # 10061  ECONNREFUSED                   Connection refused (happense when host found, port not)
        # 10064  EHOSTDOWN                      Host is down
        # 10065  EHOSTUNREACH                   Host is unreachable
        # 500                                   Bad http response (winrm)
        # 113    EHOSTUNREACH                   No route to host (winrm - OpenStack)
        # 111    ERROR_SSH_APPLICATION_CLOSED   User on the other side of connection closed
        # application that led to disconnection
        # 110    ERROR_SSH_CONNECTION_LOST      Connection was lost by some reason
        interval_seconds = 10
        start_time = time.time()
        while True:
            try:
                logger.info("check connection")
                if target_host.connection_method == 'winrm':
                    logger.info("Check connection on windows")

                    self.windowsConnectionService.check_connection(target_host=target_host,
                                                                   logger=logger,
                                                                   ansible_port=ansible_port)

                    logger.info("Done checking connection on windows")
                else:
                    logger.info("Check connection on linux")
                    self.linuxConnectionService.check_connection(target_host=target_host,
                                                                 logger=logger,
                                                                 ansible_port=int(ansible_port))
                    logger.info("Done checking connection on linux")
                break
            except ExcutorConnectionError as e:
                if e.errno not in self.valid_errnos:
                    raise e.inner_error
                if time.time() - start_time >= timeout_minutes * 60:
                    raise e.inner_error
                time.sleep(interval_seconds)
