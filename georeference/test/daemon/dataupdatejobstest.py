# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 05.08.15

@author: mendt
'''
import unittest
import logging
import time
from georeference.settings import DBCONFIG_PARAMS_TESTING
from georeference.models.meta import initializeDb
from georeference.models.meta import getPostgresEngineString
from georeference.daemon.dataupdatejobs import runningNewJobs
from georeference.daemon.dataupdatejobs import runningUpdateJobs
from georeference.daemon.dataupdatejobs import updateDataBasis
from georeference.utils.logger import createLogger

class DataUpdateJobsTestTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print '=============='
        print 'Start georeferenceupdate tests ...'
        print '=============='
        cls.logger = createLogger('GeoreferenceUpdateTest', logging.DEBUG)

    @unittest.skip('Skip testRunningNewJobs')
    def testRunningNewJobs(self):
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Test if testRunningNewJobs runs correctly ..."

        dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS_TESTING), self.logger)
        response = runningNewJobs(dbsession, self.logger, True)

        # add tests
        # @TODO

        dbsession.rollback()

    @unittest.skip('Skip testRunningNewJobs')
    def testRunningUpdateJobs(self):
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Test if testRunningUpdateJobs runs correctly ..."

        dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS_TESTING), self.logger)
        response = runningUpdateJobs(dbsession, self.logger, True)

        # add tests
        # @TODO

        dbsession.rollback()

    @unittest.skip('Skip testLookForUpdateProcess')
    def testLookForUpdateProcess(self):
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Test if testLookForUpdateProcess runs correctly ..."

        dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS_TESTING), self.logger)
        response = updateDataBasis(dbsession, self.logger, True)

        # add tests
        # @TODO

        dbsession.rollback()

    @unittest.skip('Skip testLookForUpdateProcess_Infinity')
    def testLookForUpdateProcess_Infinity(self):
        print "--------------------------------------------------------------------------------------------"
        print "\n"
        print "Test if testLookForUpdateProcess_Infinity runs correctly ..."

        dbsession = initializeDb(getPostgresEngineString(DBCONFIG_PARAMS_TESTING), self.logger)
        while True:
            print "New loop run ..."
            updateDataBasis(dbsession, self.logger, True)
            dbsession.commit()
            print "Long sleep ..."
            time.sleep(10)


        # add tests
        # @TODO


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
