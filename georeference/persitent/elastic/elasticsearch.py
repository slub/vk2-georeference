'''
Created on May 12, 2015

@author: mendt
'''
import json
import requests

def deleteRecordFromEsById(key, esIndexUrl):
    """ Function deletes elastic search record by id.
    
    :type key: str
    :type esIndexUrl: str
    :return: dict """
    r = requests.delete("%s/%s"%(esIndexUrl, key))
    return r.json()

def getRecordFromEsById(key, esIndexUrl):
    """ Function queries elastic search record by id.
    
    :type key: str
    :type esIndexUrl: str
    :return: dict """
    r = requests.get("%s/%s"%(esIndexUrl, key))
    return r.json()

def pushRecordToEs(dataRecord, esIndexUrl, logger):
    """ Functions pushs a new record to a elasticsearch node.
    
    :type dataRecord: dict 
    :type esIndexUrl: str
    :type logger: logging.Logger
    :return: str Id of the inserted record """
    logger.debug(dataRecord)
    
    keys = dataRecord.keys()
    for key in keys:
        payload = json.dumps(dataRecord[key])
        r = requests.put("%s/%s"%(esIndexUrl, key), data=payload)
        logger.debug('Record was pushed to elasticsearch - status: %s'%r.status_code)
        return key