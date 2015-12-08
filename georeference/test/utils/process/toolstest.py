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
from georeference.utils.process.tools import getBoundsFromDataset
from georeference.utils.process.tools import extractSRIDFromDataset

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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()