# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 20.01.16

@author: mendt

The following script update aggregated layers.
'''
import os
import logging
from georeference.settings import DBCONFIG_PARAMS
from georeference.settings import GEOREFERENCE_PERSITENT_VRT
from georeference.settings import TMP_DIR
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map
from georeference.persitent.binding.wms import pushMapObjToWmsDatabaseIndex
from georeference.persitent.binding.wms import removeMapObjFromWmsDatabaseIndex
from georeference.scripts.updatevrt import updateVirtualdatasetForTimestamp


# Id in the database of the wms layer
AGGREGATED_LAYERID = {
    'mtb':87
}

def updateMTBLayer(dbsession, logger, withOverviews=False):
    """ Functions update the vrt databasis for a mtb layer

    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    :type boolean: withOverviews (Default: False) Be careful with this parameter, because of much more workload todo.
    :return: str """
    logger.info('Update aggregated layer for MTBs ...')

    logger.info('Update database reference of the aggregated layer ...')
    mapObjs = Map.all(dbsession)
    for mapObj in mapObjs:
        if str(mapObj.maptype).lower() == 'mtb':
            if mapObj.isttransformiert:
                pushMapObjToWmsDatabaseIndex(mapObj, AGGREGATED_LAYERID[str(mapObj.maptype).lower()], dbsession)
            else:
                removeMapObjFromWmsDatabaseIndex(mapObj, AGGREGATED_LAYERID[str(mapObj.maptype).lower()], dbsession)

    logger.info('Update vrts for this aggregated layer ... ')
    for value in range(1868, 1946):
        updateVirtualdatasetForTimestamp('%s-01-01 00:00:00'%value, os.path.join(GEOREFERENCE_PERSITENT_VRT, 'mtb'), TMP_DIR, DBCONFIG_PARAMS, dbsession, logger)

    if withOverviews:
        logger.info('Calculate overviews for vrts ...')

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    logging.basicConfig()
    logger = logging.getLogger('update-aggregated-layers')

    # update the aggregated layers
    updateMTBLayer(dbsession, logger)
    logger.info('Finish updating aggregated layers.')
    dbsession.commit()