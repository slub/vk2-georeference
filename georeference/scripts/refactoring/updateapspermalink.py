# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 02.10.15

@author: mendt
@description:
    The following scripts updates the database path for all map files.
'''
from os import path
from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata

APS_PERMALINK_PATH = 'http://www.deutschefotothek.de/list/freitext/'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    metadata = Metadata.all(dbsession)

    for metadataObj in metadata:
        if metadataObj.ppn == 'PPN-Sammelaufnahme':
            mapObj = Map.by_id(metadataObj.mapid, dbsession)
            metadataObj.apspermalink = APS_PERMALINK_PATH + mapObj.apsdateiname
    dbsession.commit()