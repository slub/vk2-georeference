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
import logging
from gdal import GA_ReadOnly
from PIL import Image
from numpy import ndarray

from georeference.utils.logger import createLogger
from georeference.utils.process.georeferencer import SRC_DICT_WKT
from georeference.utils.process.clipimage import clipImage
from georeference.utils.process.clipimage import resampleGeoreferencedImage
from georeference.utils.process.georeferencer import correctGCPOffset
from georeference.utils.process.georeferencer import maskImage
from georeference.utils.process.georeferencer import createGdalDataset
from georeference.utils.process.georeferencer import getOffsetValues
from georeference.utils.process.georeferencer import createVrt
from georeference.utils.process.georeferencer import georeference
from georeference.utils.process.georeferencer import createClipShapefile
from georeference.utils.process.georeferencer import transformClipPolygon
from georeference.utils.process.georeferencer import rectifyImageAffine
from georeference.utils.process.georeferencer import rectifyPolynom
from georeference.utils.process.georeferencer import rectifyPolynomWithVRT
from georeference.utils.process.georeferencer import rectifyTps
from georeference.utils.process.georeferencer import rectifyTpsWithVrt

class GeoreferencerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):   
        print '=============='
        print 'Start process modul tests ...'
        print '=============='
        
        cls.dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../test-data')
        
        # new test data 
        cls.testData = [
            (637, 652),
            (625, 7125),
            (7741, 7133),
            (7755, 668),
            (637, 652)
        ]
        cls.size = [8383, 9089]
        cls.testGcp = [
            gdal.GCP(9.99999904632568, 48.9000015258789, 0, 637, 652),
            gdal.GCP(9.99999904632568, 48.7999992370605, 0, 625, 7125),
            gdal.GCP(10.1666669845581, 48.7999992370605,0, 7741, 7133),
            gdal.GCP(10.1666669845581, 48.9000015258789, 0, 7755, 668)
        ]
        cls.bbox = [
            [9.99999904632568, 48.7999992370605],
            [9.99999904632568, 48.9000015258789],
            [10.1666669845581, 48.9000015258789],
            [10.1666669845581, 48.7999992370605],
            [9.99999904632568, 48.7999992370605]
        ]
        cls.file = os.path.join(cls.dir,'test-mtb.tif')   
        
        # old test data    
        cls.proj =  '+proj=longlat +ellps=bessel +datum=potsdam +no_defs'
        cls.logger = createLogger('GeoreferenceTest', logging.DEBUG)
        cls.testData1 = {
            'mtb': {
                'srcFile': os.path.join(cls.dir,'test-mtb.tif'),
                'gcps': [
                    gdal.GCP(9.999999047035397, 48.90000152653428, 0, 637, 652),
                    gdal.GCP(9.999999047069203, 48.79999923774097, 0, 625, 7125),
                    gdal.GCP(10.166666985288636, 48.79999923771421,0, 7741, 7133),
                    gdal.GCP(10.166666985254116, 48.90000152650738, 0, 7755, 668)
#                     gdal.GCP(10.109429790857027, 48.872275997293876, 0, 5274, 2654),
#                     gdal.GCP(10.097754297988152, 48.83477141386819, 0, 4724, 5086),
#                     gdal.GCP(10.137929188012347, 48.85194532840476, 0, 2434, 3808)
                ],
                'bbox': [
                    [9.999999047035397, 48.79999923774097],
                    [9.999999047035397, 48.90000152653428],
                    [10.166666985288636, 48.90000152653428],
                    [10.166666985288636, 48.79999923774097],
                    [9.999999047035397, 48.79999923774097]
                ],
                'clip': [
                    [637, 652],
                    [625, 7125],
                    [7741, 7133],
                    [7755, 668],
                    [637, 652]
                ],
                'srs': 4314
            }
        }
        cls.gcps = []
        cls.gcps.append(gdal.GCP(21.1666679382324, 55.7999992370605, 0, 7057,7348))
        cls.gcps.append(gdal.GCP(21.1666679382324, 55.9000015258789, 0, 7043,879))
        cls.gcps.append(gdal.GCP(20.9999980926514, 55.7999992370605, 0, 985,7331))
        cls.gcps.append(gdal.GCP(20.9999980926514, 55.9000015258789, 0, 969,869))
        cls.boundingbox = [[20.9999980926514,55.7999992370605],[20.9999980926514,55.9000015258789],
                           [21.1666679382324,55.9000015258789],[21.1666679382324,55.7999992370605],
                           [20.9999980926514,55.7999992370605]]

    #@unittest.skip("testCreateVrt")
    def testCreateVrt(self):
        dst_path = os.path.join(self.dir, 'test_createVrt.vrt')
        dataset = gdal.Open(self.file, GA_ReadOnly)
        response = createVrt(dataset, dst_path)

        print '====================='
        print 'Test if createVrt ...'
        print 'Response: %s'%response
        print '====================='
        
        self.assertTrue(os.path.exists(dst_path), 'Could not find created vrt file')
        self.assertTrue(isinstance(response, gdal.Dataset), 'Response is not of type gdal.Dataset')
        
        # clear up
        del dataset
        if os.path.exists(dst_path):
            os.remove(dst_path)
            
    #@unittest.skip("testClipImage")
    def testClipImage(self):
        destPath = os.path.join(self.dir, 'test-clipped-image.tif')
        response = clipImage(self.file, destPath, self.testData)
        
        print '====================='
        print 'Test if testClipImage ...'
        print 'Response: %s'%response
        print '====================='
        
        self.assertTrue(os.path.exists(destPath), 'Could not find created tiff file')
        
        # clear up
        if os.path.exists(destPath):
            os.remove(destPath)

    #@unittest.skip("testMaskImage")
    def testMaskImage(self):
        image = Image.open(self.file)
        response = maskImage(image, self.testData)
        
        print '====================='
        print 'Test if testMaskImage ...'
        print 'Response: %s'%response
        print '====================='
        
        self.assertTrue(isinstance(response, ndarray), 'Response is not of type list')
    
    #@unittest.skip("testGetOffsetValues")
    def testGetOffsetValues(self):
        response = getOffsetValues(self.testData, Image.open(self.file))
        
        print '====================='
        print 'Test if testGetOffsetValues ...'
        print 'Response: %s'%response
        print '====================='
        
        self.assertTrue(isinstance(response, dict), 'Response is not of type dictionary')
        self.assertTrue('top' in response, 'Missing key in response')
        self.assertTrue('left' in response, 'Missing key in response')
        self.assertTrue('right' in response, 'Missing key in response')
        self.assertTrue('bottom' in response, 'Missing key in response')
        
    #@unittest.skip("testCreateGdalMemDataset")
    def testCreateGdalMemDataset(self):
        image = Image.open(self.file)
        ndarray = maskImage(image, self.testData)
        driver = gdal.GetDriverByName("MEM")
        if driver is None:
            raise ValueError("Can't find MEM Driver")
        
        response = createGdalDataset(image, ndarray, driver)
         
        print '====================='
        print 'Test if testCreateGdalMemDataset ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertTrue(isinstance(response, gdal.Dataset), 'Response is not of type gdal dataset')
        self.assertEqual(response.RasterXSize, 8382, 'Response dataset has not expected x size.')
        self.assertEqual(response.RasterYSize, 9089, 'Response dataset has not expected y size.')
        self.assertEqual(response.RasterCount, 4, 'Response dataset has not expected band count.')
        
        #response.FlushCache() 
        # clear up
        del response
        del image
        del ndarray
            
    #@unittest.skip("testCreateGdalGeoTiffDataset")
    def testCreateGdalGeoTiffDataset(self):
        destPath = os.path.join(self.dir, 'test-create-gdal-dataset.tif')
        image = Image.open(self.file)
        ndarray = maskImage(image, self.testData)
        offset = getOffsetValues(self.testData, image)
        driver = gdal.GetDriverByName("GTiff")
        if driver is None:
            raise ValueError("Can't find GeoTiff Driver")
        
        response = createGdalDataset(image, ndarray, driver, offset, destPath)
         
        print '====================='
        print 'Test if testCreateGdalGeoTiffDataset ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertTrue(isinstance(response, gdal.Dataset), 'Response is not of type gdal dataset')
        self.assertEqual(response.RasterXSize, 7130, 'Response dataset has not expected x size.')
        self.assertEqual(response.RasterYSize, 6481, 'Response dataset has not expected y size.')
        self.assertEqual(response.RasterCount, 4, 'Response dataset has not expected band count.')
        
        #response.FlushCache() 
        # clear up
        del image
        del ndarray
        del response
        if os.path.exists(destPath):
            os.remove(destPath)
    
    #@unittest.skip("testCreateGdalGeoTiffDatasetGeoreferenced")
    def testCreateGdalGeoTiffDatasetGeoreferenced(self):
        destPath = os.path.join(self.dir, 'test-create-gdal-dataset-georeferenced.tif')
        destPath2 = os.path.join(self.dir, 'test-create-gdal-dataset-georeferenced2.tif')

        image = Image.open(self.file)
        
        ndarray = maskImage(image, self.testData)
        offset = getOffsetValues(self.testData, image)
        driver = gdal.GetDriverByName("GTiff")
        if driver is None:
            raise ValueError("Can't find GeoTiff Driver")
        
        response = createGdalDataset(image, ndarray, driver, None, destPath)
        response1 = createGdalDataset(image, ndarray, driver, offset, destPath2)
        
        print '====================='
        print 'Test if testCreateGdalGeoTiffDataset ...'
        print 'Response: %s'%response
        print '====================='
         
        
        geoTransform = gdal.GCPsToGeoTransform(self.testGcp)
        geoTransform1 = gdal.GCPsToGeoTransform(correctGCPOffset(self.testGcp, offset))
        geoProj = SRC_DICT_WKT[4314]
        response.SetProjection(geoProj)
        response.SetGeoTransform(geoTransform)
        response1.SetProjection(geoProj)
        response1.SetGeoTransform(geoTransform1)        
        response.FlushCache() 
        response1.FlushCache()
        # clear up
        del image
        del ndarray
        del response
        del response1
        
        # create vrt
        dst_path = os.path.join(self.dir, 'test_createVrt.vrt')
        dataset = gdal.Open(self.file, GA_ReadOnly)
        vrt = createVrt(dataset, dst_path)
        vrt.SetProjection(geoProj)
        vrt.SetGeoTransform(geoTransform)
        vrt.FlushCache()
        del vrt
        
        # create georef classic
        dst_path2 = os.path.join(self.dir, 'test-mtb-georef.tif')
        logger = createLogger('GeoreferenceTest', logging.DEBUG)
        georeference(self.file, dst_path2, self.dir, 
                geoTransform, 4314, 'polynom', logger)
