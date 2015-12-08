# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import unittest
import logging
import os
from datetime import datetime
from georeference.settings import DBCONFIG_PARAMS_TESTING
from georeference.settings import TEST_LOGIN
from georeference.settings import TEST_DATA_DIR
from georeference.settings import ELASTICSEARCH_INDEX
from georeference.models.meta import initializeDb
from georeference.models.meta import getPostgresEngineString
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata
from georeference.daemon.jobs.georeferencejobs import activate
from georeference.utils.logger import createLogger
from georeference.daemon.elastic.elasticsearch import getRecordFromEsById
from georeference.daemon.elastic.elasticsearch import deleteRecordFromEsById

class GeoreferenceJobsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print '=============='
        print 'Start GernicJobsTest tests ...'
        print '=============='

        cls.logger = createLogger('GernicJobsTest', logging.DEBUG)
        cls.dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS_TESTING))

    def setUp(self):
        self.process = Georeferenzierungsprozess(
                    mapid = 10002567,
                    nutzerid = TEST_LOGIN,
                    clippolygon = {
                        'source':'pixel',
                        'polygon': [[467, 923],[7281, 999],[7224, 7432],[258, 7471],[467, 923]]},
                    georefparams = {
                        'source': 'pixel',
                        'target': 'EPSG:4314',
                        'gcps': [
                            {'source': [467, 923], 'target': [10.6666660308838, 51.4000015258789]},
                            {'source': [7281, 999], 'target': [10.8333339691162, 51.4000015258789]},
                            {'source': [7224, 7432], 'target': [10.8333339691162, 51.2999992370605]},
                            {'source': [258, 7471], 'target': [10.6666660308838, 51.2999992370605]}
                        ],
                        "algorithm": "affine",
                    },
                    timestamp = "2014-08-09 12:20:26",
                    type = 'new',
                    algorithm = 'affine',
                    isactive = True,
                    processed = False,
                    overwrites = 0,
                    adminvalidation = '')

        self.map = Map(id = 10002567, apsobjectid=90015724, apsdateiname = "df_dk_0010001_4630_1928",
                boundingbox = "POLYGON((10.6666660308838 51.2999992370605,10.6666660308838 51.4000015258789,10.8333339691162 51.4000015258789,10.8333339691162 51.2999992370605,10.6666660308838 51.2999992370605))",
                originalimage = os.path.join(TEST_DATA_DIR, "df_dk_0010001_4630_1928.tif"))

        self.metadata = Metadata(
                mapid = 10002567,
                imagezoomify = 'http://fotothek.slub-dresden.de/zooms/df/dk/0010000/df_dk_0010001_3352_1918/ImageProperties.xml',
                title = '',
                titleshort = '',
                scale = '1:25000',
                timepublish = datetime.now(),
                imagejpg = 'http://fotothek.slub-dresden.de/fotos/df/dk/0010000/df_dk_0010001_2655.jpg',
                thumbssmall = 'http://fotothek.slub-dresden.de/thumbs/df/dk/0010000/df_dk_0010001_6817.jpg',
                description = 'Ars an der Mosel. - Aufn. 1880, hrsg. 1882, Aufldr. 1916. - 1:25000. - [Berlin]: Kgl. Preuss. Landesaufnahme, 1916. - 1 Kt.',
                technic = 'Lithografie & Umdruck',
                type = 'Druckgraphik'
            )

        try:
            self.dbsession.add(self.metadata)
            self.dbsession.add(self.map)
            self.dbsession.flush()
        except Exception:
            raise

    def tearDown(self):
        self.dbsession.rollback()

    def testActivate(self):
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Test if testProcessGeorefImage runs correctly ..."

        key = activate(self.process, self.map, self.dbsession, self.logger)
        self.assertTrue(self.process.processed)
        self.assertTrue(self.map.isttransformiert)
        self.assertTrue(len(self.map.georefimage) > 10)

        # check if the record was added to elasticsearch and remove it when necessary
        response = getRecordFromEsById(key, ELASTICSEARCH_INDEX)
        self.assertEqual(response['found'], True, 'Could not find expected record')
        self.assertEqual(response['_id'], key, 'Key is not like expected')

        # clear up
        response = deleteRecordFromEsById(key, ELASTICSEARCH_INDEX)
        if response['found'] is not True:
            raise Exception("Problems while trying to clean up elasticsearch test index")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
