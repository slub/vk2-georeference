# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import ast
import unittest
from pyramid import testing

from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata
from georeference.test.basetestcase import BaseTestCase
from georeference.views.process.georeferenceresourcebyobjectid import getByObjectId

class GeoreferenceResourceTest(BaseTestCase):
    
    def setUp(self):     
        self.config = testing.setUp()   
        self.config.registry.dbmaker = self.Session  


        # create and insert test data to database
        self.testData = [
            Map(id = 10000023, apsobjectid=90015724, apsdateiname = "df_dk_0010001_3352_1890", recommendedsrid=4314, boundingbox = "POLYGON((16.9999980926514 51.7999992370605,16.9999980926514 51.9000015258789,17.1666679382324 51.9000015258789,17.1666679382324 51.7999992370605,16.9999980926514 51.7999992370605))", maptype="M"),
            Map(id = 10000024, apsobjectid=90015725, apsdateiname = "df_dk_0010001_3352_18901", maptype = "GL"),
            Metadata(mapid = 10000023, imagezoomify = 'http://fotothek.slub-dresden.de/zooms/df/dk/0010000/df_dk_0010001_3352_1918/ImageProperties.xml', title = '', titleshort = ''),
            Metadata(mapid = 10000024, imagezoomify = 'http://fotothek.slub-dresden.de/zooms/df/dk/0010000/df_dk_0010001_3352_1918/ImageProperties.xml', title = '', titleshort = '')
        ]
        
        try:
            for obj in self.testData:
                self.dbsession.add(obj)
                self.dbsession.flush()
        except Exception:
            raise
         
    def tearDown(self):
        testing.tearDown()    
        self.dbsession.rollback()
        
    def testGetProcessWithPOSTRequest(self):
         
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetProcessWithPOSTRequest for an objectid for a new mtb process ..."
        print "--------------------------------------------------------------------------------------------"
         
        params = {'objectid':'oai:de:slub-dresden:vk:id-10000023'}
        request = self.getPOSTRequest(params)
        response = getByObjectId(request)
         
        print "Response - %s"%response

        self.assertTrue("recommendedsrid" in response, "Missing key/value in response ...")
        self.assertEqual(response["recommendedsrid"], 4314, "Response has not expexted maptype ...")
        self.assertTrue("objectid" in response, "Missing key/value in response ...")
        self.assertTrue("timestamp" in response, "Missing key/value in response ...")
        self.assertTrue("type" in response, "Missing key/value in response ...")
        self.assertEqual(response["type"], "new", "Response has not expexted maptype ...")
        self.assertTrue("maptype" in response, "Missing key/value in response ...")
        self.assertEqual(response["maptype"], "M", "Response has not expexted maptype ...")
        self.assertTrue("zoomify" in response, "Missing key/value in response ...")
        self.assertTrue("metadata" in response, "Missing key/value in response ...")
        self.assertTrue("title_short" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("title_long" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("dateiname" in response["metadata"], "Missing key/value in response ...")
        

    def testGetProcessWithTwoParam(self):

        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of georeferenceGetProcess for an objectid/georeferenceid for a existing process ..."

        # First test if it correctly response in case of existing georef process
        # Create dummy process
        georefProc = Georeferenzierungsprozess(
                    mapid = 10000023,
                    messtischblattid = 90015724,
                    nutzerid = self.user,
                    georefparams = ast.literal_eval("{'new': { 'source': 'pixel', 'target': 'EPSG:4314',\
                        'gcps': [{'source': [8681, 1013], 'target': [8.50000095367432, 54.7000007629395]},\
                        {'source': [8576, 7372], 'target': [8.50000095367432, 54.5999984741211]},\
                        {'source': [2358, 7260], 'target': [8.33333301544189, 54.5999984741211]},\
                        {'source': [2465, 888], 'target': [8.33333301544189, 54.7000007629395]}], 'algorithm':'affine'},\
                        'remove': {'source': 'pixel', 'target': 'EPSG:4314', 'gcps': [\
                        {'source': [483, 7227], 'target': [8.33333301544189, 54.5999984741211]}, {'source': [464, 840], 'target': [8.33333301544189, 54.7000007629395]}]}}"),
                    clip = "POLYGON((16.9999980926514 51.7999992370605,16.9999980926514 51.9000015258789,17.1666679382324 51.9000015258789,17.1666679382324 51.7999992370605,16.9999980926514 51.7999992370605))",
                    timestamp = "2014-08-09 12:20:26",
                    type = 'new',
                    isactive = True,
                    processed = True,
                    overwrites = 0,
                    adminvalidation = ''
        )
        self.dbsession.add(georefProc)
        self.dbsession.flush()

        # object id and georeferenceid are different for testing that the georeferenceid beat the objectid
        params = {'objectid':'oai:de:slub-dresden:vk:id-10000023'}
        request = self.getPOSTRequest(params)
        response = getByObjectId(request)

        print "Response - %s"%response

        self.assertEqual(response['extent'], [16.9999980926514, 51.7999992370605, 17.1666679382324, 51.9000015258789],
                         'Wrong or missing parameter in response ...')
        self.assertEqual(response['objectid'], 10000023,'Wrong or missing parameter in response ...')
        self.assertEqual(response['timestamp'], "2014-08-09 12:20:26",'Wrong or missing parameter in response ...')
        self.assertEqual(response['georeferenceid'], georefProc.id,'Wrong or missing parameter in response ...')
        self.assertEqual(response['type'], "update",'Wrong or missing parameter in response ...')
        self.assertEqual(response['zoomify'], "http://fotothek.slub-dresden.de/zooms/df/dk/0010000/df_dk_0010001_3352_1918/ImageProperties.xml",'Wrong or missing parameter in response ...')

        self.dbsession.delete(georefProc)
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main() 