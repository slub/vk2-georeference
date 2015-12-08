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
from georeference.settings import DIRECTORY_TYPE_MAPPING
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map

DATA_DIRECTORY = '/srv/vk/data/original'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    maps = Map.all(dbsession)

    for map in maps:
        # extract the filename of the image
        fileName = map.originalimage[map.originalimage.rfind('/') + 1:]
        subDirectory = DIRECTORY_TYPE_MAPPING[map.maptype]
        newOriginalImagePath = path.join(
            path.join(DATA_DIRECTORY, subDirectory),
            fileName)
        if not path.exists(newOriginalImagePath):
            print "%s"%newOriginalImagePath
        else:
            print 'Update path'
            map.originalimage = newOriginalImagePath

    dbsession.commit()