#!/usr/bin/env python
# -*- coding: utf-8 -*-
#/******************************************************************************
# * $Id: UpdateMappingService.py 2014-01-28 jmendt $
# *
# * Project:  Virtuelles Kartenforum 2.0
# * Purpose:  This script encapsulate then tasks which are run for updating the vk2 mapping services. This 
# *           includes asking the database for new georeference process parameter and if they are available 
# *           it run's incremental for each timestamp the following process. At first it's calculate for all
# *           messtischblätter per timestamp the georeference maps. After that it recalculate the virtual    
# *           datasets for the timestamps, which are used for by the original wms for publishing the messtischblätter.
# *           After that it reseeds the cache for there extend of the new georeferenced messtischblätter for 
# *           the timestamp. At least it update's the database and pushed the metadata for the messtischblätter
# *           to the csw service. From this moment on the messtischblätter together with there metadata are 
# *           available for the users. 
# * Author:   Jacob Mendt
# * @todo:    Update georeference datasource
# *
# * 
# ******************************************************************************
# * Copyright (c) 2014, Jacob Mendt
# *
# * Permission is hereby granted, free of charge, to any person obtaining a
# * copy of this software and associated documentation files (the "Software"),
# * to deal in the Software without restriction, including without limitation
# * the rights to use, copy, modify, merge, publish, distribute, sublicense,
# * and/or sell copies of the Software, and to permit persons to whom the
# * Software is furnished to do so, subject to the following conditions:
# *
# * The above copyright notice and this permission notice shall be included
# * in all copies or substantial portions of the Software.
# *
# * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# * DEALINGS IN THE SOFTWARE.
# ****************************************************************************/'''
# * 
# * Example command:
# * bin/python vkviewer/python/scripts/UpdateVirtualdatasets.py --mode 'testing' --host 'localhost' --user 'postgres' --password 'postgres' 
# *   --db 'messtischblattdb' --tmp_dir '/tmp/virtualdatasets' --vrt_dir '/tmp'

import logging
import argparse
import os
import subprocess
import sys
from subprocess import CalledProcessError

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH_PARENT = os.path.abspath(os.path.join(BASE_PATH, os.pardir))
sys.path.insert(0, BASE_PATH)
sys.path.append(BASE_PATH_PARENT)

from georeference.models.meta import initializeDb
from georeference.models.vkdb.virtualdataset import Virtualdataset
from georeference.utils.logger import createLogger
from georeference.utils.exceptions import ParameterException

""" Default options """
# Directory for saving the temporary files
TMP_DIR = '/tmp'

# Target dir for georeference messtischblatt
GEOREF_TARGET_DIR = '/tmp'

# Target dir for saving the virtual datasets
VRT_TARGET_DIR = '/tmp'


""" Functions """
def loadDbSession(database_params): 
    logger.info('Initialize new database connection ...')
    sqlalchemy_enginge = 'postgresql+psycopg2://%(user)s:%(password)s@%(host)s:5432/%(db)s'%(database_params)
    try:
        return initializeDb(sqlalchemy_enginge)
    except:
        logger.error('Could not initialize database. Plase check your database settings parameter.')
        raise ParameterException('Could not initialize database. Plase check your database settings parameter.')

def buildCreateVrtCmd(target_path, shapefile_path):
    """ Create the command for producing a virtutal dataset via gdalbuildvrt command on 
        the basic of a shapefile        
        
        Arguments:
            target_path {string}
            shapefile_path {string} Shapefile which represents the tileindex and has a attribute 'LOCATION'
        Returns: {string}
    """
    return "gdalbuildvrt --config GDAL_CACHEMAX 500 -resolution 'highest' -hidenodata -addalpha -overwrite -tileindex \"LOCATION\" %s %s"%(target_path, '%s.shp'%shapefile_path)

def buildCreateShapeTileIndexCmd(timestamp, shp_path, database_params):
    """ Create the command for command line processing of a shapefile, which represents
        a tileindex for one timestamp for all historic messtischblaetter.
        
        Arguments:
            timestamp {Integer} Time in year
            shp_path {String}
            database_params {dict}
        Returns: {String} """    
    createShapeTileIndexCmd = "pgsql2shp -f %(shp_path)s -h %(host)s -u %(user)s -P '%(password)s' %(db)s \
    \"SELECT map.boundingbox, map.georefimage as location, metadata.timepublish as time \
    FROM map, metadata WHERE map.maptype = 'M' AND map.isttransformiert = True AND map.id = metadata.mapid AND EXTRACT('year' from metadata.timepublish) = %(timestamp)s\""
    return createShapeTileIndexCmd % (dict({
        'shp_path': shp_path,                                  
        'timestamp': str(timestamp) 
    }.items() + database_params.items()))

    
