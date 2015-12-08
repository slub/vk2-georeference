# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import os
import sys
import logging
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from zope.sqlalchemy import ZopeTransactionExtension

from settings import DBCONFIG_PARAMS
from settings import ROUTE_PREFIX
from georeference.models.meta import initialize_sql
from georeference.models.meta import Base
from georeference.models.meta import getPostgresEngineString
from georeference.utils.logger import createLogger

# set path for finding correct project scripts and modules
sys.path.insert(0,os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "python"))

# load logger
LOGGER = createLogger('georeference', logging.DEBUG)

# base path
here = os.path.dirname(os.path.abspath(__file__))

def loadLogger(debug=True):
    """ This function initialize the logger for the application.
        
    @param boolean: debug (Default=True) """
    if debug:
        LOGGER = createLogger('georeference', logging.DEBUG)
    else:
        LOGGER = logging.getLogger(__name__)
    
def addRoutes(config):
    """ Adds routing endpoints to the pyramid application 
    
    @param dict: config """
    config.add_route('process_byobjectid', ROUTE_PREFIX+'/georef/process')
    config.add_route('process_bygeoreferenceid', ROUTE_PREFIX+'/georef/process/{georeferenceid}')
    config.add_route('georeference', ROUTE_PREFIX+'/georef/{action}')
    config.add_route('admin-process', ROUTE_PREFIX+'/admin/process')
    config.add_route('admin-evaluation', ROUTE_PREFIX+'/admin/process/{action}')
    config.add_route('user-history', ROUTE_PREFIX+'/user/{userid}/history')
    config.add_route('user-georeference-information', ROUTE_PREFIX+'/user/information')
 
def loadDB(config, settings, debug=False):
    """ Loads the database connection based on sql alchemy 
    
    @param dict: config
    @param dict: settings
    @param boolean: debug (Default=False) """
    def db(request):
        return request.registry.dbmaker()   
    
    if debug:
        engine = create_engine(getPostgresEngineString(DBCONFIG_PARAMS), encoding='utf8', echo=True)
    else:
        engine = engine_from_config(settings, prefix='sqlalchemy.')
    config.registry.dbmaker = scoped_session(sessionmaker(bind=engine,extension=ZopeTransactionExtension()))
    config.add_request_method(db, reify=True)   
    
    initialize_sql(engine)
    config.scan('models')

def createWsgiApp(global_config, debug=False, **settings):
    
    # first of all load the loggers
    loadLogger(debug)
    
    if debug:
        settings = {}
        settings['reload_all'] = True
        settings['debug_all'] = True
        
    LOGGER.info('Loading Configurator ...')
    config = Configurator(settings=settings)

    LOGGER.info('Include pyramid_tm ...')
    config.include('pyramid_tm')
    
    LOGGER.info('Loading database settings in ...')
    loadDB(config, settings, debug)

    # add routes
    LOGGER.info('Initialize routes ...')
    addRoutes(config)
    
    # add views to routes
    LOGGER.info('Add views (route endpoints) ...')
    config.scan('views')
    
    LOGGER.info('Georeference rest application is initialize.')
    return config.make_wsgi_app()


def main(global_config, **settings):
    return createWsgiApp(global_config, debug=False, **settings)

if __name__ == '__main__':
    app = createWsgiApp(None, debug=True)
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
