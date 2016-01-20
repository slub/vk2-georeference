# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
from georeference.models.vkdb.refmaplayer import RefMapLayer

def pushMapObjToWmsDatabaseIndex(mapObj, layerId, dbsession):
    """ Function adds a record to an wms database index.

    :type georeference.models.vkdb.map.Map: mapObj
    :type int: layerId
    :type sqlalchemy.orm.session.Session: dbsession """
    if mapObj.isttransformiert == True:
        refmapslayer = RefMapLayer.by_id(layerId, mapObj.id, dbsession)
        if not refmapslayer:
            refmapslayer = RefMapLayer(layerid=layerId, mapid=mapObj.id)
            dbsession.add(refmapslayer)

def removeMapObjFromWmsDatabaseIndex(mapObj, layerId, dbsession):
    """ Function removes a map object from a wms database record

    :type georeference.models.vkdb.map.Map: mapObj
    :type int: layerId
    :type sqlalchemy.orm.session.Session: dbsession """
    # actual there is only a database index used for
    refmaplayer = RefMapLayer.by_id(layerId, mapObj.id, dbsession)
    if refmaplayer:
        dbsession.delete(refmaplayer)