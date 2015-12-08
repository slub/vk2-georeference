'''
Created on Jul 21, 2014

@author: mendt
'''
import argparse, subprocess, logging, os, sys, shutil
from georeference.utils.logger import createLogger

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH_PARENT = os.path.abspath(os.path.join(BASE_PATH, os.pardir))
sys.path.insert(0, BASE_PATH)
sys.path.append(BASE_PATH_PARENT)


def buildTMSCache(source_path, target_dir, logger, srs = 4314):
    file_name, file_extension = os.path.splitext(os.path.basename(source_path))
    
    # check if target dir extist
    tms_target_dir = os.path.join(target_dir, file_name)
    if os.path.exists(tms_target_dir):
        logger.info('Remove old tsm cache directory ...')
        shutil.rmtree(tms_target_dir)
                  
    os.makedirs(tms_target_dir)
    command = 'gdal2tiles.py -z 1-15 -w none -s EPSG:%s %s %s'%(srs, source_path, tms_target_dir)
    # now execute command
    logger.info('Execute - %s'%command)
    try:
        subprocess.check_call(command, shell = True)
    except:
        pass   
        return None
    return None

def updateTMSCache(source_dir, target_dir, logger):
    """ Processes for updating the cache 
            
    Arguments:
        source_dir {string}
        target_dir (string)
        logger {Logger} """

    logger.info(' Get files from source directory ...')
    directory_content = os.listdir(source_dir)
    for file in directory_content:
        buildTMSCache(os.path.join(source_dir, file), target_dir, 4314, logger)
    
        


    
""" Main """    
if __name__ == '__main__':
    script_name = 'UpdateTMSCache.py'
    parser = argparse.ArgumentParser(description = 'This scripts create a TMS Cache for all georeferenced maps.', prog = 'Script %s'%script_name)
    parser.add_argument('--log_file', help='define a log file')
    parser.add_argument('--target_dir', help='Directory where the TMS directories should be placed.')
    parser.add_argument('--source_dir', help='Source directory') 
    arguments = parser.parse_args()
    
    # create logger
    if arguments.log_file:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = createLogger('UpdateTMSCache', logging.DEBUG, logFile=''.join(arguments.log_file), formatter=formatter)
    else: 
        logger = createLogger('UpdateTMSCache', logging.DEBUG)       

    updateTMSCache(arguments.source_dir, arguments.target_dir,logger)
