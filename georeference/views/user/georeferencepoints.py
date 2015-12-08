# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 07.10.15

@author: mendt
'''
import traceback
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from sqlalchemy import desc
from sqlalchemy import func

from georeference import LOGGER
from georeference.utils.exceptions import ParameterException
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata

GENERAL_ERROR_MESSAGE = 'Something went wrong while trying to process your requests. Please try again or contact the administrators of the Virtual Map Forum 2.0.'

@view_config(route_name='user-georeference-information', renderer='json')
def getGeoreferencePoints(request):

    LOGGER.info('Request - Get georeference points.')
    dbsession = request.db
    try:
        LOGGER.debug('Get points per user')
        queryData = request.db.query(Georeferenzierungsprozess.nutzerid, func.count(Georeferenzierungsprozess.nutzerid))\
            .filter(Georeferenzierungsprozess.adminvalidation != 'invalide')\
            .group_by(Georeferenzierungsprozess.nutzerid)\
            .order_by(desc(func.count(Georeferenzierungsprozess.nutzerid)))\
            .limit(10)
        user_points = []
        for record in queryData:
            userid = record[0]
            count = record[1]
            user_points.append({'userid':userid, 'points': 20*count})

        LOGGER.debug('Get georeference map count')
        queryData = request.db.query(func.count(Map.isttransformiert))\
            .filter(Map.isttransformiert == True)\
            .filter(Map.istaktiv == True)
        georeference_map_count = []
        for record in queryData:
            georeference_map_count = record[0]

        LOGGER.debug('Get missing georeference map count')
        queryData = request.db.query(func.count(Map.isttransformiert))\
            .filter(Map.isttransformiert == False)\
            .filter(Map.istaktiv == True)
        missing_georeference_map_count = []
        for record in queryData:
            missing_georeference_map_count = record[0]

        return {'pointoverview': user_points, 'georeference_map_count': georeference_map_count, 'missing_georeference_map_count':missing_georeference_map_count}
    except Exception as e:
        LOGGER.error('Error while trying to request georeference history information');
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPInternalServerError(GENERAL_ERROR_MESSAGE)