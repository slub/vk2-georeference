'''
Created on Apr 28, 2015

@author: mendt
'''
from vkviewer.python.utils.idgenerator import createOAI

from georeference.settings import GN_SETTINGS
from georeference.csw.InsertMetadata import insertMetadata
from georeference.csw.CswTransactionBinding import gn_transaction_delete

def pushMapObjToCsw(mapObj, dbsession, logger):
    """ Function push a given map record to a csw instance 
    
    :type mapObj: vkviewer.python.models.vkdb.Map
    :type dbsession: sqlalchemy.orm.session.Session
    :type logger: logging.Logger """
    insertMetadata(id=mapObj.id,db=dbsession,logger=logger)
    
def removeMapObjFromCsw(mapObj, dbsession, logger):
    """ Function push a given map record to a csw instance 
    
    :type mapObj: vkviewer.python.models.vkdb.Map
    :type dbsession: sqlalchemy.orm.session.Session
    :type logger: logging.Logger """
    oai = createOAI(mapObj.id)
    gn_transaction_delete(oai, GN_SETTINGS['gn_username'], GN_SETTINGS['gn_password'], logger)