# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 04.08.15

@author: mendt
'''
import os
import uuid
from mapscript import MS_IMAGEMODE_RGB, MS_OFF, MS_PIXELS, MS_LAYER_RASTER, layerObj, mapObj, MS_ON, outputFormatObj
from georeference.utils.exceptions import MapfileBindingInitalizationException


OutputFormat_JPEG = {"NAME":"jpeg","MIMETYPE":"image/jpeg","DRIVER":"AGG/JPEG","EXTENSION":"jpg",
                        "IMAGEMODE":MS_IMAGEMODE_RGB,"TRANSPARENT":MS_OFF}
Metadata = {"wms_srs":"EPSG:4326","wms_onlineresource":"http://localhost/cgi-bin/mapserv?",
            "wms_enable_request":"*","wms_titel":"Temporary Messtischblatt WMS"}

def createMapfile(layername, datapath, georefTargetSRS,  mapfileTemplate, mapfileDir, mapfileParams):
    """ Function creates a temporary mapfile

    :type layername: str
    :type datapath: str
    :type georefTargetSRS: int
    :type mapfileTemplate: str
    :type mapfileDir: str
    :type mapfileParams: str """
    try:
        mapfile =  MapfileBinding(mapfileTemplate,mapfileDir, **mapfileParams)
        mapfile.addLayerToMapfile(datapath, layername, georefTargetSRS)
        wms = mapfile.saveMapfile()
        return wms
    except:
        raise

class MapfileBinding:

    def __init__(self, src_mapfilePath, dest_mapfileFolder, **kwargs):
        # init wms service name
        self.servicename= "wms_%s.map"%uuid.uuid4()

        # init the mapfile based on a template file
        self.mapfilepath = os.path.join(dest_mapfileFolder, self.servicename)
        self.__initMapfile__(src_mapfilePath, self.mapfilepath)


        if len(kwargs) > 0:
            self.__initMapfileParameter__(kwargs)
        else:
            raise MapfileBindingInitalizationException("Missing mapfile information!")

    def __initMapfile__(self, src_mapfilePath, dest_mapfilePath):
        mapfile = mapObj(src_mapfilePath)
        self.saveMapfile(mapfile)
        self.mapfile = mapObj(self.mapfilepath)

    def __initMapfileParameter__(self, kwargs):
        """
        Set the option parameter for the map element
        """
        #generic mapfile options
        self.mapfile.units = MS_PIXELS
        self.mapfile.status = MS_ON

        #if "OUTPUTFORMAT" in kwargs:
        #    self.__addOutputFormat__(kwargs["OUTPUTFORMAT"])
        if "METADATA" in kwargs:
            self.__addMetadata__(kwargs["METADATA"])

    def __addMetadata__(self, dictMD):
        self.wms_url = dictMD["wms_onlineresource"]+"map=%s"%self.mapfilepath
        for key in dictMD:
            if key is "wms_onlineresource":
                self.mapfile.web.metadata.set(key,self.wms_url)
            else:
                self.mapfile.web.metadata.set(key,dictMD[key])

    def __addOutputFormat__(self, dictOutFormat):
        """
        Function adds a outputformat object to the mapfile.

        @param dictOutFormat: Represents a dictionary with the outputformat arguments. It should
        contains the keys:

            @param NAME:
            @param MIMETYPE:
            @param DRIVER:
            @param EXTENSION:
            @param IMAGEMODE:
            @param TRANSPARENT:
        """
        # creates a OutputFormatObject and adds the parameter to it
        if "DRIVER" in dictOutFormat:
            outFormatObj = outputFormatObj(dictOutFormat["DRIVER"])
        else:
            raise MapfileBindingInitalizationException("Missing Driver for OutputFormat Element")

        if "NAME" in dictOutFormat:
            outFormatObj.name = dictOutFormat["NAME"]
        if "MIMETYPE" in dictOutFormat:
            outFormatObj.mimetype = dictOutFormat["MIMETYPE"]
        if "EXTENSION" in dictOutFormat:
            outFormatObj.extension = dictOutFormat["EXTENSION"]
        if "IMAGEMODE" in dictOutFormat:
            outFormatObj.imagemode = dictOutFormat["IMAGEMODE"]
        if "TRANSPARENT" in dictOutFormat:
            outFormatObj.transparent = dictOutFormat["TRANSPARENT"]

        # adds the OutputFormatObject to the mapfile
        self.mapfile.appendOutputFormat(outFormatObj)

    def saveMapfile(self, mapfile = None):
        if mapfile != None and isinstance(mapfile,mapObj):
            mapfile.save(self.mapfilepath)
            return None
        else:
            self.mapfile.save(self.mapfilepath)
            return self.mapfile.getMetaData("wms_onlineresource")

    def addLayerToMapfile(self, dataPath, layerName,georefTargetSRS):
        """ Function adds a layer to a mapfile

        :type dataPath: str
        :type layerName: str
        :type georefTargetSRS: int """

        layer = layerObj()
        layer.data = dataPath
        layer.type = MS_LAYER_RASTER
        layer.name = layerName
        layer.units = MS_PIXELS
        layer.status = MS_OFF
        layer.setProjection("init=epsg:%s"%georefTargetSRS)
        self.mapfile.insertLayer(layer)
