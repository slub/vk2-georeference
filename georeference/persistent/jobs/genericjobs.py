# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
import uuid

import os
from georeference.settings import ELASTICSEARCH_INDEX
from georeference.settings import GEOREFERENCE_PERSITENT_TARGETDIR
from georeference.settings import OAI_ID_PATTERN
from georeference.settings import TMP_DIR
from georeference.utils.parser.georeferenceparser import parseGcps
from georeference.utils.process.georeferencer import addOverviews
from georeference.utils.process.georeferencer import createClipShapefile
from georeference.utils.process.georeferencer import rectifyTps
from georeference.utils.process.georeferencer import rectifyPolynom
from georeference.utils.process.tools import convertPostgisStringToList
from georeference.utils.process.tools import stripSRIDFromEPSG
from georeference.persistent.elastic.datamodel import createSearchRecord
from georeference.persistent.elastic.elasticsearch import pushRecordToEs
from georeference.persistent.elastic.elasticsearch import deleteRecordFromEsById

def processGeorefImage(mapObj, georefObj, dbsession, logger):
    """ Function process a persistent georeference image

    :type georeference.models.vkdb.map.Map: mapObj
    :type georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess: georefObj
    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :return: str """
    gcps = parseGcps(georefObj.georefparams['gcps'])
    georefTargetSRS = stripSRIDFromEPSG(georefObj.georefparams['target'])
    targetPath = os.path.join(GEOREFERENCE_PERSITENT_TARGETDIR, os.path.join(str(mapObj.maptype).lower(), mapObj.apsdateiname+'.tif'))
    transformationAlgorithm = georefObj.georefparams['algorithm'] if 'algorithm' in georefObj.georefparams else 'affine'
    destPath = None

    # create clip shape if exists
    clipShpPath = None
    if georefObj.clip is not None:
        clipShpPath = os.path.join(TMP_DIR, '%s' % uuid.uuid4())
        clipShpPath = createClipShapefile(convertPostgisStringToList(georefObj.clip), clipShpPath, georefObj.getSRIDClip(dbsession))

    logger.debug('Process georeference result ...')
    if transformationAlgorithm == 'affine':
        destPath = rectifyPolynom(mapObj.originalimage, targetPath, [], gcps, georefTargetSRS, logger, TMP_DIR, clipShpPath, order=1)
    elif transformationAlgorithm == 'polynom':
        destPath = rectifyPolynom(mapObj.originalimage, targetPath, [], gcps, georefTargetSRS, logger, TMP_DIR, clipShpPath)
    elif transformationAlgorithm == 'tps':
        destPath = rectifyTps(mapObj.originalimage, targetPath, [], gcps, georefTargetSRS, logger, TMP_DIR, clipShpPath)

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