def getVirtualDatasetCreateCommands(targetVrtPath, tmp_dir, time, database_params):
    """ This function create a virtual dataset for the given parameters 
        
        Arguments:
            targetVrtPath {string}
            tmp_dir {string}
            time {Integer}
            database_params {dict} for querying the database via pgsql2shp
            with_cache {Boolean} If true also a update cache command is created
        Returns: {list} commands for creating virtual datasets """
    shpTilePath = os.path.join(tmp_dir, (str(time)))

    # collect commands 
    commands = []
    commands.append(buildCreateShapeTileIndexCmd(time, shpTilePath, database_params))
    commands.append(buildCreateVrtCmd(targetVrtPath, shpTilePath))
    # Comment out for testing purpose (time reduction)
    # commands.append(buildCreateVrtOverviewCmd(targetVrtPath))
    return commands
   
    
def updateVrt( database_params, vrt_target_dir, tmp_dir, logger, dbsession, vrt):
    """ Processes a refreshed virtual dataset, updates the cache and after all update the 
        database relations in messtischblatt db

    :type dict: database_params
    :type str: vrt_target_dir
    :type str: tmp_dir
    :type logging.Logger: logger
    :type sqlalchemy.orm.session.Session: dbsession
    :type georeference.models.vkdb.virtauldatasets.Virtualdatasets: vrt
    :return: str
    """
    try:
        logger.info('Starting updating virtual datasets for timestamp %s ...'%vrt.timestamp)
        targetPath  = os.path.join(vrt_target_dir, '%s.vrt'%vrt.timestamp.year)
        commands = getVirtualDatasetCreateCommands(targetPath, tmp_dir, vrt.timestamp.year, database_params)
        
        # now execute command
        for command in commands:
            logger.info('Execute - %s'%command)
            subprocess.check_call(command, shell = True)

        logger.info('Update database state for virtual datasets ...')
        vrt.setPath(targetPath, dbsession)

        return targetPath
    except CalledProcessError as e:
        logger.error('CalledProcessError while trying to run a command for updating the virtual datasets.')
        pass
    except:
        raise
           
def updateVirtualdatasetForTimestamp( timestamp, vrt_target_dir, tmp_dir, database_params, dbsession, logger):
    """ This function controls the complete update process for one timestamp 
        
    :type int: timestamp
    :type str: vrt_target_dir
    :type str: tmp_dir
    :type dict: database_params
    :type sqlalchemy.orm.session.Session: dbsession
    :type logging.Logger: logger
    """
    logger.info('Update virtualdataset for timestamp %s ...'%timestamp)
    vrt = Virtualdataset.by_timestamp(timestamp, dbsession)
    targetPath = updateVrt(database_params, vrt_target_dir, tmp_dir, logger, dbsession, vrt)
    logger.info('Update virtualdataset %s.'%targetPath)


""" Main """    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'This scripts updates the virtualdatasets for all or for a single \
        timestamp.', prog = 'Script UpdateVirtualdatasets.py')
    
    # parse command line
    parser = argparse.ArgumentParser(description='Parse the key/value pairs from the command line!')
    parser.add_argument('--mode', type=str, default='testing', help='Run in "production" or "testing" mode. Without mode parameter it run\'s in testing mode.')
    parser.add_argument('--host', help='host for messtischblattdb')
    parser.add_argument('--user', help='user for messtischblattdb')
    parser.add_argument('--password', help='password for messtischblattdb')
    parser.add_argument('--db', help='db name for messtischblattdb')
    parser.add_argument('--log_file', help='define a log file')
    parser.add_argument('--tmp_dir', default='/tmp', help='define directory for temporary files (default: /tmp')
    parser.add_argument('--vrt_dir', default='/tmp', help='define directory for vrt files (default: /tmp')
    arguments = parser.parse_args()
    
    # create logger
    if arguments.log_file:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        sqlalchemy_logger = createLogger('sqlalchemy.engine', logging.DEBUG, logFile=''.join(arguments.log_file), formatter=formatter)     
        logger = createLogger('UpdateVRT', logging.DEBUG, logFile=''.join(arguments.log_file), formatter=formatter)
    else: 
        sqlalchemy_logger = createLogger('sqlalchemy.engine', logging.WARN)
        logger = createLogger('UpdateVRT', logging.DEBUG)   

    # parse parameter parameters
    database_params = {}
    if arguments.host:
        database_params['host'] = arguments.host
    if arguments.user:
        database_params['user'] = arguments.user
    if arguments.password:
        database_params['password'] = arguments.password
    if arguments.db:
        database_params['db'] = arguments.db
    if arguments.tmp_dir:
        TMP_DIR = arguments.tmp_dir
    if arguments.vrt_dir:
        VRT_TARGET_DIR = arguments.vrt_dir
        
    testing = False
    if arguments.mode is "testing":
        testing = True    

    logger.info('Start updating the virtualdatasets')
    for value in range(1868, 1946):
        updateVirtualdatasetForTimestamp('%s-01-01 00:00:00'%value, VRT_TARGET_DIR, TMP_DIR, database_params, loadDbSession(database_params), logger, testing=testing)
        
