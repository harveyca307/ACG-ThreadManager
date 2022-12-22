"""
Usage:
    ACG-ThreadManager <instance> --list
    ACG-ThreadManager <instance> --kill <ID>
    ACG-ThreadManager (-h | --version)

Positional Arguments:
    <instance>      Config.ini instance name

Options:
    --list          List running threads
    --kill <ID>     ID of thread to kill
    -h              Show this screen
    --version       Show version information
"""
import logging
import os
import sys
import time

import TM1py.Exceptions
from TM1py import TM1Service
from docopt import docopt

from base import application_path
from utilities import get_tm1_config

APP_NAME = 'ACG-ThreadManager'
APP_VERSION = '1.0'
LOG_FILE = APP_NAME + '.log'


def configure_logging() -> None:
    global LOG_FILE
    LOG_FILE = os.path.join(application_path, LOG_FILE)
    logging.basicConfig(
        filename=LOG_FILE,
        format="%(asctime)s - " + APP_VERSION + " - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # Also log to stdout
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def main(instance: str, **kwargs) -> None:
    config = get_tm1_config(instance=instance)
    if kwargs['--list']:
        try:
            with TM1Service(**config) as tm1:
                threads = tm1.monitoring.get_threads()
                for thread in threads:
                    if thread['Context'] != APP_NAME:
                        print(thread)
        except TM1py.Exceptions.TM1pyNotAdminException:
            logging.error("User not admin")
        except TM1py.Exceptions.TM1pyException as e:
            logging.error(e)
    else:
        try:
            with TM1Service(**config) as tm1:
                threads = tm1.monitoring.get_threads()
                for thread in threads:
                    if int(thread['ID']) == int(kwargs['--kill']):
                        tm1.monitoring.cancel_thread(kwargs['--kill'])
                        logging.info(f"Thread {kwargs['--kill']} killed")
        except TM1py.Exceptions.TM1pyNotAdminException:
            logging.error("User not admin")
        except TM1py.Exceptions.TM1pyException as e:
            logging.error(e)


if __name__ == '__main__':
    start = time.perf_counter()
    configure_logging()
    logging.info("Starting process")
    cmd_args = docopt(__doc__, version=f"{APP_NAME}, Version: {APP_VERSION}")
    _instance = cmd_args.get("<instance>")
    main(instance=_instance, **cmd_args)
    end = time.perf_counter()
    logging.info(f"Finished in {round(end - start, 2)} seconds")
