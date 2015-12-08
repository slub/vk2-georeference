# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import traceback
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError

from georeference import LOGGER
from georeference.settings import ADMIN_ADDR
from georeference.utils.exceptions import ParameterException
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.utils.exceptions import ProcessIsInvalideException
from georeference.utils.views.georeferenceresource import getGeneralMetadata
from georeference.utils.views.georeferenceresource import getSpecificGeoreferenceData
from georeference.utils.views.georeferenceresource import checkIfPendingProcessesExist

ERROR_MSG = "Please check your request parameters or contact the administrator (%s)."%ADMIN_ADDR
 
@view_config(route_name='process_bygeoreferenceid', renderer='json')
def getGeoreferenceResource(request):
    """ The function returns the process process information for a given objectid. Supports GET/POST requests
         
        :type request: pyramid.request
        :return: dict
        :raise: HTTPBadRequest
        :raise: HTTPInternalServerError """
         
    def getGeoreferenceId(request):
        """ Parse the process id from the request.
         
        :type request: pyramid.request
        :return: int|None """
        if request.method == 'GET' and 'georeferenceid' in request.matchdict:
            return int(request.matchdict['georeferenceid'])
        return None
     
    try:
        georeferenceid = getGeoreferenceId(request) 
        if georeferenceid is None:
            raise ParameterException("Wrong or missing georeferenceid.")
 
        LOGGER.debug('Create response for georeferenceid - %s ...'%georeferenceid)
        return generateGeoreferenceProcessForSpecificGeoreferenceId(georeferenceid, request, LOGGER)
    except ParameterException as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPBadRequest(ERROR_MSG) 
    except ProcessIsInvalideException as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPBadRequest('This process process is blocked for further work!')
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPInternalServerError(ERROR_MSG)

def generateGeoreferenceProcessForSpecificGeoreferenceId(georeferenceId, request, log):
    """ Function generates a process process for a given map object id
        
        :type georeferenceId: int
        :type request: pyramid.request
        :type log: logging.Logger
        :return: dict """
        
    georefProcessObj = Georeferenzierungsprozess.by_id(georeferenceId, request.db)
    mapObj = Map.by_id(georefProcessObj.mapid, request.db)    
    
    # get general metadata
    log.debug('Get general process process information ...')
    generalMetadata = getGeneralMetadata(mapObj, request)
        
    # check if there exist already a activate process process for
    # this mapObj
    log.debug('Get specific process process information ...')
    georeferenceData = getSpecificGeoreferenceData(georefProcessObj, mapObj, 4326, request.db)

    log.debug('Check if there are pending processes in the database')
    warnMsg = {}
    if checkIfPendingProcessesExist(mapObj, request):
        warnMsg["warn"] = 'Right now another users is working on the georeferencing of this map sheet. For preventing information losses please try again in 15 minutes.'
        
    # now merge dictionaries and create response
    response = {}
    response.update(generalMetadata)
    response.update(georeferenceData)
    response.update(warnMsg)
    return response