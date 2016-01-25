# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
import logging
from georeference.settings import DBCONFIG_PARAMS
from georeference.settings import TEST_MODE
from georeference.models.meta import initializeDb
from georeference.models.meta import getPostgresEngineString
from georeference.models.vkdb.adminjobs import AdminJobs
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.utils.logger import createLogger
from georeference.persistent.jobs.basicjobs import setIsValide
from georeference.persistent.jobs.basicjobs import setInValide
from georeference.persistent.jobs.georeferencejobs import activate
from georeference.persistent.jobs.georeferencejobs import deactivate

def updateDataBasis(dbsession, logger, testing = False):
    """
    Updates the data basis.

    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :type bool: testing If set to True all database changes will be reset
    :return:
    """
    runningNewJobs(dbsession, logger)
    runningUpdateJobs(dbsession, logger)
    runningAdminJobs(dbsession, logger)

    if not testing:
        dbsession.commit()
    else:
        dbsession.rollback()

def runningAdminJobs(dbsession, logger):
    """ Runs new admin jobs

    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    """
    logger.info('Check for admin jobs')
    jobs = AdminJobs.getUnprocessedJobs(dbsession)

    # process jobs
    for job in jobs:
        if job.setto == 'isvalide':
            setIsValide(job, dbsession, logger)
            job.processed = True
        elif job.setto == 'invalide':
            setInValide(job, dbsession, logger)
            job.processed = True

def runningNewJobs(dbsession, logger):
    """ Runs the persistent georeference job for new georeference jobs

    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :return: int Number of processed jobs
    """
    logger.info('Check for unprocessed new georeference jobs ...')
    unprocessedJobs = Georeferenzierungsprozess.getUnprocessedObjectsOfTypeNew(dbsession)
    counter = 0
    for job in unprocessedJobs:
        logger.info('Start processing of a "new" georeference process with id - %s'%job.id)
        georefObj = Georeferenzierungsprozess.clearRaceConditions(job, dbsession)
        mapObj = Map.by_id(georefObj.mapid, dbsession)
        activate(georefObj, mapObj, dbsession, logger)

        logger.info('Finish processing of a "new" georeference process with id - %s'%job.id)
        counter += 1

    return counter

def runningUpdateJobs(dbsession, logger):
    """ Runs the persistent georeference job for update georeference jobs

    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :return: int Number of processed jobs
    """
    logger.info('Check for unprocessed update georeference jobs ...')
    unprocessedJobs = Georeferenzierungsprozess.getUnprocessedObjectsOfTypeUpdate(dbsession)
    counter = 0
    for job in unprocessedJobs:
        logger.info('Start processing of a "update" georeference process with id - %s'%job.id)
        georefObj = Georeferenzierungsprozess.clearRaceConditions(job, dbsession)

        # get active georeference process and deactive him, if exist
        activeGeorefProcess = Georeferenzierungsprozess.getActualGeoreferenceProcessForMapId(georefObj.mapid, dbsession)
        mapObj = Map.by_id(georefObj.mapid, dbsession)

        if activeGeorefProcess:
            logger.info('Deactivate georeference processes with id %s ...'%activeGeorefProcess.id)
            deactivate(activeGeorefProcess, mapObj, dbsession, logger)

        logger.info('Activate georeference processes with id %s ...'%georefObj.id)
        activate(georefObj, mapObj, dbsession, logger)

        logger.info('Finish processing of a "update" georeference process with id - %s'%job.id)
        counter += 1

    return counter

""" Main """
if __name__ == '__main__':
    logger = createLogger('test', logging.DEBUG)
    logger.info('Looking for pending georeference processes ...')
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    updateDataBasis(dbsession, logger, TEST_MODE)
    dbsession.commit()