# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import unittest
from pyramid import testing

from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.views.process.georeferenceconfirm import georeferenceConfirm
from georeference.test.basetestcase import BaseTestCase

TEST_LOGIN = 'test_user'

class GeoreferenceConfirmTest(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        BaseTestCase.setUpClass()

        # create and insert test data to database
        cls.testData = {
            'mapObj': Map(id = 10000023, apsobjectid = 90015724, apsdateiname = "df_dk_0010001_3352_1918",
                  originalimage = '', georefimage = '', istaktiv = False, isttransformiert = False,
                  maptype = 'M', hasgeorefparams = 0)
        }

    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.dbmaker = self.Session

        # create dummy georefprocess
        self.notReferencedObjId = 10000023
        self.dummyProcess = Georeferenzierungsprozess(
                    mapid = 10000023,
                    messtischblattid = 90015724,
                    nutzerid = TEST_LOGIN,
                    clipparameter = "{'Test':'Test'}",
                    georefparams = "{}",
                    timestamp = "2014-08-09 12:20:26",
                    type = 'new',
                    clippolygon = '',
                    algorithm = '',
                    isactive = True,
                    processed = False,
                    overwrites = 0,
                    adminvalidation = '')

        self.dummyParams = {
            'georeference': {
                'source': 'pixel',
                'target': 'EPSG:4314',
                'gcps': [
                    {'source': [467, 923], 'target': [10.6666660308838, 51.4000015258789]},
                    {'source': [7281, 999], 'target': [10.8333339691162, 51.4000015258789]},
                    {'source': [7224, 7432], 'target': [10.8333339691162, 51.2999992370605]},
                    {'source': [258, 7471], 'target': [10.6666660308838, 51.2999992370605]}
                ]
            },
            'id': 10000023,
            "clip": {
                "source":"EPSG:4314",
                "polygon": [[10.6666660308838, 51.4000015258789],[10.8333339691162, 51.4000015258789],[10.8333339691162, 51.2999992370605],
                            [10.6666660308838, 51.2999992370605],[10.6666660308838, 51.4000015258789]]
            },
            "algorithm": "affine",
            "userid": TEST_LOGIN
        }

        # add test data
        self.dbsession.add(self.testData['mapObj'])
        self.dbsession.flush()


    def tearDown(self):
        testing.tearDown()
        self.dbsession.rollback()

    def testConfirmedTypeNewPassed(self):

        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Testing correct working of georeferenceConfirm for valide input parameters ..."

        # get query params
        params = self.dummyParams
        params["type"] = 'new'

        request = self.getPOSTRequest(params)
        response = georeferenceConfirm(request)

        print "Response - %s"%response

        self.assertEqual(response['text'], 'Georeference result saved. It will soon be ready for use.',
                         'The response parameter text is not like expected ...')
        self.assertTrue('georeferenceid' in response, 'Missing parameter in response ...')
        self.assertTrue('points' in response, 'Missing parameter in response ...')
        self.assertEqual(response['points'], 20, 'The response (points) is not like expected ...')

    def testConfirmedTypeNewFailed(self):

        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Testing correct working of georeferenceGetProcess for an objectid for a existing process ..."

        # First test if it correctly response in case of existing georef process
        # Create dummy process
        georefProc = self.dummyProcess
        self.dbsession.add(georefProc)
        self.dbsession.flush()

        params = self.dummyParams
        params["type"] = "new"
        request = self.getPOSTRequest(params)
        response = georeferenceConfirm(request)

        print "Response - %s"%response

        self.assertTrue('text' in response, 'Confirmation failed. There is already an active process of type new. Please use the georeferenceid for updating')
        self.assertEqual(response['georeferenceid'], georefProc.id, 'The response (georeferenceid) is not like expected ...')

        self.dbsession.delete(georefProc)
        self.dbsession.flush()

    def testConfirmedTypeUpdate(self):

        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Testing correct working of georeferenceGetProcess for an objectid for a existing process ..."

        # First test if it correctly response in case of existing georef process
        # Create dummy process
        georefProc = self.dummyProcess
        self.dbsession.add(georefProc)
        self.dbsession.flush()

        params = self.dummyParams
        params["type"] = "update"
        params["overwrites"] = georefProc.id
        request = self.getPOSTRequest(params)
        response = georeferenceConfirm(request)

        print "Response - %s"%response

        self.assertEqual(response['text'], 'Georeference result saved. It will soon be ready for use.',
                         'The response parameter text is not like expected ...')
        self.assertTrue('georeferenceid' in response, 'Missing parameter in response ...')
        self.assertTrue('points' in response, 'Missing parameter in response ...')
        self.assertEqual(response['points'], 20, 'The response (points) is not like expected ...')

        self.dbsession.delete(georefProc)
        self.dbsession.flush()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()