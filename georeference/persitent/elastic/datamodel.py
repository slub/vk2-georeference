'''
Created on May 11, 2015

@author: mendt
'''
import os
import gdal
from pyproj import Proj
from pyproj import transform
from georeference.settings import ELASTICSEARCH_SRS
from georeference.settings import DIRECTORY_TYPE_MAPPING
from georeference.settings import GEOREFERENCE_PERSITENT_TMS_URL
from georeference.settings import OAI_ID_PATTERN
from georeference.settings import PERMALINK_RESOLVER
from georeference.settings import TEMPLATE_OGC_SERVICE_LINK
from georeference.models.vkdb.metadata import Metadata
from georeference.utils.tools import getImageSize
from georeference.utils.process.georeferencer import transformClipPolygon
from georeference.utils.parser.georeferenceparser import parseGcps

def createSearchRecord(mapObj, dbsession, logger, georefObj=None):
    """ Function creates an elasticsearch record for a given mapObj
        
    :type mapObj: vkviewer.python.models.vkdb.Map
    :type dbsession: sqlalchemy.orm.session.Session
    :type logger: logging.Logger
    :type georefObj: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess|None
    """
    mapData = {}
    # check if map is georeferenced because only
    # georeferenced map should be published via the index
    metadataObj = Metadata.by_id(mapObj.id, dbsession)
    timepublish = metadataObj.timepublish.date()
    oai = OAI_ID_PATTERN%mapObj.id
    onlineResList = getOnlineResourceData(mapObj, metadataObj, metadataObj.timepublish.year, oai, dbsession)

    mapData["oai:de:slub-dresden:vk:id-%s"%mapObj.id] = {
        "id": mapObj.id,
        "dataid": mapObj.apsdateiname,
        "title": metadataObj.titleshort,
        "titlelong": metadataObj.title,
        "description": metadataObj.description,
        "online-resources": onlineResList,
        "denominator": int(metadataObj.scale.split(':')[1]),
        "keywords": ";".join([metadataObj.type,metadataObj.technic]),
        "time": "%s-%s-%s"%(timepublish.year, timepublish.month, timepublish.day),
        "plink": metadataObj.apspermalink,
        "org":metadataObj.imagejpg,
        "georeference": mapObj.isttransformiert,
        "maptype": mapObj.maptype,
        "thumb": metadataObj.thumbssmall,
        "zoomify":metadataObj.imagezoomify
    }
            
    # if there is a geometry then add it to the record
    boundingbox = None
    try:
        elasticsearchSRS = int(ELASTICSEARCH_SRS.split(':')[1])
        extent = mapObj.getExtent(dbsession, elasticsearchSRS)
        boundingbox = {
            "type": "polygon",
            "coordinates": [[
                [extent[0],extent[1]],
                [extent[0],extent[3]],
                [extent[2],extent[3]],
                [extent[2],extent[1]],
                [extent[0],extent[1]]
            ]]
        } 
    except AttributeError:
        logger.debug('Missing geometry')
        pass
            
    if boundingbox is not None and mapObj.isttransformiert:
        mapData[oai]["geometry"] = boundingbox

    # if georeferenced add tms cache
    if mapObj.isttransformiert:
        # create tms url
        subDirectory = DIRECTORY_TYPE_MAPPING[mapObj.maptype]
        file_name, file_extension = os.path.splitext(os.path.basename(mapObj.georefimage))
        tmsUrl = GEOREFERENCE_PERSITENT_TMS_URL + '/' + os.path.join(subDirectory, file_name)
        mapData[oai]["tms"] = tmsUrl

    if georefObj is not None:
        transformedClipPolygon = getTransformedClipPolygon(mapObj, georefObj, logger)
        mapData[oai]["clippolygon"] = transformedClipPolygon

    return mapData   

def getTransformedClipPolygon(mapObj, georefObj, logger):
    """ Function gets a transformed clip polygon for a given parameter set

    :type mapObj: vkviewer.python.models.vkdb.Map
    :type georefObj: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess
    :type logger: logging.Logger """
    polygon = georefObj.clippolygon['polygon']
    gcps = parseGcps(georefObj.georefparams['gcps'])
    srid = georefObj.georefparams['target']

    # generate a transformed clip polygon based on the georeference
    # parameter and an affine transformation
    geoTransform = gdal.GCPsToGeoTransform(gcps)
    transformedClipPolygon = transformClipPolygon(polygon, geoTransform)

    # check if the clip polygon has to reproject to the elasticsearch srs (Default is 4326)
    if srid.lower() != ELASTICSEARCH_SRS.lower():
        transformPolygonInTargetSRS = []
        inProj = Proj(init=srid.lower())
        outProj = Proj(init=ELASTICSEARCH_SRS.lower())
        for record in transformedClipPolygon:
            x, y = transform(inProj,outProj,record[0],record[1])
            transformPolygonInTargetSRS.append([x,y])
        transformedClipPolygon = transformPolygonInTargetSRS

    return transformedClipPolygon


def getOnlineResourceData(mapObj, metadataObj, time, oai, dbsession):    
    """ Function creates a list of online resource records 
    
        :type mapObj: vkviewer.python.models.vkdb.Map
        :type metadataObj: vkviewer.python.models.vkdb.Metadata
        :type time: int
        :type oai: str
        :type dbsession: sqlalchemy.orm.session.Session
        :rtype: Array"""
    image_size = getImageSize(mapObj.georefimage)
    onlineResList = [
        {
            'url':metadataObj.apspermalink,
            'type':'Permalinkk'
        }
    ]
    
    # append OGC services if georeferenced
    if mapObj.isttransformiert:
        # get srid and bbox
        srid = mapObj.getSRID(dbsession)
        extent = mapObj.getExtent(dbsession, srid)
            
        # append VK2 Permalink 
        onlineResList.append({
            'url':PERMALINK_RESOLVER+oai,
            'type':'Permalink'
        })
        
        # append WMS 
        onlineResList.append({
            'url':TEMPLATE_OGC_SERVICE_LINK['dynamic_ows_template']%({
                'mapid':mapObj.id,
                'service':'WMS'                
                }),
            'type':'WMS'
        })
        onlineResList.append({
            'url':TEMPLATE_OGC_SERVICE_LINK['wms_template']%({
                'westBoundLongitude':str(extent[0]),
                'southBoundLatitude':str(extent[2]),
                'eastBoundLongitude':str(extent[2]),
                'northBoundLatitude':str(extent[3]),
                'srid':srid,
                'time':time,
                'width':256,
                'height':256
            }),
            'type':'Time-enabled WMS'
        })
        if time <= 1900:
            # append normal wcs     
            onlineResList.append({
                'url':TEMPLATE_OGC_SERVICE_LINK['dynamic_ows_template']%({
                    'mapid':mapObj.id,
                    'service':'WCS'                
                }),
                'type':'WCS'
            })  
            # append time-enabled WCS
            onlineResList.append({
                'url':TEMPLATE_OGC_SERVICE_LINK['wcs_template']%({
                    'westBoundLongitude':str(extent[0]),
                    'southBoundLatitude':str(extent[2]),
                    'eastBoundLongitude':str(extent[2]),
                    'northBoundLatitude':str(extent[3]),
                    'srid':srid,
                    'time':time,
                    'width':str(image_size['x']),
                    'height':str(image_size['y'])
                }),
                'type':'Time-enabled WCS'
            })
    return onlineResList
