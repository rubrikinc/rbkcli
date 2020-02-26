"""
Local System Info.

Gathers basic information about:
- Operational System (type, version);
- Python environment (version and packages);
- Network connectivity (is it connected to the internet);
"""

from collections import OrderedDict
import json
import os
import pkg_resources
import platform
import socket
import sys


REMOTE_SERVER = "www.pypi.org"


def get_os_version():
    return {
        'name': str(os.name),
        'system': str(platform.system()),
        'release': str(platform.release())
    }


def get_python_info():
    dists = [str(d).replace(" ","==") for d in pkg_resources.working_set]
    return {
        'version': sys.version,
        'packages': dists
    }


def is_connected(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    s.close()
    return True
  except:
     pass
  return False


def main():
    # Generate resulting json in specific order.
    environment_data = OrderedDict()
    environment_data['os_info'] =  get_os_version()
    environment_data['python_info'] = get_python_info()
    environment_data['is_pypi_reachable'] = is_connected(REMOTE_SERVER)

    print(json.dumps(environment_data, indent=2))
    

if __name__ == '__main__':
    main()
