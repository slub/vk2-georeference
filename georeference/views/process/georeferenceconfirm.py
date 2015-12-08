# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import ast
import traceback
from datetime import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError

from georeference import LOGGER
from georeference.settings import ADMIN_ADDR
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.utils.exceptions import ParameterException
from georeference.utils.tools import convertUnicodeDictToUtf
from georeference.utils.tools import convertTimestampToPostgisString
from georeference.utils.parser.georeferenceparser import parseGeoreferenceParamsFromRequest

ERROR_MSG = "Please check your request parameters or contact the administrator (%s)."%ADMIN_ADDR

@view_config(route_name='georeference', renderer='json', match_param='action=confirm')
def georeferenceConfirm(request):
    """ The function persistent saves a georeference confirmation request

        :type request: pyramid.request
        :return: dict
        :raise: HTTPBadRequest
        :raise: HTTPInternalServerError """
    LOGGER.info('Receive georeference validation request with parameters: %s'%request.json_body)

    try:
        # extract validation data
        LOGGER.debug('Parse request params ...')
        requestData = parseGeoreferenceParamsFromRequest(request)

        # in case of type new,
        # check if there already exist an actual georeference process for this object with this type
        if requestData['type'] == 'new' and Georeferenzierungsprozess.isGeoreferenced(requestData['mapObj'].id, request.db):
            msg = 'There exists already an active georeference process for this map id. It is therefore not possible to save a georeference process of type "new".'
            LOGGER.debug(msg)

            georeferenceid = Georeferenzierungsprozess.getActualGeoreferenceProcessForMapId(requestData['mapObj'].id, request.db).id
            return {'text':msg,'georeferenceid':georeferenceid}

        LOGGER.debug('Save georeference parameter in datase ...')
        timestamp = convertTimestampToPostgisString(datetime.now())
        georefParam = str(convertUnicodeDictToUtf(requestData['georeference']))
        clipParam = str(convertUnicodeDictToUtf(requestData['clip']))
        overwrites = requestData['overwrites'] if 'overwrites' in requestData else 0
        georefProcess = Georeferenzierungsprozess(
            messtischblattid = requestData['mapObj'].apsobjectid,
            nutzerid = requestData['userid'],
            georefparams = ast.literal_eval(georefParam),
            clipparameter = georefParam,
            timestamp = timestamp,
            isactive = False,
            type = requestData['type'],
            overwrites = overwrites,
            clippolygon = ast.literal_eval(clipParam),
            adminvalidation = '',
            processed = False,
            mapid =  requestData['mapObj'].id,
            algorithm = requestData['georeference']['algorithm'])

        request.db.add(georefProcess)
        request.db.flush()

        LOGGER.debug('Create response ...')
        # @TODO has to be updated
        points = int(len(requestData['georeference']['gcps']) * 5)
        return {'text':'Georeference result saved. It will soon be ready for use.','georeferenceid':georefProcess.id, 'points':points}
    except ParameterException as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPBadRequest(ERROR_MSG)
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPInternalServerError(ERROR_MSG)

def parseConfirmationRequestParams(request):
    """ Checks if the request params are complete and parse them

    :type request: pyramid.request
    :return: dict
    :raise: georeference.utils.exceptions.ParameterException """
    requestData = parseGeoreferenceParamsFromRequest(request)
    requestData['userid'] = requestData['username'] # checkIsUser(request)

    if not 'type' in requestData:
        raise ParameterException("Missing type field in request.")
    if requestData['type'] == 'update' and 'overwrites' not in requestData:
        raise ParameterException("Missing overwrites field in update request.")

    return requestData