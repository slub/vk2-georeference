# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
import os
from georeference.settings import TEST_MODE
from georeference.settings import GEOREFERENCE_PERSITENT_TMS
from georeference.persitent.jobs.genericjobs import processGeorefImage
from georeference.persitent.jobs.genericjobs import pushRecordToSearchIndex
from georeference.utils.exceptions import GeoreferenceProcessingException
from georeference.utils.process.tools import parseBoundingBoxPolygonFromFile
from georeference.utils.process.tools import parseSRIDFromFile
from georeference.scripts.updatetms import calculateCompressedTMS


def activate(georefObj, mapObj, dbsession, logger):
    """ This function activates a georeference process for a mapObj.

    :type georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess: georefObj
    :type georeference.models.vkdb.map.Map: mapObj
    :type sqlalchemy.orm.session.Session: dbSession
    :type logging.Logger: logger
    :return: string """
    logger.debug('Activate georeference process with id %s ...'%georefObj.id)

    logger.debug('Create persistent georeference result ...')
    destPath = processGeorefImage(mapObj, georefObj, dbsession, logger)

    # check if the georeferencing was run correctly
    if destPath is None:
        logger.error('Something went wrong while trying to process a georeference process.')
        raise GeoreferenceProcessingException('Something went wrong while trying to process a georeference process.')

    logger.debug('Set map as active and update boundingbox ...')
    boundingboxFromFile = parseBoundingBoxPolygonFromFile(destPath)
    sridFromFile = parseSRIDFromFile(destPath)
    mapObj.setActive(destPath)
    mapObj.setBoundingBox(boundingboxFromFile, sridFromFile, dbsession)

    # for proper working of the mapping service update all pending database changes have to be commited
    if not TEST_MODE:
        dbsession.commit()

    # update the tile map service
    logger.info('Calculating tms cache ...')
    newTargetDirectory = os.path.join(GEOREFERENCE_PERSITENT_TMS, str(mapObj.maptype).lower())
    calculateCompressedTMS(destPath, newTargetDirectory, mapObj.getSRID(dbsession))

    # push metadata record to elasticsearch index
    datarecordKey = pushRecordToSearchIndex(mapObj, dbsession, logger, georefObj)

    # push metadata to catalogue
    # this method has to be supported again
    # logger.debug('Push metadata record for map %s to cataloge service ...'%mapObj.id)
    # pushMapObjToCsw(mapObj, dbsession, logger)

    # update process
    georefObj.setActive()

    # flush session
    if TEST_MODE:
        dbsession.flush()

    return datarecordKey

def deactivate(georefObj, mapObj, dbsession, logger):
    """ This function deactivates a georeference process for a mapObj.

    :type georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess: georefObj
    :type georeference.models.vkdb.map.Map: mapObj
    :type sqlalchemy.orm.session.Session: dbSession
    :type logging.Logger: logger """
    logger.debug('Deactivate georeference process with id %s ...'%georefObj.id)

    # reset mapObj
    mapObj.setDeactive()

    # update metadata record from elasticsearch
    datarecordKey = pushRecordToSearchIndex(mapObj, dbsession, logger)

    # logger.debug('Remove metadata record from catalog instance ...')
    # removeMapObjFromCsw(mapObj, dbsession, logger)

    logger.debug('Deactivate job ...')
    georefObj.setDeactive()

    # flush session
    if TEST_MODE:
        dbsession.flush()