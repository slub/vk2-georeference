# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import desc

from georeference.models.meta import Base



class Metadata(Base):
    __tablename__ = 'metadata'
    __table_args__ = {'extend_existing':True}
    mapid = Column(Integer, primary_key=True)
    title = Column(String(255))
    titleshort = Column(String(70))
    serientitle = Column(String(255))
    description = Column(String(255))
    measures = Column(String(255))
    scale = Column(String(255))
    type = Column(String(255))
    technic = Column(String(255))
    ppn = Column(String(255))
    apspermalink = Column(String(255))
    imagelicence = Column(String(255))
    imageowner = Column(String(255))
    imagejpg = Column(String(255))
    imagezoomify = Column(String(255))
    timepublish = Column(DateTime(timezone=False))
    blattnr = Column(String(10))
    thumbssmall = Column(String(255))
    thumbsmid = Column(String(255))
    
    @classmethod
    def by_id(cls, id, session):
        return session.query(Metadata).filter(Metadata.mapid == id).first()

    @classmethod
    def all(cls, session):
        return session.query(Metadata).order_by(desc(Metadata.mapid))