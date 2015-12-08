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


class GeoreferenceResourceByObjectIdTest(BaseTestCase):
    
    def setUp(self):     
        self.config = testing.setUp()   
        self.config.registry.dbmaker = self.Session  
        
        # create dummy georefprocess
        self.notReferencedObjId = 10000023
        self.dummyProcess = Georeferenzierungsprozess(
                    mapid = 10000023, 
                    messtischblattid = 90015724, 
                    nutzerid = self.user, 
                    clipparameter = "{'Test':'Test'}", 
                    georefparams = "{'Test':'Test'}",
                    timestamp = "2014-08-09 12:20:26", 
                    type = 'new', 
                    isactive = True,
                    processed = False,
                    overwrites = 0,
                    adminvalidation = ''
        )
        self.dummyProcessUpdate = Georeferenzierungsprozess(
                    mapid = 10000023, 
                    messtischblattid = 90015724, 
                    nutzerid = self.user, 
                    clipparameter = "{'new': {'source': 'pixel', 'target': 'EPSG:4314', 'gcps': [\
                        {'source': [467, 923], 'target': [10.6666660308838, 51.4000015258789]}, \
                        {'source': [7281, 999], 'target': [10.8333339691162, 51.4000015258789]}, \
                        {'source': [7224, 7432], 'target': [10.8333339691162, 51.2999992370605]},\
                        {'source': [258, 7471], 'target': [10.6666660308838, 51.2999992370605]}]},\
                                    'remove':{'source': 'pixel', 'target': 'EPSG:4314', 'gcps':[]}}", 
                    georefparams = "{'new': {'source': 'pixel', 'target': 'EPSG:4314', 'gcps': [\
                        {'source': [467, 923], 'target': [10.6666660308838, 51.4000015258789]}, \
                        {'source': [7281, 999], 'target': [10.8333339691162, 51.4000015258789]}, \
                        {'source': [7224, 7432], 'target': [10.8333339691162, 51.2999992370605]},\
                        {'source': [258, 7471], 'target': [10.6666660308838, 51.2999992370605]}]},\
                                    'remove':{'source': 'pixel', 'target': 'EPSG:4314', 'gcps':[]}}", 
                    timestamp = "2014-08-09 12:20:26", 
                    type = 'update', 
                    isactive = False,
                    processed = False,
                    overwrites = 0,
                    adminvalidation = ''
        )
        
        # create and insert test data to database
        self.testData = [
            Map(id = 10000023, apsobjectid=90015724, apsdateiname = "df_dk_0010001_3352_1890", boundingbox = "POLYGON((16.9999980926514 51.7999992370605,16.9999980926514 51.9000015258789,17.1666679382324 51.9000015258789,17.1666679382324 51.7999992370605,16.9999980926514 51.7999992370605))", maptype="M"),
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
                 
        self.assertTrue("process" in response, "Missing key/value in response ...")
        self.assertTrue("source" in response["process"], "Missing key/value in response ...")
        self.assertTrue("target" in response["process"], "Missing key/value in response ...")
        self.assertTrue("algorithm" in response["process"], "Missing key/value in response ...")
        self.assertTrue("gcps" in response["process"], "Missing key/value in response ...")
        self.assertEqual(response["process"]["gcps"][0]["source"], [], "Response has is not an empty list ...")
        self.assertTrue("extent" in response, "Missing key/value in response ...")
        self.assertTrue("objectid" in response, "Missing key/value in response ...")
        self.assertTrue("timestamp" in response, "Missing key/value in response ...")
        self.assertTrue("type" in response, "Missing key/value in response ...")
        self.assertTrue("maptype" in response, "Missing key/value in response ...")
        self.assertEqual(response["maptype"], "M", "Response has not expexted maptype ...")
        self.assertTrue("zoomify" in response, "Missing key/value in response ...")
        self.assertTrue("metadata" in response, "Missing key/value in response ...")
        self.assertTrue("title_short" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("title_long" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("dateiname" in response["metadata"], "Missing key/value in response ...")
        
    def testGetProcessWithGETRequest(self):
         
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetProcessWithGETRequest for an objectid for a new mtb process ..."
        print "--------------------------------------------------------------------------------------------"
         
        params = {'objectid':'oai:de:slub-dresden:vk:id-10000023'}
        request = self.getGETRequest(params)
        response = getByObjectId(request)
         
        print "Response - %s"%response
                 
        self.assertTrue("process" in response, "Missing key/value in response ...")
        self.assertTrue("source" in response["process"], "Missing key/value in response ...")
        self.assertTrue("target" in response["process"], "Missing key/value in response ...")
        self.assertTrue("algorithm" in response["process"], "Missing key/value in response ...")
        self.assertTrue("gcps" in response["process"], "Missing key/value in response ...")
        self.assertEqual(response["process"]["gcps"][0]["source"], [], "Response has is not an empty list ...")
        self.assertTrue("extent" in response, "Missing key/value in response ...")
        self.assertTrue("objectid" in response, "Missing key/value in response ...")
        self.assertTrue("timestamp" in response, "Missing key/value in response ...")
        self.assertTrue("type" in response, "Missing key/value in response ...")
        self.assertTrue("maptype" in response, "Missing key/value in response ...")
        self.assertEqual(response["maptype"], "M", "Response has not expexted maptype ...")
        self.assertTrue("zoomify" in response, "Missing key/value in response ...")
        self.assertTrue("metadata" in response, "Missing key/value in response ...")
        self.assertTrue("title_short" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("title_long" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("dateiname" in response["metadata"], "Missing key/value in response ...")
 
 
    def testGetProcessWithMaptypeGL(self):
         
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetProcessWithMaptypeGL for an objectid for a new geological map process ..."
        print "--------------------------------------------------------------------------------------------"
         
        params = {'objectid':'oai:de:slub-dresden:vk:id-10000024'}
        request = self.getPOSTRequest(params)
        response = getByObjectId(request)
        
         
        print "Response - %s"%response
                 
        self.assertTrue("process" not in response, "Not allowed key/value in response ...")
        self.assertTrue("extent" not in response, "Not allowed key/value in response ...")
        self.assertTrue("objectid" in response, "Missing key/value in response ...")
        self.assertTrue("timestamp" in response, "Missing key/value in response ...")
        self.assertTrue("type" in response, "Missing key/value in response ...")
        self.assertTrue("maptype" in response, "Missing key/value in response ...")
        self.assertEqual(response["maptype"], "GL", "Response has not expexted maptype ...")
        self.assertTrue("zoomify" in response, "Missing key/value in response ...")
        self.assertTrue("metadata" in response, "Missing key/value in response ...")
        self.assertTrue("title_short" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("title_long" in response["metadata"], "Missing key/value in response ...")
        self.assertTrue("dateiname" in response["metadata"], "Missing key/value in response ...")
     
    def testGetProcessWithRaceCondition(self):
         
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetProcessWithRaceCondition for an objectid for a existing process ..."
        print "--------------------------------------------------------------------------------------------"
 
 
        # First test if it correctly response in case of existing georef process
        # Create dummy process
        georefProc = self.dummyProcess
        georefProc.isactive = False
        self.dbsession.add(georefProc)
        self.dbsession.flush()
                 
        params = {'objectid':'oai:de:slub-dresden:vk:id-10000023'}
        request = self.getPOSTRequest(params)
        response = getByObjectId(request)
         
        print "Response - %s"%response
        # this is important for showing the client that their is actual a race condition with another client
        self.assertTrue('warn' in response, 'Missing parameter (warn) in response ...')        
         
        self.dbsession.delete(georefProc)
        self.dbsession.flush()      
          
    def testGetProcessWithRaceCondition1(self):
         
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetProcessWithRaceCondition1 for an objectid for a existing process ..."
        print "--------------------------------------------------------------------------------------------"
 
        # First test if it correctly response in case of existing georef process
        # Create dummy process
        georefProc = self.dummyProcess
        self.dbsession.add(georefProc)
        self.dbsession.flush()
         
        georefProcUpdate = self.dummyProcessUpdate
        georefProcUpdate.overwrites = georefProc.id
        self.dbsession.add(georefProcUpdate)
        self.dbsession.flush()
         
        params = {'objectid':'oai:de:slub-dresden:vk:id-10000023'}
        request = self.getPOSTRequest(params)
        response = getByObjectId(request)
         
        print "Response - %s"%response
        #self.assertEqual(response["process"],
        self.assertEqual(response["georeferenceid"], georefProc.id)
        # this is important for showing the client that their is actual a race condition with another client
        self.assertTrue('warn' in response, 'Missing parameter (warn) in response ...')        
         
        self.dbsession.delete(georefProc)
        self.dbsession.delete(georefProcUpdate)
        self.dbsession.flush()      
#      
#     # @unittest.skip("testGetProcessWithOneParamAndRaceCondition")       
#     def testGetProcessWithTwoParam(self):
#         
#         print "--------------------------------------------------------------------------------------------"
#         print "Testing correct working of georeferenceGetProcess for an objectid/georeferenceid for a existing process ..."
# 
#         # First test if it correctly response in case of existing georef process
#         # Create dummy process
#         georefProc = self.dummyProcess
#         georefParams = "{'new': { 'source': 'pixel', 'target': 'EPSG:4314',\
#             'gcps': [{'source': [8681, 1013], 'target': [8.50000095367432, 54.7000007629395]},\
#             {'source': [8576, 7372], 'target': [8.50000095367432, 54.5999984741211]},\
#             {'source': [2358, 7260], 'target': [8.33333301544189, 54.5999984741211]},\
#             {'source': [2465, 888], 'target': [8.33333301544189, 54.7000007629395]}], 'algorithm':'affine'},\
#             'remove': {'source': 'pixel', 'target': 'EPSG:4314', 'gcps': [\
#             {'source': [483, 7227], 'target': [8.33333301544189, 54.5999984741211]}, {'source': [464, 840], 'target': [8.33333301544189, 54.7000007629395]}]}}"
#         georefProc.clipparameter = georefParams
#         georefProc.georefparams = ast.literal_eval(georefParams)
#         georefProc.type = 'update'
#         self.dbsession.add(georefProc)
#         self.dbsession.flush()
#         
#         # object id and georeferenceid are different for testing that the georeferenceid beat the objectid
#         params = {'objectid':10000024, 'georeferenceid':georefProc.id}
#         request = self.getRequestWithAuthentification(params)
#         request.json_body = params
#         response = georeferenceGetProcess(request)
#         
#         print "Response - %s"%response
#                 
#         self.assertEqual(response['extent'], [16.9999980926514, 51.7999992370605, 17.1666679382324, 51.9000015258789],
#                          'Wrong or missing parameter in response ...')
#         self.assertEqual(response['objectid'], 10000023,'Wrong or missing parameter in response ...')
#         self.assertEqual(response['timestamp'], "2014-08-09 12:20:26",'Wrong or missing parameter in response ...')
#         self.assertEqual(response['georeferenceid'], georefProc.id,'Wrong or missing parameter in response ...')
#         self.assertEqual(response['type'], "update",'Wrong or missing parameter in response ...')
#         self.assertEqual(response['zoomify'], "http://fotothek.slub-dresden.de/zooms/df/dk/0010000/df_dk_0010001_3352_1918/ImageProperties.xml",'Wrong or missing parameter in response ...')
#         
#         self.dbsession.delete(georefProc)      
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main() 