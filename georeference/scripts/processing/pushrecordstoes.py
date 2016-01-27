# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 02.10.15

@author: mendt
@description:
    The following scripts pushs all database records to elasticsearch
'''
import logging
from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.persistent.jobs.genericjobs import pushRecordToSearchIndex
from georeference.persistent.jobs.genericjobs import removeRecordFromSearchIndex

if __name__ == '__main__':
    logging.basicConfig()
    logger = logging.getLogger('Push recrords to ES')
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS), False)
    maps = Map.all(dbsession)

    for mapObj in maps:
        if mapObj.istaktiv == True:
            print 'Push map record %s to elastic search ...' % mapObj.id
            georefObj = Georeferenzierungsprozess.getActualGeoreferenceProcessForMapId(mapObj.id, dbsession)
            pushRecordToSearchIndex(mapObj, dbsession, logger, georefObj)
        else:
            print 'Remove map record %s from elastic search ...' % mapObj.id
            removeRecordFromSearchIndex(mapObj)