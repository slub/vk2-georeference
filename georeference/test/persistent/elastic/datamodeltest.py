'''
Created on May 11, 2015

@author: mendt
'''
import unittest
import logging
import os
from datetime import datetime

from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata
from georeference.models.vkdb.georeferenzierungsprozess import Georeferenzierungsprozess
from georeference.test.basetestcase import BaseTestCase
from georeference.persistent.elastic.datamodel import createSearchRecord
from georeference.persistent.elastic.datamodel import getTransformedClipPolygon

class DataModelTest(BaseTestCase):
    
    @classmethod
    def setUpClass(cls):
        BaseTestCase.setUpClass()
        logging.basicConfig(level=logging.DEBUG)
        cls.logger = logging.getLogger('sqlalchemy.engine')
        
    def setUp(self):   
        # create and insert test data to database
        self.testData = [
            Map(
                id = 10000023, 
                apsobjectid=90015724,
                apsdateiname = "df_dk_0010001_4630_1928", 
                boundingbox = "POLYGON((16.9999980926514 51.7999992370605,16.9999980926514 51.9000015258789,17.1666679382324 51.9000015258789,17.1666679382324 51.7999992370605,16.9999980926514 51.7999992370605))", 
                maptype="M",
                originalimage = os.path.join(self.testDataDir, "df_dk_0010001_4630_1928.tif"),
                georefimage = os.path.join(self.testDataDir, "df_dk_0010001_4630_1928.tif"),
                isttransformiert = True,
                recommendedsrid = 4314
            ),
            Metadata(
                mapid = 10000023, 
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
        ]

        self.georefProcess = Georeferenzierungsprozess(
            mapid = 10000023,
            messtischblattid = 90015724,
            nutzerid = self.user,
            clipparameter = {'source': 'pixel', 'target': 'EPSG:4314', 'gcps': [\
                {'source': [467, 923], 'target': [10.6666660308838, 51.4000015258789]}, \
                {'source': [7281, 999], 'target': [10.8333339691162, 51.4000015258789]}, \
                {'source': [7224, 7432], 'target': [10.8333339691162, 51.2999992370605]},\
                {'source': [258, 7471], 'target': [10.6666660308838, 51.2999992370605]}]},
            georefparams = {'source': 'pixel', 'target': 'EPSG:4314', 'gcps': [\
                {'source': [467, 923], 'target': [10.6666660308838, 51.4000015258789]}, \
                {'source': [7281, 999], 'target': [10.8333339691162, 51.4000015258789]}, \
                {'source': [7224, 7432], 'target': [10.8333339691162, 51.2999992370605]},\
                {'source': [258, 7471], 'target': [10.6666660308838, 51.2999992370605]}]},
            clippolygon = {'source': 'pixel', 'polygon': [[7813, 7517], [1652, 7523], [1677, 1666], [7830, 1661], [7813, 7517]]},
            timestamp = "2014-08-09 12:20:26",
            type = 'update',
            isactive = False,
            processed = False,
            overwrites = 0,
            adminvalidation = ''
        )

        try:
            for obj in self.testData:
                self.dbsession.add(obj)
                self.dbsession.flush()
        except Exception:
            raise
        
    def tearDown(self):
        self.dbsession.rollback()
 
    def testGetDataRecord(self):
        mapObj = Map.by_id(10000023, self.dbsession)
        response = createSearchRecord(mapObj, self.dbsession, self.logger, self.georefProcess)

        print '====================='
        print 'Test if testGetDataRecord ...'
        print 'Response: %s'%response
        print '====================='
        
        self.assertTrue('oai:de:slub-dresden:vk:id-10000023' in response, 'Missing key in response')
        self.assertEqual(response['oai:de:slub-dresden:vk:id-10000023']['dataid'], 'df_dk_0010001_4630_1928', 'Dataid has not expected value')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    