# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
import os
import ast
from os import path
from georeference.settings import DIRECTORY_TYPE_MAPPING
from georeference.settings import DBCONFIG_PARAMS
from georeference.settings import ELASTICSEARCH_INDEX
from georeference.settings import GEOREFERENCE_PERSITENT_TARGETDIR
from georeference.settings import GEOREFERENCE_PERSITENT_TMS
from georeference.settings import GEOREFERENCE_PERSITENT_VRT
from georeference.settings import OAI_ID_PATTERN
from georeference.settings import TMP_DIR
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata
from georeference.utils.parser.georeferenceparser import parseGcps
from georeference.utils.parser.georeferenceparser import parseClipPolygon
from georeference.utils.process.georeferencer import addOverviews
from georeference.utils.process.georeferencer import rectifyImageAffine
from georeference.utils.process.georeferencer import rectifyTps
from georeference.utils.process.georeferencer import rectifyPolynom
from georeference.utils.process.tools import stripSRIDFromEPSG
from georeference.scripts.updatetms import buildTMSCache
from georeference.scripts.updatevrt import updateVirtualdatasetForTimestamp
from georeference.persitent.elastic.datamodel import createSearchRecord
from georeference.persitent.elastic.elasticsearch import pushRecordToEs
from georeference.persitent.elastic.elasticsearch import deleteRecordFromEsById

# from georeference.binding.wms import pushMapObjToWmsDatabaseIndex

def processGeorefImage(mapObj, georefObj, logger):
    """ Function process a persistent georeference image

    :type georeference.models.vkdb.map.Map: mapObj
    :type georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess: georefObj
    :type logging.Logger: logger
    :return: str """
    clipParams = parseClipPolygon(georefObj.clippolygon['polygon'])
    gcps = parseGcps(georefObj.georefparams['gcps'])
    georefTargetSRS = stripSRIDFromEPSG(georefObj.georefparams['target'])
    targetPath = os.path.join(GEOREFERENCE_PERSITENT_TARGETDIR, mapObj.apsdateiname+'.tif')
    transformationAlgorithm = georefObj.georefparams['algorithm'] if 'algorithm' in georefObj.georefparams else 'affine'
    destPath = None

    logger.debug('Process georeference result ...')
    if transformationAlgorithm == 'affine':
        destPath = rectifyImageAffine(mapObj.originalimage, targetPath, clipParams, gcps, georefTargetSRS, logger)
    elif transformationAlgorithm == 'polynom':
        destPath = rectifyPolynom(mapObj.originalimage, targetPath, clipParams, gcps, georefTargetSRS, logger, TMP_DIR)
    elif transformationAlgorithm == 'tps':
        destPath = rectifyTps(mapObj.originalimage, targetPath, clipParams, gcps, georefTargetSRS, logger, TMP_DIR)

    logger.debug('Add overviews to the image ...')
    addOverviews(destPath, '2 4 8 16 32', logger)

    return destPath

def pushRecordToSearchIndex(mapObj, dbsession, logger, georefObj=None):
    """ Push the metadata for a given mapObj to the search index (actual ElasticSearch).
    
    :type georeference.models.vkdb.map.Map: mapObj
    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :type georefObj: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess|None
    :return: str RecordId of the ElasticSearch record
    """
    datarecord = createSearchRecord(mapObj, dbsession, logger, georefObj)
    return pushRecordToEs(datarecord, ELASTICSEARCH_INDEX, logger)

def removeRecordFromSearchIndex(mapObj):
    """ Removes the equivalent record from the search index. Instead georeference is set to false

    :deprecated:
    :type georeference.models.vkdb.map.Map: mapObj
    :return:
    """
    key = OAI_ID_PATTERN%mapObj.id
    deleteRecordFromEsById(key, ELASTICSEARCH_INDEX)
    
def updateMappingServices(mapObj, destPath, dbsession, logger):
    """ Function process a TMS cache for a georeference image and if it is messtischblatt also updates the vrts

    :type georeference.models.vkdb.map.Map: mapObj
    :type str: destPath
    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :return: str """
    logger.info('Calculating tms cache and vrt...')
    # get correct path
    subDirectory = DIRECTORY_TYPE_MAPPING[mapObj.maptype]
    newTargetDirectory = path.join(GEOREFERENCE_PERSITENT_TMS, subDirectory)
    buildTMSCache(destPath, newTargetDirectory, logger, mapObj.getSRID(dbsession))

    if mapObj.maptype == "M":
        metadata = Metadata.by_id(mapObj.id, dbsession)
        updateVirtualdatasetForTimestamp('%s-01-01 00:00:00'%metadata.timepublish.year, GEOREFERENCE_PERSITENT_VRT, TMP_DIR, DBCONFIG_PARAMS, dbsession, logger)