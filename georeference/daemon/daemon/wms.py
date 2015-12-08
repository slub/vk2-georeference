# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
from georeference.settings import GEOREFERENCE_PERSITENT_WMS_LAYERID
from georeference.models.vkdb.refmaplayer import RefMapLayer

def pushMapObjToWmsDatabaseIndex(mapObj, dbsession):
    """ Function adds a record to an wms database index.

    :type mapObj: vkviewer.python.models.vkdb.Map
    :type dbsession: sqlalchemy.orm.session.Session """
    # actual there is only a database index used for
    if mapObj.maptype == 'M' and mapObj.isttransformiert == True:
        layerid = GEOREFERENCE_PERSITENT_WMS_LAYERID[mapObj.maptype]
        refmapslayer = RefMapLayer.by_id(layerid, mapObj.id, dbsession)
        if not refmapslayer:
            refmapslayer = RefMapLayer(layerid=layerid, mapid=mapObj.id)
            dbsession.add(refmapslayer)

def removeMapObjFromWmsDatabaseIndex(mapObj, dbsession):
    """ Function removes a map object from a wms database record

    :type mapObj: vkviewer.python.models.vkdb.Map
    :type dbsession: sqlalchemy.orm.session.Session """
    # actual there is only a database index used for
    refmaplayer = RefMapLayer.by_id(GEOREFERENCE_PERSITENT_WMS_LAYERID[mapObj.maptype], mapObj.id, dbsession)
    if refmaplayer:
        dbsession.delete(refmaplayer)