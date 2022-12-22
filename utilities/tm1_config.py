import os
from configparser import ConfigParser
from getpass import getpass

import keyring
from keyring.backends import Windows

from base import application_path

keyring.set_keyring(Windows.WinVaultKeyring())
FILE = os.path.join(application_path, 'config.ini')


def str_to_bool(entry: str) -> bool:
    if entry.lower() in ['y', 't', 'true', 'yes', '1']:
        return True
    else:
        return False


def get_tm1_config(instance: str) -> dict:
    config = ConfigParser()
    config.read(FILE)
    if not config.has_section(instance):
        _config = create_section(instance=instance, config=config)
    else:
        address = config[instance]['address']
        port = config[instance]['port']
        ssl = config[instance]['ssl']
        gateway = config[instance]['gateway']
        namespace = config[instance]['namespace']
        user = config[instance]['user']
        password = keyring.get_password(instance, user)
        if not password:
            password = getpass(f"Enter password for '{user}': ")
        keyring.set_password(instance, user, password)
        _config = {
            'address': address,
            'port': port,
            'ssl': ssl,
            'gateway': gateway,
            'namespace': namespace,
            'user': user,
            'password': password,
            'session_context': 'ACG-ThreadManager'
        }
        return _config


def create_section(instance: str, config: ConfigParser) -> dict:
    while True:
        address = input(f"Enter address for {instance}")
        if not address:
            print("Address is a required field")
            continue
        else:
            break
    while True:
        port = input(f"Enter HTTPPortNumber from tm1s.cfg): ")
        if not port:
            print("Port is a required field")
            continue
        else:
            break
    ssl = str_to_bool(input(f"Does '{instance}' use ssl (default False): "))
    namespace = input(f"Enter CAM Namespace (leave empty if no CAM Security): ")
    if not namespace:
        namespace = None
    gateway = input("Enter Gateway URI (leave empty if no SSO): ")
    if not gateway:
        gateway = None
    while True:
        user = input(f"Enter username for '{instance}': ")
        if not user:
            print("Username is a required field")
            continue
        else:
            break
    _blank_password = str_to_bool(input(f"Does '{user}' have a blank password (default False): "))
    if _blank_password:
        password = None
    else:
        while True:
            password = getpass(f"Enter password for '{user}': ")
            if not password:
                print("Password is a required field")
                continue
            else:
                keyring.set_password(instance, user, password)
                break
    _config = {
        'address': address,
        'port': port,
        'ssl': ssl,
        'gateway': gateway,
        'namespace': namespace,
        'user': user,
        'session_context': 'ACG-ThreadManager'
    }
    config[instance] = _config
    config.write(open(FILE, 'w'))
    _config['password'] = password
    return _config
