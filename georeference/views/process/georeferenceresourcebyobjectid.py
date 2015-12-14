# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import traceback
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError

from georeference import LOGGER
from georeference.settings import ADMIN_ADDR
from georeference.settings import OAI_ID_PATTERN
from georeference.utils.exceptions import ParameterException
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.utils.views.georeferenceresource import getGeneralMetadata
from georeference.utils.views.georeferenceresource import getSpecificGeoreferenceData
from georeference.utils.views.georeferenceresource import checkIfPendingProcessesExist

ERROR_MSG = "Please check your request parameters or contact the administrator (%s)."%ADMIN_ADDR
 
@view_config(route_name='process_byobjectid', renderer='json')
def getByObjectId(request):
    """ The function returns the process process information for a given objectid. Supports GET/POST requests
        
        :type request: pyramid.request
        :return: dict
        :raise: HTTPBadRequest
        :raise: HTTPInternalServerError """
        
    def getObjectId(request):
        """ Parse the object id from the request.
        
        :type request: pyramid.request
        :return: int """
        objectid = None
        if request.method == 'POST' and 'objectid' in request.json_body:
            objectid = request.json_body['objectid']
        if request.method == 'GET' and 'objectid' in request.params:
            objectid = request.params['objectid']
            
        if objectid is None:
            return None
        else:
            namespace, id = objectid.rsplit('-', 1)
            
            # check if it is the correct namespace
            if namespace == OAI_ID_PATTERN.rsplit('-', 1)[0]:
                return int(id)
        return None
    
    try:
        objectid = getObjectId(request)
        if objectid is None:
            raise ParameterException("Wrong or missing objectid.")

        LOGGER.debug('Create response for objectid - %s ...'%objectid)
        return generateGeoreferenceProcessForMapObj(objectid, request, LOGGER)
    except ParameterException as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPInternalServerError(ERROR_MSG)

def generateGeoreferenceProcessForMapObj(mapObjId, request, log):
    """ Function generates a process process for a given map object id
         
        :type mapObjId: int
        :type request: pyramid.request
        :type log: logging.Logger
        :return: dict """
         
    def getMtbGLSpecificGeoreferenceInformation(mapObj, request):
        """ Query the specific process base data for a messtischblatt/geological map
     
        :type mapObj: georeference.models.vkdb.map.Map
        :type request: pyramid.request
        :return: dict """
        srid = mapObj.getSRID(request.db)
        extent = mapObj.getExtent(request.db, srid)
        return { 
            'georeference': {
                'source':'pixel',
                'target':'EPSG:%s'%srid,
                'gcps': [
                    {"source":[], "target":[extent[0],extent[1]]},
                    {"source":[], "target":[extent[0],extent[3]]},
                    {"source":[], "target":[extent[2],extent[1]]},
                    {"source":[], "target":[extent[2],extent[3]]}
                ],
                'algorithm': 'affine'
            },
            'extent':extent
        }
         
    mapObj = Map.by_id(mapObjId, request.db)    
     
    # get general metadata
    log.debug('Get general process process information ...')
    generalMetadata = getGeneralMetadata(mapObj, request)
         
    # check if there exist already a activate process process for
    # this mapObj
    log.debug('Get specific process process information ...')
    if Georeferenzierungsprozess.isGeoreferenced(mapObj.id, request.db):
        # there does exist a process process for this mapObj
        georefProcessObj = Georeferenzierungsprozess.getActualGeoreferenceProcessForMapId(mapObj.id, request.db)
        georeferenceData = getSpecificGeoreferenceData(georefProcessObj, mapObj, 4326, request.db)
    else: 
        # there does not exist a process process for this mapObj
        georeferenceData = {
            "timestamp": "",
            "type": "new"
        }
         
    # log.debug('Check if there is special behavior needed in case of messtischblatt')
    mtbGeorefBaseData = {}
    if (mapObj.maptype == 'M' or mapObj.maptype == 'GL') and 'georeference' not in georeferenceData and mapObj.boundingbox is not None:
        mtbGeorefBaseData = getMtbGLSpecificGeoreferenceInformation(mapObj, request)
             
    log.debug('Check if there are pending processes in the database')
    warnMsg = {}
    if checkIfPendingProcessesExist(mapObj, request):
        warnMsg["warn"] = 'Right now another users is working on the georeferencing of this map sheet. For preventing information losses please try again in 15 minutes.'
         
    # now merge dictionaries and create response
    response = {
        "recommendedsrid": mapObj.recommendedsrid
    }
    response.update(generalMetadata)
    response.update(georeferenceData)
    response.update(mtbGeorefBaseData)
    response.update(warnMsg)
    return response