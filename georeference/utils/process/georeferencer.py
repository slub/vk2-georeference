# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import os
import uuid
import sys
import subprocess
import shapefile
import numpy
import gdal
from PIL import Image
from PIL import ImageDraw
from gdalconst import GDT_Byte
from gdalconst import GA_ReadOnly
from georeference.settings import SRC_DICT_WKT
from georeference.utils.exceptions import ClipException
from georeference.utils.exceptions import CreateGCPException
from georeference.utils.exceptions import AddOverviewException

gdal.UseExceptions()

# SRS_DICT_PROJ = {
#     4314:'+proj=longlat +ellps=bessel +datum=potsdam +no_defs'
# }

def addOverviews(dstFile, overviewLevels, logger):
    """ Function adds overview to given geotiff.

    :type dstFile: str
    :type overviewLevels: str
    :type logger: logging.Logger
    :return: str
    :raise: vkviewer.python.georef.georeferenceexceptions.AddOverviewException """
    try:
        logger.debug('Adding overviews to raster %s'%dstFile)
        command = "gdaladdo --config GDAL_CACHEMAX 500 -r average %s %s"%(dstFile,overviewLevels)
        subprocess.check_call(command, shell=True)
        return dstFile
    except:
        logger.error("%s - Unexpected error while trying add overviews to the raster: %s - with command - %s"%(sys.stderr,sys.exc_info()[0],command))
        raise AddOverviewException("Error while running subprocess via commandline!")

def correctGCPOffset(gcps, offset):
    """ Function corrects the gcp so that the offset is recognized.

    :type gcps: List<gdal.GCP>
    :type offset: dict<string, integer>
    :return: List<gdal.GCP> """
    response = []
    for gcp in gcps:
        gdal.GCP(9.99999904632568, 48.9000015258789, 0, 637, 652)
        response.append(gdal.GCP(gcp.GCPX, gcp.GCPY, gcp.GCPZ, gcp.GCPPixel - offset['left'], gcp.GCPLine - offset['top']))
    return response

def createClipShapefile(polyCoords, dstFile, srs):
    """ Function creates a shapefile with one single clip polygon

    :type polyCoords: List<List<Float>>
    :type dstFile: str
    :type srs: int
    :return: str """
    # make sure the destination path is not given as absolute shapefile name
    if '.' in os.path.basename(dstFile):
        dstFile = str(dstFile).split('.')[0]

    # create the shapefile
    shpWriter = shapefile.Writer(shapefile.POLYGON)
    shpWriter.poly(parts=[polyCoords])
    shpWriter.field('epsg', 'C', '6')
    shpWriter.record(str(srs))
    shpWriter.save(dstFile)

    # create the PRJ file
    prj = open("%s.prj"%dstFile, "w")
    epsg = SRC_DICT_WKT[srs]
    prj.write(epsg)
    prj.close()

    return '%s.shp'%dstFile

def createGCPs(clipParams, georefCoords, imgHeight):
    """ For a given list of gcps coordinates it creates a list of gdal GCPS.

    :type clipParams: List.<str>
    :type georefCoords: List.<List.<Float>>
    :type imgHeight: int
    :return: List.<gdal.GCP>
    :raise: vkviewer.python.georef.georeferenceexceptions.CreateGCPException """
    try:
        # at first parse pixel coords
        pixels = []
        for point in clipParams.split(","):
            x, y = point.split(":")
            # recalculate the y coordinates because of different coordinates origin
            pixels.append((round(float(x)),imgHeight - round(float(y))))

        # order the list
        xList = []
        yList = []
        for tuple in pixels:
            xList.append(tuple[0])
            yList.append(tuple[1])
        xList.sort()
        yList.sort()
        orderedList = [0, 0, 0, 0]
        for tuple in pixels:
            if (tuple[0] == xList[0] or tuple[0] == xList[1]) and \
                (tuple[1] == yList[2] or tuple[1] == yList[3]):
                orderedList[0] = tuple
            elif (tuple[0] == xList[0] or tuple[0] == xList[1]) and \
                (tuple[1] == yList[0] or tuple[1] == yList[1]):
                orderedList[1] = tuple
            elif (tuple[0] == xList[2] or tuple[0] == xList[3]) and \
                (tuple[1] == yList[0] or tuple[1] == yList[1]):
                orderedList[2] = tuple
            elif (tuple[0] == xList[2] or tuple[0] == xList[3]) and \
                (tuple[1] == yList[2] or tuple[1] == yList[3]):
                orderedList[3] = tuple

        # run the matching
        gcps = []
        for i in range(0,len(orderedList)):
            gcps.append(gdal.GCP(georefCoords[i][0], georefCoords[i][1], 0, orderedList[i][0],orderedList[i][1]))
        return gcps
    except:
        raise CreateGCPException('Error while trying to create the GCPs')


