# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
'''
Created on Feb 11, 2015

@author: mendt
'''
import os
import unittest
import gdal
from gdal import GA_ReadOnly
from georeference.utils.process.tools import convertPostgisStringToList
from georeference.utils.process.tools import convertListToPostgisString
from georeference.utils.process.tools import extractSRIDFromDataset
from georeference.utils.process.tools import getBoundsFromDataset
from georeference.utils.process.tools import sortPolygonCoordinates

class ToolsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):   
        print '=============='
        print 'Start process modul tests ...'
        print '=============='
        
        cls.dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../test-data')
        cls.clip_raster = os.path.join(cls.dir,'test-mtb-georef.tif')

    def testGetBoundsFromDataset(self):
        dataset = gdal.Open( self.clip_raster, GA_ReadOnly)
        response = getBoundsFromDataset(dataset)

        print '====================='
        print 'Test if testGetBoundsFromDataset ...'
        print 'Response: %s'%response
        print '====================='

        self.assertTrue(len(response) == 4, 'Response has not expected form.')

        del dataset

    def testExtractSRIDFromDataset(self):
        dataset = gdal.Open( self.clip_raster, GA_ReadOnly)
        response = extractSRIDFromDataset(dataset)

        print '====================='
        print 'Test if testExtractSRIDFromDataset ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEquals(response, 'EPSG:4314', 'Response is not like expected.')

        del dataset

    def testConvertPostgisStringToList(self):
        response = convertPostgisStringToList('POLYGON((16.9999980926514 51.7999992370605,16.9999980926514 51.9000015258789,17.1666679382324 51.9000015258789,17.1666679382324 51.7999992370605,16.9999980926514 51.7999992370605))')

        print '====================='
        print 'Test if testConvertPostgisStringToList ...'
        print 'Response: %s'%response
        print '====================='

        self.assertTrue(len(response) == 5)

    def testConvertListToPostgisString(self):
        response = convertListToPostgisString([[16.9999980926514, 51.7999992370605], [16.9999980926514, 51.9000015258789],
                                               [17.1666679382324, 51.9000015258789], [17.1666679382324, 51.7999992370605],
                                               [16.9999980926514, 51.7999992370605]]
                                              , 'POLYGON')

        print '====================='
        print 'Test if testConvertListToPostgisString ...'
        print 'Response: %s'%response
        print '====================='

        self.assertTrue(isinstance(response,str))

    def testSortPolygonCoordinates(self):

        print '====================='
        print 'Test if testSortPolygonCoordinates ...'
        print '====================='

        wrongArray = [[11.499968348633589, 51.100006191711365], [11.500029766654176, 50.999996094228884],
                      [11.666697687046739, 51.09999838531544], [11.66663625943301, 51.000003906380776],
                      [11.499968348633589, 51.100006191711365]]
        correctArray = [[10.499998982954674, 51.70004323484564], [10.499999109696809, 51.599956002150265],
                        [10.666666921079132, 51.600041018367804], [10.666667048036956, 51.69995821875753],
                        [10.499998982954674, 51.70004323484564]]
        wrongArrayResponse = sortPolygonCoordinates(wrongArray)
        correctArrayResponse = sortPolygonCoordinates(correctArray)

        print wrongArrayResponse

        self.assertTrue(correctArray == correctArrayResponse, 'Response is not like expected')
        self.assertTrue(wrongArray != wrongArrayResponse, 'Response is not like expected')



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()