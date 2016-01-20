# -*- coding: utf-8 -*-
'''
Created on Nov 1, 2013

@author: mendt
'''
import logging

#
# General
#

# DBCONFIG parameters for production use
DBCONFIG_PARAMS = {
    'host': 'localhost',
    'user':'user',
    'password':'password',
    'db':'vkdb'
}

# Definition of used srids
SRC_DICT_WKT = {
    3043:'PROJCS[\"ETRS89 / UTM zone 31N (N-E)\",GEOGCS[\"ETRS89\",DATUM[\"European_Terrestrial_Reference_System_1989\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6258\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4258\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",3],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"3043\"]]',
    4314:'GEOGCS[\"DHDN\",DATUM[\"Deutsches_Hauptdreiecksnetz\",SPHEROID[\"Bessel 1841\",6377397.155,299.1528128,AUTHORITY[\"EPSG\",\"7004\"]],TOWGS84[598.1,73.7,418.2,0.202,0.045,-2.455,6.7],AUTHORITY[\"EPSG\",\"6314\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4314\"]]',
    4326:'GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]]'
}

#
# For the web service
#

# Prefix for url routing. This is important if the service run's under an apache server parallel to other 
# applications
ROUTE_PREFIX = '/georeference'

# Admin address in case of unexpected API behavior
ADMIN_ADDR = 'Max.Mustermann@slub-dresden.de'

#
# Settings for the georeferencing service
#

# Temporary directory for tmp results
TMP_DIR = '/tmp'

# Directory where the mapfiles for the validation process are saved
GEOREFERENCE_MAPFILE_FOLDER = '~/tmp'

# Template for the validation mapfile
GEOREFERENCE_MAPFILE_TEMPLATE = '~/template-files/dynamic_template.map'

# Default settings for the validation mapfile
GEOREFERENCE_MAPFILE_DEFAULT_PARAMS = {
    "METADATA": {
        "wms_srs":"epsg:3857 epsg:4314 epsg:4326",
        "wms_onlineresource":"http://localhost/cgi-bin/mapserv?",
        "wms_enable_request":"*",
        "wms_titel":"Temporary Messtischblatt WMS",
        "wms_contactorganization":"Saxon State and University Library Dresden (SLUB)",
        "wms_contactperson":"Jacob Mendt", 
        "wms_contactelectronicmailaddress":"admin@kartenforum.slub-dresden.de",
        "wms_abstract":"This WMS provides the original Messtischblaetter without an spatial coordinate system."
    }
}

#
# Parameter for the georeference persitent / persitent georeferencing
#

# Settings for logger of the georeference persitent
GEOREFERENCE_DAEMON_LOGGER = {
    'name':'georeferenceupdate',
    'file':'~/tmp/updatedaemon.log',
    'level':logging.INFO,
    'formatter':'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Settings for the georeference persitent
GEOREFERENCE_DAEMON_SETTINGS = {
    'stdin':'~/tmp/null',
    'stdout':'~/tmp/tty',
    'stderr':'~/tmp/tty',
    'pidfile_path':'~/tmp/updatedaemon.pid',
    'pidfile_timeout':5,
    'sleep_time': 60
}

# Georeference TMS Cache url
GEOREFERENCE_PERSITENT_TMS_URL = 'http://vk2-cdn{s}.slub-dresden.de/tms2'

# Target dir where the persitent process maps should be saved
GEOREFERENCE_PERSITENT_TARGETDIR = '~/mtb_data_ref/'

# Target dir for the tms cache
GEOREFERENCE_PERSITENT_TMS = '~/tms_cache/'

# Target dir of the VRT files
GEOREFERENCE_PERSITENT_VRT = '~/tmp/georef'

# Id in the database of the wms layer
GEOREFERENCE_PERSITENT_WMS_LAYERID = {
    'M':87,
    'Ä':87
}

# Pattern for building the correct oai id
OAI_ID_PATTERN = 'oai:de:slub-dresden:vk:id-%s'

# Permalink resolver
PERMALINK_RESOLVER = 'http://digital.slub-dresden.de/'

# Template which are used for the creating of metadata records
TEMPLATE_OGC_SERVICE_LINK = {
    'wms_template':'http://localhost/cgi-bin/mtbows?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=Historische Messtischblaetter&TRANSPARENT=true&FORMAT=image/png&STYLES=&SRS=EPSG:%(srid)s&BBOX=%(westBoundLongitude)s,%(southBoundLatitude)s,%(eastBoundLongitude)s,%(northBoundLatitude)s&WIDTH=%(width)s&HEIGHT=%(height)s&TIME=%(time)s',
    'wcs_template':'http://localhost/cgi-bin/wcs?&SERVICE=WCS&VERSION=1.0.0&REQUEST=GetCoverage&COVERAGE=Historische_Messtischblaetter&CRS=EPSG:%(srid)s&BBOX=%(westBoundLongitude)s,%(southBoundLatitude)s,%(eastBoundLongitude)s,%(northBoundLatitude)s&TIME=%(time)s&WIDTH=%(width)s&HEIGHT=%(height)s&FORMAT=image/tiff',
    'dynamic_ows_template':'http://localhost/cgi-bin/dynamic-ows?map=%(mapid)s&SERVICE=%(service)s&VERSION=1.0.0&REQUEST=GetCapabilities'
}

# Elastic search index
ELASTICSEARCH_INDEX = 'http://localhost/spatialdocuments/map'

# Elastic search coordinate system
ELASTICSEARCH_SRS = 'EPSG:4326'

#
# For testing
#

# DBCONFIG parameters for testing
DBCONFIG_PARAMS_TESTING = {
    'host': 'localhost',
    'user':'user',
    'password':'testing',
    'db':'testdb'
}

# Flag parameter for testing mode
TEST_MODE = False

# TEST USER 
TEST_LOGIN = 'maxmustermann'

# Test data dir
TEST_DATA_DIR = '~/vk2-georeference/georeference/test/test-data'