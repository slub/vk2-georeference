# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 22.01.16

@author: mendt
'''
import multiprocessing as mp
import random
import string
import os
import sys

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH_PARENT = os.path.abspath(os.path.join(BASE_PATH, os.pardir))
sys.path.insert(0, BASE_PATH)
sys.path.append(BASE_PATH_PARENT)

from georeference.settings import DBCONFIG_PARAMS
from georeference.models.meta import getPostgresEngineString
from georeference.models.meta import initializeDb
from georeference.models.vkdb.map import Map
from georeference.scripts.updatetms import calculateCompressedTMS
from georeference.scripts.updatetms import compressTMSCache

DATA_DIRECTORY_TMS = '/srv/vk/data/tms'

RUN_IN_PARALLEL_MODE = True

NUMBER_PROCESSES = 6

OVERWRITE = True

if __name__ == '__main__':
    # first get a list of jobs
    jobList = []
    dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS), False)
    maps = Map.all(dbsession)
    for mapObj in maps:
        if mapObj.isttransformiert:
            jobList.append([
                mapObj.georefimage,
                os.path.join(DATA_DIRECTORY_TMS, str(mapObj.maptype).lower())
            ])
            tmsCachePath = os.path.join(DATA_DIRECTORY_TMS, str(mapObj.maptype).lower())

    print jobList

    if not RUN_IN_PARALLEL_MODE:
        print 'Update TMS cache serial ...'
        for record in jobList:
            calculateCompressedTMS(record[0], record[1])
        print 'Finish update TMS cache!'

    else:
        print 'Update TMS cache parallel ...'

        # define parallel process function
        def updateTMSProcess(job):
            calculateCompressedTMS(job[0], job[1])
            return job

        pool = mp.Pool(processes=NUMBER_PROCESSES)
        results = pool.map(updateTMSProcess, jobList)

        print 'Finish update TMS cache!'