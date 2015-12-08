# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 08.10.15

@author: mendt
'''
import os
import gdal
from gdal import GA_ReadOnly
from georeference.models.vkdb.map import Map
from georeference.utils.process.tools import getBoundsFromDataset
from georeference.test.basetestcase import BaseTestCase

class MapTest(BaseTestCase):


    @classmethod
    def setUpClass(cls):
        BaseTestCase.setUpClass()


        print '=============='
        print 'Start process module map tests ...'
        print '=============='

        cls.dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../test-data')
        cls.file = os.path.join(cls.dir,'test-mtb-georef.tif')

    def tearDown(self):
        self.dbsession.rollback()

    def testSetBoundingBox(self):
        mapObj = Map(id=1, georefimage=self.file)

        # check if response is correct
        dataset = gdal.Open( self.file, GA_ReadOnly)
        bounds = getBoundsFromDataset(dataset)
        polygon = "POLYGON((%(lx)s, %(ly)s, %(lx)s, %(uy)s, %(ux)s, %(uy)s, %(ux)s, %(ly)s, %(lx)s, %(ly)s))"% {
            "lx": bounds[0], "ly": bounds[1], "ux": bounds[2], "uy": bounds[3] }

        print polygon
        print self.file
        print getBoundsFromDataset(dataset)

    def testCreateMapObjWithBBox(self):
        geometry = "POLYGON((10.8333330154419 50.5,10.8333330154419 50.6000022888184,11.0000009536743 50.6000022888184,11.0000009536743 50.5,10.8333330154419 50.5))"
        mapObj = Map(id=1, boundingbox=geometry)
        self.dbsession.add(mapObj)
        self.dbsession.flush()