#         if os.path.exists(destPath):
#             os.remove(destPath)

        # create georef clipped 
        dst_path3 = os.path.join(self.dir, 'test-mtb-georef-clipped.tif')
        clipPath = createClipShapefile(self.bbox, os.path.join(self.dir, 'test_shp'), 4314)
        response = georeference(self.file, dst_path3, self.dir, 
                                geoTransform, 4314, 'polynom', logger, clipPath)
        
    #@unittest.skip("testCreateGdalGeoTiffDatasetGeoreferencedSimple")
    def testCreateGdalGeoTiffDatasetGeoreferencedSimple(self):
        destPath = os.path.join(self.dir, 'test-create-gdal-dataset-georeferenced-simple.tif')

        image = Image.open(self.file)
        
        ndarray = maskImage(image, self.testData)
        offset = getOffsetValues(self.testData, image)
        driver = gdal.GetDriverByName("GTiff")
        if driver is None:
            raise ValueError("Can't find GeoTiff Driver")
        
        response = createGdalDataset(image, ndarray, driver, offset, destPath)
        
        print '====================='
        print 'Test if testCreateGdalGeoTiffDatasetGeoreferencedSimple ...'
        print 'Response: %s'%response
        print '====================='
         
        geoTransform = gdal.GCPsToGeoTransform(correctGCPOffset(self.testGcp, offset))
        geoProj = SRC_DICT_WKT[4314]
        response.SetProjection(geoProj)
        response.SetGeoTransform(geoTransform)
        response.SetProjection(geoProj)    
        response.FlushCache() 
        
        # clear up
        del image
        del ndarray
        del response
        if os.path.exists(destPath):
            os.remove(destPath)
            
    #@unittest.skip("testRectifyImageAffine")
    def testRectifyImageAffine(self):
        destPath = os.path.join(self.dir, 'test-rectifyImage.tif')
        response = rectifyImageAffine(self.file, destPath, self.testData, self.testGcp, 4314, self.logger)
        
        print '====================='
        print 'Test if testRectifyImageAffine ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)
        
        if os.path.exists(destPath):
            os.remove(destPath)

    def testRectifyImageAffineWithEmptyClip(self):
        destPath = os.path.join(self.dir, 'test-rectifyImageWithOutClip.tif')
        response = rectifyImageAffine(self.file, destPath, [], self.testGcp, 4314, self.logger)

        print '====================='
        print 'Test if testRectifyImageAffineWithEmptyClip ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        if os.path.exists(destPath):
            os.remove(destPath)

        
    #@unittest.skip("testResampleGeoreferencedImageSimple")
    def testResampleGeoreferencedImageSimple(self):
        destPath = os.path.join(self.dir, 'test-create-gdal-dataset-resample-simple.tif')
        image = Image.open(self.file)
        ndarray = maskImage(image, self.testData)
        offset = getOffsetValues(self.testData, image)
        driver = gdal.GetDriverByName("MEM")
        if driver is None:
            raise ValueError("Can't find Mem Driver")
        srcDataset = createGdalDataset(image, ndarray, driver, offset)

        
        outputDriver = gdal.GetDriverByName('GTiff')
        if outputDriver is None: 
            raise ValueError("Can't find GTiff Driver")
        
        geoTransform = gdal.GCPsToGeoTransform(correctGCPOffset(self.testGcp, offset))
        geoProj = SRC_DICT_WKT[4314]
        srcDataset.SetProjection(geoProj)
        srcDataset.SetGeoTransform(geoTransform)
        response = resampleGeoreferencedImage(srcDataset, geoTransform, geoProj, outputDriver, destPath)
        
        print '====================='
        print 'Test if testResampleGeoreferencedImageSimple ...'
        print 'Response: %s'%response
        print '====================='
        
        response.FlushCache() 
        
        self.assertTrue(isinstance(response, gdal.Dataset), "Response is not a gdal.Dataset.")
        
        # clear up
        del image
        del ndarray
        del response
        if os.path.exists(destPath):
            os.remove(destPath)
    
    #@unittest.skip("testTransformClipPolygon")   
    def testTransformClipPolygon(self):
        geoTransform = gdal.GCPsToGeoTransform(self.testData1['mtb']['gcps'])
        response = transformClipPolygon(self.testData1['mtb']['clip'], geoTransform)
        
        print '====================='
        print 'Test if testTransformClipPolygon ...'
        print 'Response: %s'%response
        print '====================='

        self.assertTrue(isinstance(response, list), 'Response is not of type list ...')
            
    #@unittest.skip("testGeoreference")   
    def testGeoreferenceMtbWithoutClip(self):
        dstPath = os.path.join(self.dir, 'mtb-georef-withoutclip.tif')
        geoTransform = gdal.GCPsToGeoTransform(self.testData1['mtb']['gcps'])
        response = georeference(self.testData1['mtb']['srcFile'], dstPath, self.dir, 
                                geoTransform, self.testData1['mtb']['srs'], 'polynom', self.logger)
        
        print '====================='
        print 'Test if testGeoreferenceMtb ...'
        print 'Response: %s'%response
        print '====================='

        self.assertTrue(os.path.exists(dstPath), 'Could not find created vrt file ...')
        self.assertEqual(response, dstPath, 'Response is not like expected ...')
        
        responseDataset = gdal.Open(response, GA_ReadOnly)
        self.assertTrue(responseDataset.GetProjection() == 'GEOGCS["DHDN",DATUM["Deutsches_Hauptdreiecksnetz",SPHEROID["Bessel 1841",6377397.155,299.1528128000008,AUTHORITY["EPSG","7004"]],TOWGS84[598.1,73.7,418.2,0.202,0.045,-2.455,6.7],AUTHORITY["EPSG","6314"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4314"]]', 'Response has not expected coordinate system ...')
         
        # clear up
        del responseDataset
        if os.path.exists(dstPath):
            os.remove(dstPath)

    #@unittest.skip("testGeoreferenceMtbWithClip")   
    def testGeoreferenceMtbWithClip(self):
        dstPath = os.path.join(self.dir, 'mtb-georef-clipped.tif')
        geoTransform = gdal.GCPsToGeoTransform(self.testData1['mtb']['gcps'])
        clipPath = createClipShapefile(self.testData1['mtb']['bbox'], os.path.join(self.dir, 'test_shp'), self.testData1['mtb']['srs'])
        response = georeference(self.testData1['mtb']['srcFile'], dstPath, self.dir, 
                                geoTransform, self.testData1['mtb']['srs'], 'polynom', self.logger, clipPath)
        
        print '====================='
        print 'Test if testGeoreferenceMtb ...'
        print 'Response: %s'%response
        print '====================='

        self.assertTrue(os.path.exists(dstPath), 'Could not find created vrt file ...')
        self.assertEqual(response, dstPath, 'Response is not like expected ...')
                    
        responseDataset = gdal.Open(response, GA_ReadOnly)
        self.assertTrue(responseDataset.GetProjection() == 'GEOGCS["DHDN",DATUM["Deutsches_Hauptdreiecksnetz",SPHEROID["Bessel 1841",6377397.155,299.1528128000008,AUTHORITY["EPSG","7004"]],TOWGS84[598.1,73.7,418.2,0.202,0.045,-2.455,6.7],AUTHORITY["EPSG","6314"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4314"]]', 'Response has not expected coordinate system ...')
         
        # clear up
        del responseDataset
        if os.path.exists(dstPath):
            os.remove(dstPath)
        if os.path.exists(clipPath):
            os.remove('%s.shp'%os.path.join(self.dir, 'test_shp'))
            os.remove('%s.dbf'%os.path.join(self.dir, 'test_shp'))
            os.remove('%s.prj'%os.path.join(self.dir, 'test_shp'))
            os.remove('%s.shx'%os.path.join(self.dir, 'test_shp'))
                
    #@unittest.skip("testCreateClipShapefile")
    def testCreateClipShapefile(self):
        dst_path = os.path.join(self.dir, 'test_shapefile')
        response = createClipShapefile(self.boundingbox, dst_path, 4314)
        
        print '====================='
        print 'Test if testCreateClipShapefile ...'
        print 'Response: %s'%response
        print '====================='
        
        self.assertTrue('%s.shp'%dst_path == response, 'Response is not like expected ...')

        # clean up 
        if os.path.exists('%s.shp'%dst_path):
            os.remove('%s.shp'%dst_path)
            os.remove('%s.dbf'%dst_path)
            os.remove('%s.prj'%dst_path)
            os.remove('%s.shx'%dst_path)
            
    #@unittest.skip("testRectifyImageAffineForAK")
    def testRectifyImageAffineForAK(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-affine.tif')
        file = os.path.join(self.dir,'test-ak.jpg')  
        clip = [(2327, 2118), (9214, 2099), (9195, 7235), (2297, 7234), (2327, 2118)]
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyImageAffine(file, destPath, clip, gcps, srs, self.logger)
        
        print '====================='
        print 'Test if testRectifyImageForAK  ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)
        
        if os.path.exists(destPath):
            os.remove(destPath)

    #@unittest.skip("testRectifyImageAffineForAK")
    def testRectifyImageAffineForAKWithoutClop(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-affine.tif')
        file = os.path.join(self.dir,'test-ak.jpg')
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyImageAffine(file, destPath, [], gcps, srs, self.logger)

        print '====================='
        print 'Test if testRectifyImageForAK  ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        if os.path.exists(destPath):
            os.remove(destPath)

    #@unittest.skip("testRectifyImagePolynom1ForMtb")
    def testRectifyImagePolynom1ForMtb(self):
        destPath = os.path.join(self.dir, 'test-mtb-rectified-polynom1.tif')
        response = rectifyPolynom(self.file, destPath, self.testData, self.testGcp, 4314, self.logger, self.dir, None, order=1)
        
        print '====================='
        print 'Test if testRectifyImagePolynom1ForMtb  ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)
        
        if os.path.exists(destPath):
            os.remove(destPath)  
           
    #@unittest.skip("testRectifyImagePolynom1ForAK")
    def testRectifyImagePolynom1ForAK(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-polynom1.tif')
        file = os.path.join(self.dir,'test-ak.jpg')  
        clip = [(2327, 2118), (9214, 2099), (9195, 7235), (2297, 7234), (2327, 2118)]
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyPolynom(file, destPath, clip, gcps, srs, self.logger, self.dir, None, order=1)
        
        print '====================='
        print 'Test if testRectifyImagePolynom1ForAK  ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)
        
        if os.path.exists(destPath):
            os.remove(destPath)

    #@unittest.skip("testRectifyImagePolynom1ForAKWithoutClip")
    def testRectifyImagePolynom1ForAKWithoutClip(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-polynom1-withoutclip.tif')
        file = os.path.join(self.dir,'test-ak.jpg')
        clip = []
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyPolynom(file, destPath, clip, gcps, srs, self.logger, self.dir, None, order=1)

        print '====================='
        print 'Test if testRectifyImagePolynom1ForAKWithoutClip  ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        # if os.path.exists(destPath):
        #     os.remove(destPath)

    #@unittest.skip("testRectifyPolynomWithVRTForAKWithoutClip")
    def testRectifyPolynomWithVRTForAKWithoutClip(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-polynom1-withoutclip-vrt.tif')
        file = os.path.join(self.dir,'test-ak.jpg')
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyPolynomWithVRT(file, destPath, gcps, srs, self.logger, self.dir, None, order=1)

        print '====================='
        print 'Test if testRectifyPolynomWithVRTForAKWithoutClip  ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        # if os.path.exists(destPath):
        #     os.remove(destPath)

    #@unittest.skip("testRectifyImagePolynom2ForAK")   
    def testRectifyImagePolynom2ForAK(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-polynom2.tif')
        file = os.path.join(self.dir,'test-ak.jpg')  
        clip = [(2327, 2118), (9214, 2099), (9195, 7235), (2297, 7234), (2327, 2118)]
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyPolynom(file, destPath, clip, gcps, srs, self.logger, self.dir, None, order=2)
        
        print '====================='
        print 'Test if testRectifyImagePolynom2ForAK  ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)
        
#         if os.path.exists(destPath):
#             os.remove(destPath)  
    
    #@unittest.skip("testRectifyImagePolynom3ForAK")   
    def testRectifyImagePolynom3ForAK(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-polynom3.tif')
        file = os.path.join(self.dir,'test-ak.jpg')  
        clip = [(2327, 2118), (9214, 2099), (9195, 7235), (2297, 7234), (2327, 2118)]
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyPolynom(file, destPath, clip, gcps, srs, self.logger, self.dir, None, order=3)
        
        print '====================='
        print 'Test if testRectifyImagePolynom3ForAK  ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

#         if os.path.exists(destPath):
#             os.remove(destPath)  
            
    #@unittest.skip("testRectifyImageTpsForAK")   
    def testRectifyImageTpsForAK(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-tps.tif')
        file = os.path.join(self.dir,'test-ak.jpg')  
        clip = [(2327, 2118), (9214, 2099), (9195, 7235), (2297, 7234), (2327, 2118)]
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyTps(file, destPath, clip, gcps, srs, self.logger, self.dir)
        
        print '====================='
        print 'Test if testRectifyImageTpsForAK  ...'
        print 'Response: %s'%response
        print '====================='
         
        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        # if os.path.exists(destPath):
        #     os.remove(destPath)

    #@unittest.skip("testRectifyImageTpsForAKWithoutClip")
    def testRectifyImageTpsForAKWithoutClip(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-tps-withoutclip.tif')
        file = os.path.join(self.dir,'test-ak.jpg')
        clip = []
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyTps(file, destPath, clip, gcps, srs, self.logger, self.dir)

        print '====================='
        print 'Test if testRectifyImageTpsForAKWithoutClip  ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        # if os.path.exists(destPath):
        #     os.remove(destPath)

    #@unittest.skip("testRectifyTpsWithVrtForAKWithoutClip")
    def testRectifyTpsWithVrtForAKWithoutClip(self):
        destPath = os.path.join(self.dir, 'test-ak-rectified-tps-withoutclip-vrt.tif')
        file = os.path.join(self.dir,'test-ak.jpg')
        srs = 4314
        gcps = [
            gdal.GCP(13.322571166912697, 50.869534359847236, 0, 5473, 6079),
            gdal.GCP(13.346566162286086, 50.91926655702792, 0, 5670, 5589),
            gdal.GCP(13.53735995082988, 50.802610870942374, 0, 7020, 6807),
            gdal.GCP(13.667546305614797, 50.89755275702876, 0, 7812, 5913),
            gdal.GCP(13.741126714401176, 51.05625639529854, 0, 8338, 4161),
            gdal.GCP(13.681169234684086, 51.1685499300691, 0, 7942, 2791),
            gdal.GCP(13.47756543137287, 51.16569220735402, 0, 6609, 2882),
            gdal.GCP(13.300067220165836, 51.06061124738151, 0, 5102, 4096),
            gdal.GCP(13.310932518222272, 51.19680951127774, 0, 5295, 2447),
            gdal.GCP(12.921352950966174, 50.83419856543994, 0, 2536, 6561),
            gdal.GCP(12.983108161200633, 50.984707383627985, 0, 3048, 5009),
            gdal.GCP(12.973153769483801, 51.099562229978154, 0, 3091, 3676),
            gdal.GCP(13.119775225375355, 51.12445831286638, 0, 4017, 3228),
            gdal.GCP(13.124513229340627, 50.97154471762153, 0, 4037, 4961),
        ]
        response = rectifyTpsWithVrt(file, destPath, gcps, srs, self.logger, self.dir)

        print '====================='
        print 'Test if testRectifyTpsWithVrtForAKWithoutClip  ...'
        print 'Response: %s'%response
        print '====================='

        self.assertEqual(response, destPath, "Response is not equal to %s"%destPath)

        # if os.path.exists(destPath):
        #     os.remove(destPath)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()