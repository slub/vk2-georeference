# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import numpy
import gdal
from PIL import Image, ImageDraw
from gdalconst import GDT_Byte, GRA_NearestNeighbour

def clipImage(srcPath, destPath, polygon):
    """
    Function clips image for a given polygon. Does not do a resampling.

    :param srcPath: str
    :param destPath: str
    :param polygon:
    :return: List.<List.<Integer>>: polygon
    """
    # read image as RGB and add alpha (transparency)
    im = Image.open(srcPath).convert("RGBA")

    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)

    # create mask
    # polygon = [(637, 652),(625, 7125),(7741, 7133),(7755, 668),(637, 652)]
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]

    # transparency (4th column)
    newImArray[:,:,3] = mask*255

    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGBA")
    newIm.save(destPath)

def resampleGeoreferencedImage(srcDataset, geoTransform, geoProj, outputDriver, destPath):
    """
    Function resample an unreferenced image to georeferenced image.

    :param srcDataset: gdal.Dataset
    :param geoTransform: Tuple<Float>
    :param geoProj: str
    :param outputDriver: gdal.Driver
    :param destPath: str
    :return: gdal.Dataset
    """
    targetDataset = outputDriver.Create(destPath, srcDataset.RasterXSize, srcDataset.RasterYSize, 4, GDT_Byte)
    targetDataset.SetGeoTransform(geoTransform)
    targetDataset.SetProjection(geoProj)
    gdal.ReprojectImage(srcDataset, targetDataset, geoProj, geoProj, GRA_NearestNeighbour)
    return targetDataset
