# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 02.10.15

@author: mendt
@description:
    The following scripts updates the database path for all map files.
'''
import gdal
from georeference.settings import DBCONFIG_PARAMS
from georeference.utils.process.tools import sortPolygonCoordinates
from georeference.utils.process.georeferencer import transformClipPolygon
from georeference.utils.parser.georeferenceparser import parseGcps
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess

APS_PERMALINK_PATH = 'http://www.deutschefotothek.de/list/freitext/'

def updateClipPolygonFromOldPolygon(georefObj):
    """ Function generates a new polygon string from and old polygon string.

    :type georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess: georefObj
    :return:
    """
    print 'Update clip for georeference process with id %s ...' % georefObj.id
    # generate clip polygon
    polygon = georefObj.clippolygon['polygon']
    gcps = parseGcps(georefObj.georefparams['gcps'])
    geoTransform = gdal.GCPsToGeoTransform(gcps)
    transformedClipPolygon = transformClipPolygon(polygon, geoTransform)
    correctedPolygon = sortPolygonCoordinates(transformedClipPolygon)

    # generate clip polygon string
    polygonAsStr = 'POLYGON(('
    for coordinate in correctedPolygon:
        polygonAsStr += str(coordinate[0]) + ' ' + str(coordinate[1]) + ','
    polygonAsStr = polygonAsStr[:-1] + '))'

    # get srid
    srid = georefObj.georefparams['target'].split(':')[1]

    # update database
    if len(correctedPolygon) > 4:
        georefObj.setClip(polygonAsStr, srid, dbsession)

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS), False)
    processes = Georeferenzierungsprozess.all(dbsession)

    for georefObj in processes:
        if georefObj.clippolygon is not None and len(georefObj.georefparams['gcps']) == 4 and georefObj.id < 6934:
            updateClipPolygonFromOldPolygon(georefObj)
    dbsession.commit()