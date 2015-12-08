# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import os
from osgeo import gdal

def convertTimestampToPostgisString(time):
    """
    Converts a timestamp to an postgis timestamp string
    :param time: datetime.datetime
    :return: str
    """
    timestamp = "%s-%s-%s %s:%s:%s"%(time.year, time.month, time.day,
                                        time.hour, time.minute, time.second)
    return timestamp

def convertUnicodeDictToUtf(input):
    """
    :param input: dict
    :return: dict
    """
    if isinstance(input, dict):
        return {convertUnicodeDictToUtf(key): convertUnicodeDictToUtf(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convertUnicodeDictToUtf(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def getImageSize(filePath):
    """ Functions looks for the image size of an given path
    :type filePath: str
    :return: dict|None ({x:..., y: ....}) """
    if not os.path.exists(filePath):
        return None
    try:
        datafile = gdal.Open(filePath)
        if datafile:
            return {'x':datafile.RasterXSize,'y':datafile.RasterYSize}
        return None
    except:
        pass
    finally:
        if datafile:
            del datafile