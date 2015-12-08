# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import gdal
from georeference.models.vkdb.map import Map
from georeference.utils.exceptions import ParameterException

def parseClipPolygon(polygon):
    """
    Function parse a polygon list and brings it in a list tuple structure

    :param polygon: List.<List<?>>
    :return: List.<Tuple<?>>
    """
    response = []
    for record in polygon:
        response.append((record[0], record[1]))
    return response

def parseGcps(georeference):
    """
    :param georeference:  dict
    :return: list.<gdal.GCP>
    """
    gcps = []
    for i in range(0,len(georeference)):
        gcps.append(gdal.GCP(georeference[i]['target'][0], georeference[i]['target'][1], 0, georeference[i]['source'][0],georeference[i]['source'][1]))
    return gcps

def parseGeoreferenceParamsFromRequest(request):
    """ Validates and parses process parameters from a request object.

    :param request: pyramid.request
    :return: dict
    :raise: process.utils.exceptions.ParameterException
    """

    def validateParams(params):
        """
        Checks if all necessary params for a process process are within
        the given parameter set.

        :param params: dict
        :return: bool
        :raise: process.utils.exceptions.ParameterException
        """
        if not 'id' in params:
            raise ParameterException("Missing id field in process request.")
        if not 'georeference' in params:
            raise ParameterException("Missing process field in process request.")
        if not 'clip' in params:
            raise ParameterException("Missing clip field in process request.")
        return True

    requestParams = None
    if request.method == 'POST' and validateParams(request.json_body):
        requestParams = request.json_body

    # look if algorithm is set and if not set it to affine
    if 'algorithm' not in requestParams['georeference']:
        requestParams['georeference']['algorithm'] = 'affine'

    # append mapObj to request data
    mapObj = parseMapObjForId(requestParams, 'id', request.db)
    requestParams['mapObj'] = mapObj

    return requestParams

def parseMapObjForId(requestParams, name, dbsession):
    """
    This functions parses a map objectid from an objectid

    :param requestParams: dict
    :param name: str
    :param dbsession: sqlalchemy.orm.session.Session
    :return: process.models.vkdb.map.Map
    :raise: process.utils.exceptions.ParameterException
    """
    if name in requestParams:
        validateId(requestParams[name])
        # @deprecated
        # do mapping for support of new name schema
        mapObj = Map.by_id(int(requestParams[name]), dbsession)
        if mapObj is None:
            raise ParameterException('Missing or wrong objectid parameter.')
        else:
            return mapObj
    raise ParameterException('Missing or wrong objectid parameter.')

def validateId(id):
    """
    Checks if given id is a valide objectid in the vk2.0 domain.

    :param id: ?
    :return: bool
    :raise: process.utils.exceptions.ParameterException
    """
    errorMsg = "Object identifier is not valide."
    try:
        # check if mtbid is valide
        if (id != None):
            if isinstance(int(id), int):
                return True
            else:
                raise ParameterException(errorMsg)
    except:
        raise ParameterException(errorMsg)

    return False