def createGdalDataset(srcImage, imageArray, driver, offset=None, dstFile=None):
    """ Function creates a gdal raster dataset.

    :type srcImage: PIL.Image.Image
    :type imageArray: numpy.ndarray
    :type driver: gdal.Driver
    :type offset: dict<string, integer>|None (default = None)
    :type dstFile: str|None (default = None)
    :return: gdal.Dataset """
    xSize = srcImage.size[0] if offset is None else srcImage.size[0] - offset['left'] - offset['right']
    ySize = srcImage.size[1] if offset is None else srcImage.size[1] - offset['top'] - offset['bottom']
    outputPath = dstFile if dstFile else ''
    outputDataset = driver.Create(outputPath, int(xSize), int(ySize), 4, GDT_Byte)

    # write band data to dataset
    for band in range(0,4):
        if offset:
            outputDataset.GetRasterBand(band+1).WriteArray(imageArray[offset['top']:imageArray.shape[0]-offset['bottom'],
                                                                      offset['left']:imageArray.shape[1]-offset['right'],band])
        else:
            outputDataset.GetRasterBand(band+1).WriteArray(imageArray[:imageArray.shape[0],:imageArray.shape[1],band])

    return outputDataset

def createGeotiff(srcImage, ndarray, offset, dstFile, logger):
    """ Function creates a geotiff for a given image file. Does not fully write the image data out of the cache.
        For this dataset.FlushCache() has to be called.

    :type srcImage: PIL.Image.Image
    :type numpy.ndarray: ndarray
    :type offset: dict
    :type dstFile: str
    :type logger: logging.Logger
    :return: osgeo.gdal.Dataset
    :raise: ValueError """
    logger.debug('Create temporary geotiff ...')
    driver = gdal.GetDriverByName("GTiff")
    if driver is None:
        raise ValueError("Can't find GeoTiff Driver")
    newDataset = createGdalDataset(srcImage, ndarray, driver, offset, dstFile)
    return newDataset



def createVrt(srcDataset, dstFile):
    """ This functions creates a vrt for a corresponding, from gdal supported, source dataset.

    :type srcDataset: osgeo.gdal.Dataset
    :type dstFile: str
    :return: str """
    outputFormat = 'VRT'
    dstDriver = gdal.GetDriverByName(outputFormat)
    dstDataset = dstDriver.CreateCopy(dstFile, srcDataset,0)
    return dstDataset

def getOffsetValues(polygon, srcImage):
    """ Function calculates the offset values for a given clip polygon. Low and high are regarding the
    display coordinates system.

    :type polygon: List.<Tuple.<Integer>>
    :type srcImage: PIL.Image.Image
    :return: dict """
    lowX = 1000000
    lowY = 1000000
    highX = 0
    highY = 0
    size = [srcImage.size[0], srcImage.size[1]]

    for tuple in polygon:
        if tuple[0] < lowX:
            lowX = tuple[0]
        if tuple[0] > highX:
            highX = tuple[0]

        if tuple[1] < lowY:
            lowY = tuple[1]
        if tuple[1] > highY:
            highY = tuple[1]

    response = {
        'top': lowY,
        'left': lowX,
        'bottom': size[1] - highY,
        'right': size[0] - highX
    }
    return response

