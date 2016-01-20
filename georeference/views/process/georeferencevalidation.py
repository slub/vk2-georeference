# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import gdal
import os
import traceback
import uuid
from gdal import GA_ReadOnly
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError

from georeference import LOGGER
from georeference.settings import ADMIN_ADDR
from georeference.settings import GEOREFERENCE_MAPFILE_FOLDER
from georeference.settings import GEOREFERENCE_MAPFILE_TEMPLATE
from georeference.settings import GEOREFERENCE_MAPFILE_DEFAULT_PARAMS
from georeference.settings import TMP_DIR
from georeference.utils.exceptions import ParameterException
from georeference.utils.parser.georeferenceparser import parseGcps
from georeference.utils.parser.georeferenceparser import parseGeoreferenceParamsFromRequest
from georeference.utils.process.georeferencer import rectifyImageAffine
from georeference.utils.process.georeferencer import rectifyTpsWithVrt
from georeference.utils.process.georeferencer import rectifyPolynomWithVRT
from georeference.utils.process.mapfile import createMapfile
from georeference.utils.process.tools import getBoundsFromDataset
from georeference.utils.process.tools import stripSRIDFromEPSG

ERROR_MSG = "Please check your request parameters or contact the administrator (%s)."%ADMIN_ADDR

@view_config(route_name='georeference', renderer='json', match_param='action=validation')
def georeferenceValidation(request):
    """ The function generates a process validation result and publish it via a WMS instance. The
        wms references are returned.

        :type request: pyramid.request
        :return: dict
        :raise: HTTPBadRequest
        :raise: HTTPInternalServerError """
    LOGGER.info('Receive process validation request with parameters: %s'%request.json_body)

    try:
        # extract validation data
        LOGGER.debug('Parse request params ...')
        requestParams = parseGeoreferenceParamsFromRequest(request)

        LOGGER.debug('Parse and validate SRS params ...')
        georefSourceSRS = requestParams['georeference']['source']
        if str(georefSourceSRS).lower() != 'pixel':
            raise ParameterException('Only "pixel" is yet supported as source srs.')

        if ':' not in str(requestParams['georeference']['target']):
            raise ParameterException('Missing "EPSG:...." syntax for target srs.')
        georefTargetSRS = stripSRIDFromEPSG(requestParams['georeference']['target'])

        # generate a temporary process result and publish it via wms
        LOGGER.debug('Parse and validate gcps params ...')
        if len(requestParams['georeference']['gcps']) < 2:
            raise ParameterException('Not enough gcps for valid georeferencing ...')
        gcps = parseGcps(requestParams['georeference']['gcps'])

        # calculate validation result
        return createValidationResult(requestParams, gcps, georefTargetSRS, LOGGER)

    except ParameterException as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPBadRequest(ERROR_MSG)
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(traceback.format_exc())
        raise HTTPInternalServerError(ERROR_MSG)

def createValidationResult(requestParams, gcps, gcpstargetSrs, LOGGER):
    """ Function creates a process image and creates a temporary wms.

    :type requestParams: dict
    :type gcps: List.<gdal.GCP>
    :type georefTargetSRS: int
    :type LOGGER: logging.LOGGER
    :return: str
    :raise: vkviewer.python.georef.georeferenceexceptions.ParameterException """
    LOGGER.debug('Process georeference result ...')
    tmpFile = os.path.join(GEOREFERENCE_MAPFILE_FOLDER,requestParams['mapObj'].apsdateiname+"::"+str(uuid.uuid4())+".tif")
    destPath = None
    if requestParams['georeference']['algorithm'] == 'affine':
        destPath = rectifyImageAffine(requestParams['mapObj'].originalimage, tmpFile,
                [], gcps, gcpstargetSrs, LOGGER)
    elif requestParams['georeference']['algorithm'] == 'polynom':
        destPath = rectifyPolynomWithVrt(requestParams['mapObj'].originalimage, tmpFile, gcps, gcpstargetSrs, LOGGER, TMP_DIR)
    elif requestParams['georeference']['algorithm'] == 'tps':
        destPath = rectifyTpsWithVrt(requestParams['mapObj'].originalimage, tmpFile, gcps, gcpstargetSrs, LOGGER, TMP_DIR)
    else:
        raise ParameterException('Transformation algorithm - %s - is not supported yet.'%requestParams['georeference']['algorithm'])

    LOGGER.debug('Create temporary mapfile ...')
    wmsUrl = createMapfile(requestParams['mapObj'].apsdateiname, destPath, gcpstargetSrs, GEOREFERENCE_MAPFILE_TEMPLATE, GEOREFERENCE_MAPFILE_FOLDER, GEOREFERENCE_MAPFILE_DEFAULT_PARAMS)

    LOGGER.debug('Calculate extent ...')
    dataset = gdal.Open(destPath, GA_ReadOnly)
    extent = getBoundsFromDataset(dataset)
    LOGGER.debug('Deliver results.')
    return {'wmsUrl':wmsUrl,'layerId':requestParams['mapObj'].apsdateiname, 'extent': extent}