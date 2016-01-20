# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 18.01.16

@author: mendt

The following scripts calculates for all mapObj in the database which are georeferenced an
Tile Map Service.

'''
import os
import logging
from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map
from georeference.scripts.updatetms import buildTMSCache

DATA_DIRECTORY_TMS = '/srv/vk/data/tms'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    mapObjs = Map.all(dbsession)
    logging.basicConfig()
    logger = logging.getLogger('TMS')

    print 'Calculate complete new tms cache ...'

    for mapObj in mapObjs:
        if mapObj.isttransformiert:
            tmsCachePath = os.path.join(DATA_DIRECTORY_TMS, str(mapObj.maptype).lower())
            buildTMSCache(mapObj.georefimage, tmsCachePath, logger, mapObj.getSRID(dbsession))

    print 'Finish updating.'