def georeference(srcFile, dstFile, tmpDir, geoTransform, srs, algorithm, logger, clip_shp = None):
    """ This function georeference an unrectified image to a georeferenced image.

    :deprecated: Do not use this function anymore -- Alternative: The function could handle for the persistent calculation of georeference results.

    :type srcFile: str
    :type dstFile: str
    :type tmpDir: str
    :type geoTransform: Tuple<Float>
    :type srs: str
    :type algorithm: str
    :type logger: logging.Logger
    :type clipShp: str|None (Default = None)
    :return: str """
    try:
        vrt_dataset = None
        dest_dataset = None
        shp_file = None

        logger.info('Run georeferencing of %s'%srcFile)
        src_dataset = gdal.Open(srcFile, GA_ReadOnly)
        vrt_file = os.path.join(tmpDir, '%s.vrt'%uuid.uuid4())
        vrt_dataset = createVrt(src_dataset, vrt_file)
        logger.debug('Set source projection of the vrt ...')
        vrt_dataset.SetProjection(SRC_DICT_WKT[srs])
        vrt_dataset.SetGeoTransform(geoTransform)

        if clip_shp:
            vrt_dataset = None
            logger.debug('Crop result to given shapefile geometry')
            return clipRasterWithShapfile(vrt_file, dstFile, clip_shp, logger)
        else:
            logger.debug('Create response without clipping ...')
            dest_dataset = src_dataset.GetDriver().CreateCopy(dstFile, vrt_dataset, 0)
            return dstFile
    except:
        pass
    finally:
        if vrt_dataset or vrt_file:
            del vrt_dataset
            os.remove(vrt_file)
        if dest_dataset:
            del dest_dataset
        if shp_file:
            os.remove('%s.shp'%shp_file)
            os.remove('%s.dbf'%shp_file)
            os.remove('%s.prj'%shp_file)
            os.remove('%s.shx'%shp_file)

def maskImage(srcImage, polygon):
    """ Function clips a image based on a polygon.

    :type srcImage: PIL.Image.Image
    :type polygon: List.<List.<int>>
    :return: numpy.ndarray """

    # add alpha (transparency)
    im = srcImage.convert("RGBA")

    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)

    # create mask
    # polygon = [(637, 652),(625, 7125),(7741, 7133),(7755, 668),(637, 652)]
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    if len(polygon) == 0:
        polygon = [(0,0), (imArray.shape[1], 0),(imArray.shape[1], imArray.shape[0]), (0, imArray.shape[0]), (0,0)]
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]

    # transparency (4th column)
    newImArray[:,:,3] = mask*255

    return newImArray

def rectifyImageAffine(srcFile, dstFile, clipPolygon, gcps, srs, logger):
    """ Functions generates clips an image and adds a geotransformation matrix to it

    :type srcFile: str
    :type dstFile: str
    :type clipPolygon: List.<Tuple.<int>>
    :type gcps: List.<gdal.GCP>
    :type srs: int Right now the function only supports 4314 as spatial reference system
    :type logger: logging.logger
    :return: str
    :raise: ValueError """
    logger.debug('Open image ...')
    srcImage = Image.open(srcFile)

    logger.debug('Clip image ...')
    ndarray = maskImage(srcImage, clipPolygon)

    logger.debug('Calculate offset ...')
    offset = {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}
    if len(clipPolygon) > 0:
        offset = getOffsetValues(clipPolygon, srcImage)

    # create an output geotiff
    newDataset = createGeotiff(srcImage, ndarray, offset, dstFile, logger)

    logger.debug('Do georeferencing based on an affine transformation ...')
    geoTransform = gdal.GCPsToGeoTransform(correctGCPOffset(gcps, offset))
    geoProj = SRC_DICT_WKT[srs]
    if geoProj is None:
        raise ValueError("SRS with id - %s - is not supported"%srs)
    newDataset.SetProjection(geoProj)
    newDataset.SetGeoTransform(geoTransform)
    newDataset.FlushCache()

    # clear up
    del srcImage
    del newDataset
    del ndarray

    return dstFile

def rectifyPolynom(srcFile, dstFile, clipPolygon, gcps, srs, logger, tmpDir, order=None):
    """ Functions generates clips an image and adds a geotransformation matrix to it

    :type srcFile: str
    :type dstFile: str
    :type clipPolygon: List.<Tuple.<int>>
    :type gcps: List.<gdal.GCP>
    :type srs: int Right now the function only supports 4314 as spatial reference system
    :type logger: logging.logger
    :type tmpDir: str
    :type order: int (Default None)
    :return: str
    :raise: ValueError """
    tmpFile = None
    try:
        # define tmp file path
        tmpDataName = uuid.uuid4()
        tmpFile = os.path.join(tmpDir, '%s.tif'%tmpDataName)

        logger.debug('Open image ...')
        srcImage = Image.open(srcFile)

        logger.debug('Clip image ...')
        ndarray = maskImage(srcImage, clipPolygon)

        logger.debug('Calculate offset ...')
        offset = getOffsetValues(clipPolygon, srcImage)

        # create an output geotiff
        newDataset = createGeotiff(srcImage, ndarray, offset, tmpFile, logger)

        logger.debug('Add gcps to image')
        geoProj = SRC_DICT_WKT[srs]
        if geoProj is None:
            raise ValueError("SRS with id - %s - is not supported"%srs)
        newDataset.SetGCPs(correctGCPOffset(gcps, offset), geoProj)
        newDataset.FlushCache()

        # memory stuff
        del srcImage
        del ndarray
        del newDataset

        # doing the rectification
        if os.path.exists(tmpFile):
            # doing a rectification of an image using a polynomial transformation
            # and a nearest neighbor resampling method
            logger.debug('Do georeferencing based on an polynom transformation ...')
            resampling = 'near'
            if order is None:
                command = 'gdalwarp -overwrite --config GDAL_CACHEMAX 500 -r %s -wm 500 %s %s'%(resampling, tmpFile, dstFile)
            else:
                ord = order if order in [1,2,3] else 1
                command = 'gdalwarp -overwrite --config GDAL_CACHEMAX 500 -r %s -order %s -wm 500 %s %s'%(resampling, ord, tmpFile, dstFile)
            subprocess.check_call(command, shell=True)
        return dstFile
    except:
        raise
    finally:
        if os.path.exists(tmpFile):
            os.remove(tmpFile)

