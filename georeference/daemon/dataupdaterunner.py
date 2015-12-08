# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
import time
import os
import logging
import sys
from daemon import runner
from logging.handlers import TimedRotatingFileHandler
from georeference.settings import DBCONFIG_PARAMS
from georeference.settings import GEOREFERENCE_DAEMON_SETTINGS
from georeference.settings import GEOREFERENCE_DAEMON_LOGGER
from georeference.models.meta import initializeDb
from georeference.models.meta import getPostgresEngineString
from georeference.utils.logger import createLogger
from georeference.daemon.dataupdatejobs import updateDataBasis

# insert the module paths for correct behavior on the command line
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH_PARENT = os.path.abspath(os.path.join(BASE_PATH, os.pardir))
ROOT_PATH = os.path.abspath(os.path.join(os.path.abspath(os.path.join(BASE_PATH_PARENT, os.pardir)), os.pardir))
sys.path.insert(0, BASE_PATH)
sys.path.append(BASE_PATH_PARENT)
sys.path.append(ROOT_PATH)


# Initialize the logger
if not os.path.exists(GEOREFERENCE_DAEMON_LOGGER['file']):
    open(GEOREFERENCE_DAEMON_LOGGER['file'], 'a').close()

formatter = logging.Formatter(GEOREFERENCE_DAEMON_LOGGER['formatter'])
handler = TimedRotatingFileHandler(GEOREFERENCE_DAEMON_LOGGER['file'], when='d', interval=1, backupCount=14)
handler.setFormatter(formatter)
LOGGER = createLogger(GEOREFERENCE_DAEMON_LOGGER['name'], GEOREFERENCE_DAEMON_LOGGER['level'], handler = handler)

class GeoreferenceDaemonApp():
    """ The GeoreferenceDaemonApp is used to run the update of the georeference
        basis in a regulary time. It could be programmed by the options parameter
        in the settings.py 
    """
        
    def __init__(self):
        self.stdin_path = GEOREFERENCE_DAEMON_SETTINGS['stdin']
        if not os.path.exists(self.stdin_path):
            open(self.stdin_path, 'a').close()

        self.stdout_path = GEOREFERENCE_DAEMON_SETTINGS['stdout']
        self.stderr_path = GEOREFERENCE_DAEMON_SETTINGS['stderr']
        self.pidfile_path = GEOREFERENCE_DAEMON_SETTINGS['pidfile_path']
        self.pidfile_timeout = GEOREFERENCE_DAEMON_SETTINGS['pidfile_timeout']

    def run(self):
        LOGGER.info('Georeference update runner daemon is started!')
        while True:
            LOGGER.info('Looking for pending georeference processes ...')
            dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS), LOGGER)
            updateDataBasis(dbsession, LOGGER, True)
            dbsession.commit()
            dbsession.close()

            LOGGER.info('Go to sleep ...')
            time.sleep(GEOREFERENCE_DAEMON_SETTINGS['sleep_time'])


# Initialize DaemonRunner
daemon_runner = runner.DaemonRunner(GeoreferenceDaemonApp())

# This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

