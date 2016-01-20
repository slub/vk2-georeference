# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 18.01.16

@author: mendt
'''
import os
import shutil
from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map


DATA_DIRECTORY_ORGINAL = '/srv/vk/data/original'
DATA_DIRECTORY_GEOREF = '/srv/vk/data/georef'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    mapObjs = Map.all(dbsession)
    imageDoesNotExist = []
    oldPaths = []

    for mapObj in mapObjs:
        print 'Update data dirs for %s ...' % mapObj.originalimage

        # update orginal paths
        newPath = os.path.join(DATA_DIRECTORY_ORGINAL, os.path.join(str(mapObj.maptype).lower(), str(mapObj.originalimage).split('/')[-1]))
        if not os.path.exists(newPath):
            # check if path exist in old folder and if yes move the file
            oldPath = os.path.join(DATA_DIRECTORY_ORGINAL, os.path.join('mtb', str(mapObj.originalimage).split('/')[-1]))
            if os.path.exists(oldPath):
                oldPaths.append(oldPath)
                print 'Move file from %s to %s ...' % (oldPath, newPath)
                print 'Copy file ...'
                shutil.copy(oldPath, newPath)
                print 'Remove old file ...'
                os.remove(oldPath)
            else:
                imageDoesNotExist.append(newPath)

        # update path in database
        if newPath != mapObj.originalimage:
            mapObj.originalimage = newPath

        # update georef images
        if mapObj.georefimage != '':
            print 'Update georef images ...'
            newPath = os.path.join(DATA_DIRECTORY_GEOREF, os.path.join(str(mapObj.maptype).lower(), '%s.tif' % mapObj.apsdateiname))
            print 'Copy: %s to %s ' % (mapObj.georefimage, newPath)
            if not os.path.exists(newPath):
                shutil.copy(mapObj.georefimage, newPath)
            print 'Update database reference'
            mapObj.georefimage = newPath


    for path in imageDoesNotExist:
        print('Image %s does not exist' % path)

    print 'Moved %s files ...' % len(oldPaths)

    print 'Finish updating.'

    dbsession.commit()