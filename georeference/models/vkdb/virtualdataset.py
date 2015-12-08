from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import desc
from georeference.models.meta import Base
from georeference.models.vkdb.geometry import Geometry



class Virtualdataset(Base):
    __tablename__ = 'virtualdatasets'
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key=True)
    path = Column(String(255))
    timestamp = Column(DateTime(timezone=False))
    boundingbox = Column(Geometry)   
    lastupdate = Column(String(255))
    
    @classmethod
    def all(cls, session):
        return session.query(Virtualdataset).order_by(desc(Virtualdataset.id))

    
    @classmethod
    def by_id(cls, id, session):
        return session.query(Virtualdataset).filter(Virtualdataset.id == id).first()
    
    @classmethod 
    def by_timestamp(cls, timestamp, session):
        return session.query(Virtualdataset).filter(Virtualdataset.timestamp == timestamp).first()

    def setPath(self, path, dbsession):
        """ Update the path of the virtualdataset.

        :type str: path
        :type sqlalchemy.orm.session.Session: dbsession
        """
        self.path = path
        self.lastupdate = str(datetime.now())

        # update bbox
        query = "UPDATE virtualdatasets SET boundingbox = ( SELECT st_setsrid(st_envelope(st_extent(boundingbox)),4314) \
            FROM (SELECT map.boundingbox as boundingbox, metadata.timepublish as zeit FROM map, metadata WHERE map.maptype = 'M' AND map.isttransformiert = True \
            AND map.id = metadata.mapid AND EXTRACT('year' from metadata.timepublish) = %s) as foo) WHERE id = %s;"
        dbsession.execute(query%(self.timestamp.year, self.id))