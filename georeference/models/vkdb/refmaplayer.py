'''
Created on Jan 17, 2014

@author: mendt
'''
from sqlalchemy import Column
from sqlalchemy import Integer
from georeference.models.meta import Base


class RefMapLayer(Base):
    __tablename__ = 'refmaplayer'
    __table_args__ = {'extend_existing':True}
    layerid = Column(Integer, primary_key=True)
    mapid = Column(Integer, primary_key=True)
    
    @classmethod
    def by_id(cls, layerid, mapid, session):
        return session.query(RefMapLayer).filter(RefMapLayer.layerid == layerid).filter(RefMapLayer.mapid == mapid).first()

