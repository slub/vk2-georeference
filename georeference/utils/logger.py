# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
import logging

def createLogger(name, logLevel, logFile=None, formatter=None, handler = None):
    """ Initialize a logger
    
    :param string: name
    :param int: logLevel
    :param string: logFile (Default=None)
    :param logging.Formatter: formatter (Default=None)
    :param logging.Handler: handler (Default=None)
    :return: logging.Logger """
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(logLevel)
    
    if logFile and formatter:
        logHandler = logging.FileHandler(logFile)
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
    elif handler:
        logger.addHandler(handler)
        
    return logger

def getLoggerFileHandler(file, formatter):
    """ Create a logger file handler
    
    :param string file
    :param string: formatter 
    :return: logging.FileHandler """
    formatter = logging.Formatter(formatter)
    handler = logging.FileHandler(file)
    handler.setFormatter(formatter)
    return handler