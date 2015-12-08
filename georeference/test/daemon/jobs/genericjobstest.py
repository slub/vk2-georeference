# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import unittest
import logging
import os
import time
from georeference.settings import DBCONFIG_PARAMS_TESTING
from georeference.settings import TEST_LOGIN
from georeference.settings import TEST_DATA_DIR
from georeference.models.meta import initializeDb
from georeference.models.meta import getPostgresEngineString
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.daemon.jobs.genericjobs import processGeorefImage
from georeference.utils.logger import createLogger

class GernicJobsTest(unittest.TestCase):

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

    def tearDown(self):
        self.dbsession.rollback()

    def testProcessGeorefImage(self):
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Test if testProcessGeorefImage runs correctly ..."

        response = processGeorefImage(self.map, self.process, self.dbsession, self.logger)
        self.assertTrue(isinstance(response, str))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
