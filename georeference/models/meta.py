# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def initialize_sql(engine):
    """ 
    Binds the engine to the Base object.
    
    :type engine: string 
    """
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    
def initializeDb(sqlalchemy_engine):
    """ 
    Creates a session object based on SQLAlchemy
    :type sqlalchemy_engine: string
    :return: sqlalchemy.orm.session.Session 
    """
    engine = create_engine(sqlalchemy_engine, encoding='utf8', echo=True)
    DBSession = sessionmaker(bind=engine)
    initialize_sql(engine)
    return DBSession()

def getPostgresEngineString(dbconfig):
    """ 
    The function creates an postgresql engine string used by SQLAlchemy.
    
    :type dbconfig: dict
    :return: string 
    """
    return 'postgresql+psycopg2://%(user)s:%(password)s@%(host)s:5432/%(db)s'%(dbconfig)

Base = declarative_base()

   