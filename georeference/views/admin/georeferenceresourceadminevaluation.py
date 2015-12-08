# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 06.10.15

@author: mendt
'''
import traceback
from datetime import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from georeference import LOGGER
from georeference.utils.tools import convertTimestampToPostgisString
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.adminjobs import AdminJobs

#from vkviewer.python.georef.utils import getTimestampAsPGStr
GENERAL_ERROR_MESSAGE = 'Something went wrong while trying to process your requests. Please try again or contact the administrators of the Virtual Map Forum 2.0.'

@view_config(route_name='admin-evaluation', renderer='json', match_param='action=setinvalide')
def setProcessToInValide(request):
    LOGGER.info('Request - Set admin evaluation of georeference process to invalide ....')
    try:
        # remove georeference process
        if 'georeferenceid' in request.params:
            georeferenceid = request.params['georeferenceid']
            comment = '' if 'comment' not in request.params else request.params['comment']

            # check if georeference id exist
            georeferenceprocess = Georeferenzierungsprozess.by_id(georeferenceid, request.db)
            if georeferenceprocess:
                newJob = createNewAdminJob(georeferenceprocess, 'invalide', request.params['userid'], comment)
                request.db.add(newJob)

            return {'message':'The georeference process has been set to invalide.'}
        else:
            raise Exception('Missing parameter (georeferenceid) ...')
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        return HTTPBadRequest(GENERAL_ERROR_MESSAGE);

@view_config(route_name='admin-evaluation', renderer='json', match_param='action=setisvalide')
def setProcessToIsValide(request):
    LOGGER.info('Request - Set admin evaluation of georeference process to isvalide ....')
    try:
        # remove georeference process
        if 'georeferenceid' in request.params:
            georeferenceid = request.params['georeferenceid']
            comment = '' if 'comment' not in request.params else request.params['comment']

            # check if georeference id exist
            georeferenceprocess = Georeferenzierungsprozess.by_id(georeferenceid, request.db)
            if georeferenceprocess:
                newJob = createNewAdminJob(georeferenceprocess, 'isvalide', request.params['userid'], comment)
                request.db.add(newJob)

            return {'message':'The georeference process has been set to isvalide.'}
        else:
            raise Exception('Missing parameter (georeferenceid) ...')
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        return HTTPBadRequest(GENERAL_ERROR_MESSAGE);

def createNewAdminJob(georeferenceprocess, setto, userid, comment):
    return AdminJobs(georefid = georeferenceprocess.id, processed = False, setto = setto,
                     timestamp = convertTimestampToPostgisString(datetime.now()), comment = comment, userid = userid)