# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 06.10.15

@author: mendt
'''
import traceback
from georeference import LOGGER
from georeference.settings import OAI_ID_PATTERN
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.metadata import Metadata
from georeference.utils.tools import convertUnicodeDictToUtf
from georeference.utils.process.tools import convertPostgisStringToList

from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.view import view_config
from sqlalchemy import desc
from sqlalchemy.sql.expression import or_

GENERAL_ERROR_MESSAGE = 'Something went wrong while trying to process your requests. Please try again or contact the administrators of the Virtual Map Forum 2.0.'

@view_config(route_name='admin-process', renderer='json')
def adminEvaluationGeoreferenceProcess(request):
    try:
        LOGGER.info('Request - Get georeference processes.')

        if 'mapid' in request.params:
            LOGGER.debug('Get processes for mapid %s ...'%request.params['mapid'])
            # parse the id
            mapid = None
            if '-' in request.params['mapid']:
                namespace, mapid = request.params['mapid'].rsplit('-', 1)
                # check if it is the correct namespace
                if namespace != OAI_ID_PATTERN.rsplit('-', 1)[0]:
                    return []
            queryData = request.db.query(Georeferenzierungsprozess, Metadata).join(Metadata, Georeferenzierungsprozess.mapid == Metadata.mapid)\
                .filter(Georeferenzierungsprozess.mapid == mapid)\
                .order_by(desc(Georeferenzierungsprozess.id))
        elif 'userid' in request.params:
            LOGGER.debug('Get processes for userid %s ...'%request.params['userid'])
            queryData = request.db.query(Georeferenzierungsprozess, Metadata).join(Metadata, Georeferenzierungsprozess.mapid == Metadata.mapid)\
                .filter(Georeferenzierungsprozess.nutzerid == request.params['userid'])\
                .order_by(desc(Georeferenzierungsprozess.id))
        elif 'validation' in request.params:
            LOGGER.debug('Get processes for adminvalidation %s ...'%request.params['validation'])
            queryData = request.db.query(Georeferenzierungsprozess, Metadata).join(Metadata, Georeferenzierungsprozess.mapid == Metadata.mapid)\
                .filter(Georeferenzierungsprozess.adminvalidation == request.params['validation'])\
                .order_by(desc(Georeferenzierungsprozess.id))
        else:
            LOGGER.debug('Get all pending processes ...')
            queryData = request.db.query(Georeferenzierungsprozess, Metadata).join(Metadata, Georeferenzierungsprozess.mapid == Metadata.mapid)\
                .filter(or_(Georeferenzierungsprozess.adminvalidation == '', Georeferenzierungsprozess.adminvalidation == None))\
                .order_by(desc(Georeferenzierungsprozess.id))

        response = []
        for record in queryData:
            georef = record[0]
            metadata = record[1]
            dict = {
                    'georef_id':georef.id,
                    'mapid':georef.mapid,
                    'georef_params': georef.georefparams,
                    'time': str(metadata.timepublish),
                    'processed': georef.processed,
                    'adminvalidation': georef.adminvalidation,
                    'title': metadata.title,
                    'apsobjectid': georef.messtischblattid,
                    'georef_time':str(georef.timestamp),
                    'type':georef.type,
                    'userid': georef.nutzerid,
                    'georef_isactive':georef.isactive
                }

            if georef.clip is not None:
                dict['clippolygon'] = {
                    'source': 'EPSG:%s' % georef.getSRIDClip(request.db),
                    'polygon': convertPostgisStringToList(georef.clip)
                }

            response.append(dict)
        return response
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        return HTTPInternalServerError(GENERAL_ERROR_MESSAGE)
