# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 02.10.15

@author: mendt
@description:
    The following scripts updates the database path for all map files.
'''
from os import path
from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata

TEMPLATE_THUMBSSMALL = 'http://fotothek.slub-dresden.de/thumbs/%s'
TEMPLATE_THUMBSMID = 'http://fotothek.slub-dresden.de/mids/%s'

if __name__ == '__main__':
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS))
    metadata = Metadata.all(dbsession)

    for metadataObj in metadata:
        if metadataObj.thumbssmall == '' or metadataObj.thumbssmall is None:
            newPathEnding = metadataObj.imagejpg[str(metadataObj.imagejpg).index('dk')-3:]
            metadataObj.thumbssmall = TEMPLATE_THUMBSSMALL%newPathEnding
            metadataObj.thumbsmid = TEMPLATE_THUMBSMID%newPathEnding
    dbsession.commit()