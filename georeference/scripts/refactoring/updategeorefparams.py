# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 02.10.15

@author: mendt
@description:
    The following scripts updates the database path for all map files.
'''
import ast
from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess

DATA_DIRECTORY = '/srv/vk/data/original'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    georefObjs = Georeferenzierungsprozess.all(dbsession)

    for georefObj in georefObjs:
        clipparams = ast.literal_eval(georefObj.clipparameter)
        if georefObj.type == 'update' and 'new' in clipparams:
            newParams = clipparams['new']
            georefObj.clipparameter = str(newParams)
            georefObj.georefparams = newParams
            print "Update georeference process with id %s"%georefObj.id

    dbsession.commit()