import re
import socket
from StringIO import StringIO
from abc import ABCMeta, abstractmethod
from multiprocessing.pool import ThreadPool
from uuid import uuid4

import time
import winrm
from paramiko.ssh_exception import NoValidConnectionsError
from winrm.exceptions import WinRMTransportError

from pip._vendor.requests import ConnectionError
from paramiko import SSHClient, AutoAddPolicy, RSAKey


class IVMConnectionService(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check_connection(self, target_host):
        pass


class ExcutorConnectionError(EnvironmentError):
    def __init__(self, error_code, inner_error):
        self.errno = error_code
        self.inner_error = inner_error


class WindowsConnectionService(IVMConnectionService):
    def check_connection(self, target_host):
        session = None
        if target_host.connection_secured:
            session = winrm.Session(target_host.ip, auth=(target_host.username, target_host.password), transport='ssl')
        else:
            session = winrm.Session(target_host.ip, auth=(target_host.username, target_host.password))

        try:
            uid = str(uuid4())
            result = session.run_cmd('@echo ' + uid)
            assert uid in result.std_out
        except ConnectionError as e:
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
    def check_connection(self, target_host):
        try:
            session = SSHClient()
            session.set_missing_host_key_policy(AutoAddPolicy())

            if target_host.password:
                session.connect(target_host.ip, username=target_host.username, password=target_host.password)
            elif target_host.access_key:
                key_stream = StringIO(target_host.access_key)
                key_obj = RSAKey.from_private_key(key_stream)
                session.connect(target_host.ip, username=target_host.username, pkey=key_obj)
            else:
                raise Exception('Both password and access key are empty.')
        except NoValidConnectionsError as e:
            error_code = next(e.errors.itervalues(), type('e', (object,), {'errno': 0})).errno
            raise ExcutorConnectionError(error_code, e)
        except socket.error as e:
            raise ExcutorConnectionError(e.errno, e)
        except Exception as e:
            raise ExcutorConnectionError(0, e)


class ConnecetionService(object):
    def __init__(self):
        self.linuxConnectionService = LinuxConnectionService()
        self.windowsConnectionService=WindowsConnectionService()

    def check_connection(self, target_host,timeout_minutes=10):
        """

        :param cloudshell.cm.ansible.domain.ansible_configuration.HostConfiguration target_host:
        :return:
        """


        """
        :type executor: IScriptExecutor
        :type cancel_sampler: CancellationSampler
        """
        # 10060  ETIMEDOUT                      Operation timed out
        # 10061  ECONNREFUSED                   Connection refused (happense when host found, port not)
        # 10064  EHOSTDOWN                      Host is down
        # 10065  EHOSTUNREACH                   Host is unreachable
        # 500                                   Bad http response (winrm)
        # 113    EHOSTUNREACH                   No route to host (winrm - OpenStack)
        # 111    ERROR_SSH_APPLICATION_CLOSED   User on the other side of connection closed application that led to disconnection
        # 110    ERROR_SSH_CONNECTION_LOST      Connection was lost by some reason
        valid_errnos = [10060, 10061, 10064, 10065, 500, 113, 111, 110]
        interval_seconds = 10
        start_time = time.time()
        while True:
            # cancel_sampler.throw_if_canceled()
            try:

                if target_host.connection_method:
                    self.windowsConnectionService.check_connection(target_host)
                else:
                    self.linuxConnectionService.check_connection(target_host)
                break
            except ExcutorConnectionError as e:
                if not e.errno in valid_errnos:
                    raise e.inner_error
                if time.time() - start_time >= timeout_minutes*60:
                    raise e.inner_error
                time.sleep(interval_seconds)