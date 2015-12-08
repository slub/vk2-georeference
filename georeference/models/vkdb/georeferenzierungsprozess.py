# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import json
from georeference.models.meta import Base
from georeference.utils.exceptions import ProcessIsInvalideException

from sqlalchemy import Column, Integer, Boolean, String, DateTime, desc, asc, PickleType


class JsonPickleType(PickleType):
    impl = String
    
class Georeferenzierungsprozess(Base):
    __tablename__ = 'georeferenzierungsprozess'
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key=True)
    messtischblattid = Column(Integer)
    georefparams = Column(JsonPickleType(pickler=json))
    clipparameter = Column(String(255))
    timestamp = Column(DateTime(timezone=False))
    type = Column(String(255))
    nutzerid = Column(String(255))
    processed = Column(Boolean)
    isactive = Column(Boolean)
    overwrites = Column(Integer)
    adminvalidation = Column(String(20))
    mapid = Column(Integer)
    comment = Column(String(255))
    algorithm = Column(String(255))
    clippolygon = Column(JsonPickleType(pickler=json))
    
    @classmethod
    def all(cls, session):
        return session.query(Georeferenzierungsprozess).order_by(desc(Georeferenzierungsprozess.id))
    
    @classmethod
    def arePendingProcessForMapId(cls, mapId, session):
        """ Function should check if there exist parallel unprocessed process processes in the database.
         
        Case 1.) Multiple unprocessed process processes with type "new" and overwrites 0
        Case 2.) Multiple unprocessed process processes with type "update" and the same overwrite id
         
        :type cls: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess
        :type mapId: str
        :type session: sqlalchemy.orm.session.Session
        :return: bool """
        # at first get the actual overwrite id
        actualOverwriteProcess = cls.getActualGeoreferenceProcessForMapId(mapId, session)
         
        # at first check if there are unprocessed process processes with type new
        if actualOverwriteProcess is None:
            # check if there exist unprocessed process process for this id with type new
            unprocssedProcessOfTypeNew = session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.mapid == mapId)\
                .filter(Georeferenzierungsprozess.processed == False)\
                .filter(Georeferenzierungsprozess.type == "new").all()
         
            # there are more than one unprocessed and new georeferences processes 
            if len(unprocssedProcessOfTypeNew) > 0:
                return True
             
            raise ProcessIsInvalideException('There is no activated process process for this map sheet, ...')
         
        # now check if there exist concurrent update processes
        actualOverwriteId = actualOverwriteProcess.id
        georefProcesses = session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.mapid == mapId)\
            .filter(Georeferenzierungsprozess.overwrites == actualOverwriteId)\
            .filter(Georeferenzierungsprozess.isactive == False).all()
        if len(georefProcesses) > 0:
            return True
        return False
    
    @classmethod
    def clearRaceConditions(cls, georefObj, dbsession):
        """ Function clears race condition for a given process process
        
        :type cls: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess
        :type georefObj: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess
        :type dbsession: sqlalchemy.orm.session.Session
        :return: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess """
        concurrentObjs = dbsession.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.mapid == georefObj.mapid)\
            .filter(Georeferenzierungsprozess.type == georefObj.type)\
            .filter(Georeferenzierungsprozess.overwrites == georefObj.overwrites)\
            .order_by(desc(Georeferenzierungsprozess.timestamp)).all()
            
        # there are no race conflicts
        if len(concurrentObjs) == 1:
            return georefObj
        
        # there are race conflicts
        for i in range(1, len(concurrentObjs)):
            dbsession.delete(concurrentObjs[i])
        return concurrentObjs[0]
    
    @classmethod
    def isGeoreferenced(cls, mapId, session):
        georefProcess = session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.mapid == mapId)\
            .filter(Georeferenzierungsprozess.isactive == True)\
            .order_by(desc(Georeferenzierungsprozess.timestamp)).first()
        if georefProcess is None:
            return False
        return True
     
    @classmethod
    def by_id(cls, id, session):
        return session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.id == id).first()

    @classmethod
    def getActualGeoreferenceProcessForMapId(cls, mapId, session):
        return session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.mapid == mapId)\
            .filter(Georeferenzierungsprozess.isactive == True).first()

    @classmethod
    def getUnprocessedObjectsOfTypeNew(cls, session):
        """ Gives back all process process of type "new" which are unprocessed. Important is the distinct operatore, which
        ignore race conflicts and gives in this case only one process back.

        :type cls: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess
        :type dbsession: sqlalchemy.orm.session.Session
        :return: List.<georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess> """
        return session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.processed == False)\
            .filter(Georeferenzierungsprozess.adminvalidation != 'invalide')\
            .filter(Georeferenzierungsprozess.type == 'new')\
            .filter(Georeferenzierungsprozess.overwrites == 0)\
            .distinct(Georeferenzierungsprozess.mapid)

    @classmethod
    def getUnprocessedObjectsOfTypeUpdate(cls, session):
        """ Gives back all process process of type "Update" which are unprocessed. Important is the distinct operatore, which
        ignore race conflicts and gives in this case only one process back.

        :type cls: georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess
        :type dbsession: sqlalchemy.orm.session.Session
        :return: List.<georeference.models.vkdb.georeferenzierungsprozess.Georeferenzierungsprozess> """
        return session.query(Georeferenzierungsprozess).filter(Georeferenzierungsprozess.processed == False)\
            .filter(Georeferenzierungsprozess.adminvalidation != 'update')\
            .filter(Georeferenzierungsprozess.type == 'new')\
            .filter(Georeferenzierungsprozess.overwrites == 0)\
            .distinct(Georeferenzierungsprozess.mapid)

    def setActive(self):
        """ Sets the georeference process to active. If - isactive - is set to True - processed - has also to be set
            to True, in any cases.
        :return:
        """
        self.processed = True
        self.isactive = True

    def setDeactive(self):
        """ Sets the georeference process to deactive.

        :return:
        """
        self.isactive = False