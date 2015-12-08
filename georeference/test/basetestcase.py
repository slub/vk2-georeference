# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import unittest
import os
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from zope.sqlalchemy import ZopeTransactionExtension

from georeference.settings import DBCONFIG_PARAMS_TESTING
from georeference.settings import TEST_LOGIN
from georeference.models.meta import getPostgresEngineString

class BaseTestCase(unittest.TestCase):
      
    @classmethod
    def setUpClass(cls):     
        sqlalchemy_enginge = getPostgresEngineString(DBCONFIG_PARAMS_TESTING)
        cls.engine = create_engine(sqlalchemy_enginge, encoding='utf8', echo=True)
        cls.Session = scoped_session(sessionmaker(bind=cls.engine,extension=ZopeTransactionExtension()))
        cls.dbsession = cls.Session()
        cls.testDataDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-data')
        cls.user = TEST_LOGIN

    def tearDown(self):
        testing.tearDown()
    
    def getRequestWithDb(self, request):
        request.db = self.dbsession
        return request
    
    def getPOSTRequest(self, params):
        """ Generate a test post request for the given parameter set
        
        @param dict: params
        @return dict """
        request = self.getRequestWithDb(testing.DummyRequest(params=params, post=params))        
        request.json_body = params
        return request
    
    def getGETRequest(self, params):
        """ Generate a test get request for the given parameter set
        
        @param dict: params
        @return dict """
        request = self.getRequestWithDb(testing.DummyRequest(params=params))        
        return request