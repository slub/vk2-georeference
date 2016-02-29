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
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess

DATA_DIRECTORY_ORGINAL = '/srv/vk/data/original'
DATA_DIRECTORY_GEOREF = '/srv/vk/data/georef'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    georefObjs = Georeferenzierungsprozess.all(dbsession)

    for georefObj in georefObjs:
        if ' ' in georefObj.nutzerid:
            georefObj.nutzerid = str(georefObj.nutzerid).replace(' ', '')
            print georefObj.nutzerid
    dbsession.commit()