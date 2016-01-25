'''
Created on May 11, 2015

@author: mendt
'''
import unittest
import logging
import os
from datetime import datetime


from georeference.settings import ELASTICSEARCH_INDEX
from georeference.models.vkdb.map import Map
from georeference.models.vkdb.metadata import Metadata
from georeference.test.basetestcase import BaseTestCase
from georeference.persistent.elastic.datamodel import createSearchRecord
from georeference.persistent.elastic.elasticsearch import deleteRecordFromEsById
from georeference.persistent.elastic.elasticsearch import getRecordFromEsById
from georeference.persistent.elastic.elasticsearch import pushRecordToEs

class ElasticsearchTest(BaseTestCase):
    
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
                isttransformiert = True
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
        
        try:
            for obj in self.testData:
                self.dbsession.add(obj)
                self.dbsession.flush()
        except Exception:
            raise
        
    def tearDown(self):
        self.dbsession.rollback()
 
    def testPushRecordToEs(self):
        mapObj = Map.by_id(10000023, self.dbsession)
        datarecord = createSearchRecord(mapObj, self.dbsession, self.logger)
        key = pushRecordToEs(datarecord, ELASTICSEARCH_INDEX, self.logger)

        print '====================='
        print 'Test if testPushRecordToEs ...'
        print 'Response: %s'%key
        print '====================='
        
        # check if the record was insert correctly
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
    