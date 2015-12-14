# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata
from georeference.utils.exceptions import ProcessIsInvalideException

def checkIfPendingProcessesExist(mapObj, request):
    """ Checks if there are process in the database which are not yet processed and
        through this race condition exists.

        :type mapObj: vkviewer.python.models.vkdb.Map
        :type request: pyramid.request
        :return: bool """
    thereArePendingProcesses = False
    try:
        if Georeferenzierungsprozess.arePendingProcessForMapId(mapObj.id, request.db):
            thereArePendingProcesses =  True
    except ProcessIsInvalideException as e:
        # This exception catch the case that are right now no process process registered
        # in the database for the given mapObj id
        pass
    return thereArePendingProcesses

def getGeneralMetadata(mapObj, request):
    """ Query the general metadata for a process response.

    :type mapObj: vkviewer.python.models.vkdb.Map
    :type request: pyramid.request
    :return: dict """
    metadataObj = Metadata.by_id(mapObj.id, request.db)
    return {
        'objectid': mapObj.id,
        'maptype': mapObj.maptype,
        'zoomify': metadataObj.imagezoomify,
        'metadata': {
            'dateiname': mapObj.apsdateiname,
            'title_long': metadataObj.title,
            'title_short': metadataObj.titleshort
        }
    }

def getSpecificGeoreferenceData(georefProcessObj, mapObj, srid,  dbsession):
    """ Query the specific process information for a process response.

    :type mapObj: vkviewer.python.models.vkdb.Georeferenzierungsprozess
    :type mapObj: georeference.models.vkdb.map.Map
    :type srid: str
    :type sqlalchemy.orm.session.Session: dbsession
    :return: dict """
    params = {
        'extent': mapObj.getExtent(dbsession, srid),
        'georeference': georefProcessObj.georefparams,
        'timestamp': str(georefProcessObj.timestamp),
        'type': 'update',
        'georeferenceid': georefProcessObj.id
    }
    if len(georefProcessObj.clippolygon['polygon']) == 0:
        return params
    else:
        params['clip'] = georefProcessObj.clippolygon
        return params

