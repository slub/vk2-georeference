import unittest
import os
from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest
from georeference.models.vkdb.map import Map
from georeference.test.basetestcase import BaseTestCase
from georeference.views.process.georeferencevalidation import georeferenceValidation

class GeoreferenceValidationTest(BaseTestCase):
    
    def setUp(self):     
        self.config = testing.setUp()   
        self.config.registry.dbmaker = self.Session  
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
            'id': 10002567
        }
        
        # add testdata to database
        self.testData = [
            Map(id = 10002567, apsobjectid=90015724, apsdateiname = "df_dk_0010001_4630_1928", 
                boundingbox = "POLYGON((10.6666660308838 51.2999992370605,10.6666660308838 51.4000015258789,10.8333339691162 51.4000015258789,10.8333339691162 51.2999992370605,10.6666660308838 51.2999992370605))",
                originalimage = os.path.join(self.testDataDir, "df_dk_0010001_4630_1928.tif"))
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
    
    def testGetGeorefValidationForAffine(self):
        """ Test if the georeferenceValidation response a valid result with an affine transformation. """
               
        params = self.dummyParams
        request = self.getPOSTRequest(params)
        response = georeferenceValidation(request)
        
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetGeorefValidationForAffine with valide parameters ..."
        print "Response - %s"%response
        print "--------------------------------------------------------------------------------------------"

        self.assertTrue('layerId' in response, 'Missing parameter layer_id ....')
        self.assertEqual('df_dk_0010001_4630_1928', response['layerId'], 'Wrong parameter for layer_id ...')
        self.assertTrue('wmsUrl' in response, 'Wrong parameter for wms_url ...')
        
    def testGetGeorefValidationForTPS(self):
        """ Test if the georeferenceValidation response a valid result with an tps transformation. """
               
        params = self.dummyParams
        params['georeference']['algorithm'] = 'tps'
        request = self.getPOSTRequest(params)
        response = georeferenceValidation(request)
        
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetGeorefValidationForTPS with valide parameters ..."
        print "Response - %s"%response
        print "--------------------------------------------------------------------------------------------"

        self.assertTrue('layerId' in response, 'Missing parameter layer_id ....')
        self.assertEqual('df_dk_0010001_4630_1928', response['layerId'], 'Wrong parameter for layer_id ...')
        self.assertTrue('wmsUrl' in response, 'Wrong parameter for wms_url ...')
        
    def testGetGeorefValidationForPolynom(self):
        """ Test if the georeferenceValidation response a valid result with an polynom transformation. """
               
        params = self.dummyParams
        params['georeference']['algorithm'] = 'polynom'
        request = self.getPOSTRequest(params)
        response = georeferenceValidation(request)
        
        print "--------------------------------------------------------------------------------------------"
        print "Testing correct working of testGetGeorefValidationForPolynom with valide parameters ..."
        print "Response - %s"%response
        print "--------------------------------------------------------------------------------------------"

        self.assertTrue('layerId' in response, 'Missing parameter layer_id ....')
        self.assertEqual('df_dk_0010001_4630_1928', response['layerId'], 'Wrong parameter for layer_id ...')
        self.assertTrue('wmsUrl' in response, 'Wrong parameter for wms_url ...')
        
    def testGeoreferenceValidation_correctFail(self):
        
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Testing correct error behavior in case of wrong id parameter ..."
        print "--------------------------------------------------------------------------------------------"

        params_wrongObjId = self.dummyParams
        params_wrongObjId['id'] = 1
        request_wrongObjId = self.getPOSTRequest(params_wrongObjId)
        self.assertRaises(HTTPBadRequest, georeferenceValidation, request_wrongObjId)
    
    def testGeoreferenceValidationWrongParams1(self):
        
        print "--------------------------------------------------------------------------------------------"
        print "Testing testGeoreferenceValidationWrongParams1 ..."
        print "--------------------------------------------------------------------------------------------"
        
        params = {       
            'georeference': {
                'source': 'pixel', 
                'target': 'EPSG:4314', 
                'gcps': []
            }, 
            'id': 10002567
        }
        request = self.getPOSTRequest(params)
        self.assertRaises(HTTPBadRequest, georeferenceValidation, request)

    def testGeoreferenceValidationWrongParams2(self):
        
        print "--------------------------------------------------------------------------------------------"
        print "Testing testGeoreferenceValidationWrongParams2 ..."
        print "--------------------------------------------------------------------------------------------"
        
        params = {       
            'georeference': {
                'source': 'pixel', 
                'target': 'EPSG:4314', 
                'gcps': []
            }, 
            'id': 10002567
        }
        request = self.getPOSTRequest(params)
        self.assertRaises(HTTPBadRequest, georeferenceValidation, request)
        
    def testGeoreferenceValidationWrongParams3(self):
        
        print "--------------------------------------------------------------------------------------------"
        print "Testing testGeoreferenceValidationWrongParams4 ..."
        print "--------------------------------------------------------------------------------------------"
        
        params = {}
        request = self.getPOSTRequest(params)
        self.assertRaises(HTTPBadRequest, georeferenceValidation, request)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main() 