def rectifyTps(srcFile, dstFile, clipPolygon, gcps, srs, logger, tmpDir):
    """ Functions generates clips an image and adds a geotransformation matrix to it

    :type srcFile: str
    :type dstFile: str
    :type clipPolygon: List.<Tuple.<int>>
    :type gcps: List.<gdal.GCP>
    :type srs: int Right now the function only supports 4314 as spatial reference system
    :type logger: logging.logger
    :type tmpDir: str
    :return: str
    :raise: ValueError """
    tmpFile = None
    try:
        # define tmp file path
        tmpDataName = uuid.uuid4()
        tmpFile = os.path.join(tmpDir, '%s.tif'%tmpDataName)

        # open image
        logger.debug('Open image ...')
        srcImage = Image.open(srcFile)

        logger.debug('Clip image ...')
        ndarray = maskImage(srcImage, clipPolygon)

        logger.debug('Calculate offset ...')
        offset = getOffsetValues(clipPolygon, srcImage)

        # create an output geotiff
        newDataset = createGeotiff(srcImage, ndarray, offset, tmpFile, logger)

        logger.debug('Add gcps to image ...')
        geoProj = SRC_DICT_WKT[srs]
        if geoProj is None:
            raise ValueError("SRS with id - %s - is not supported"%srs)
        newDataset.SetGCPs(correctGCPOffset(gcps, offset), geoProj)
        newDataset.FlushCache()

        # memory stuff
        del srcImage
        del ndarray
        del newDataset

        # doing the rectification
        if os.path.exists(tmpFile):
            logger.debug('Do georeferencing based on an tps transformation ...')
            resampling = 'near'
            # doing a rectification of an image using a polynomial transformation
            # and a nearest neighbor resampling method
            command = 'gdalwarp -overwrite --config GDAL_CACHEMAX 500 -r %s -tps -wm 500 %s %s'%(resampling, tmpFile, dstFile)
            subprocess.check_call(command, shell=True)
        return dstFile
    except:
        raise
    finally:
        if os.path.exists(tmpFile):
            os.remove(tmpFile)

def transformClipPolygon(polygon, geoTransform):
    """ Functions transform the coordinates of a polygon based on an affine transformation. It therefor uses a
        a geoTransform matrix. See also http://www.gdal.org/gdal_datamodel.html for more information

    @param List<List<Float>>: polygon
    @param Tuple<Float>: geoTransform
    @return List<List<Float>> """
    transformedPolygon = []
    for coordinate in polygon:
        x = geoTransform[0] + coordinate[0] * geoTransform[1] + coordinate[1] * geoTransform[2]
        y = geoTransform[3] + coordinate[0] * geoTransform[4] + coordinate[1] * geoTransform[5]
        transformedPolygon.append([x, y])
    return transformedPolygon

def clipRasterWithShapfile(src_raster, dest_raster, clip_shp, logger):
    try:
        logger.debug('Starting cliping raster %s'%src_raster)
        command = 'gdalwarp -overwrite --config GDAL_CACHEMAX 500 -r near -wm 500 -cutline \'%s\' -crop_to_cutline %s %s'%(clip_shp, src_raster, dest_raster)
        subprocess.check_call(command, shell=True)
        return dest_raster
    except:
        logger.error("%s - Unexpected error while trying to clip the raster: %s - with command - %s"%(sys.stderr,sys.exc_info()[0],command))
        raise ClipException("Error while running subprocess via commandline!")