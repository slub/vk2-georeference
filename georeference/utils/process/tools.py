import osgeo.osr as osr
import gdal
from gdal import GA_ReadOnly

def convertPostgisStringToList(string):
    """ Converts a postgis string to a list of coordinates
    :type str: String
    :return: list|None
    """
    if 'POLYGON' in string:
        coordinates = []
        stripPolygon = string.split('POLYGON')[1]
        stripBraces = stripPolygon[2:-2]
        splitCoordinates = stripBraces.split(',')
        for splitCoordinate in splitCoordinates:
            coordinate = splitCoordinate.split(' ')
            coordinates.append([float(coordinate[0]), float(coordinate[1])])
        return coordinates
    return None

def convertListToPostgisString(coordinates, type):
    """ Converts a list of coordinates to a postgis string
    :type list: coordinates
    :type str: String
    :return: str
    """
    string = ''
    if type == 'POLYGON':
        string = 'POLYGON((%s))'

    coordinatesAsString = []
    for coordinate in coordinates:
        coordinatesAsString.append('%s %s'%(coordinate[0], coordinate[1]))

    return string % ','.join(coordinatesAsString)

def extractSRIDFromDataset(dataset):
    """ Extracts the srid from a given dataset.

    :type gdal.Dataset: dataset
    :return: string
    """
    proj = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.SetFromUserInput(proj)
    return srs.GetAttrValue('AUTHORITY', 0) + ':' + srs.GetAttrValue('AUTHORITY', 1)

def getBoundsFromDataset(dataset):
    """ Returns the bounds of a given gdal dataset.

    :type gdal.Dataset: dataset
    :return: List<number>
    """
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    geotransform = dataset.GetGeoTransform()
    bb1 = originX = geotransform[0]
    bb4 = originY = geotransform[3]

    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    width = cols*pixelWidth
    height = rows*pixelHeight

    bb3 = originX + width
    bb2 = originY + height
    return [ bb1, bb2, bb3, bb4 ]

def stripSRIDFromEPSG(epsgcode):
    """ Returns the pure epsg number as an integer.

    :type str: epsgcode:
    :return: integer
    """
    return int(epsgcode.split(':')[1])

def parseBoundingBoxPolygonFromFile(filePath):
    """ Functions parses the boundingbox polygon from a given data file and returns it as postgis
        string.

    :type str: filePath
    :return: str
    """
    dataset = gdal.Open(filePath, GA_ReadOnly)
    bounds = getBoundsFromDataset(dataset)
    return "POLYGON((%(lx)s %(ly)s, %(lx)s %(uy)s, %(ux)s %(uy)s, %(ux)s %(ly)s, %(lx)s %(ly)s))"% {
            "lx": bounds[0], "ly": bounds[1], "ux": bounds[2], "uy": bounds[3] }


def parseSRIDFromFile(filePath):
    """ Returns the pure epsg number as an integer.

    :type str: epsgcode:
    :return: integer
    """
    dataset = gdal.Open(filePath, GA_ReadOnly)
    epsgcode = extractSRIDFromDataset(dataset)
    return int(epsgcode.split(':')[1])
