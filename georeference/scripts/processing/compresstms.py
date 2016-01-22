# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Jacob Mendt

Created on 22.01.16

@author: mendt

The following scripts compresses all files within a tms cache. It is based on the PIL library.
'''
import argparse
import os
from PIL import Image

def compressTMSCache(path):
    """ Functions runs a pngs compression on the given tms cache.

    :type str: path
    :return:
    """
    print 'Run png compression on %s ...' % path
    pngs = getPngsInDirTree(path)
    for png in pngs:
        Image.open(png).convert('RGBA').quantize(method=2).save(png)

def getPngsInDirTree(baseDir):
    """ Functions iteratore of the baseDir and the subdirectory tree and and returns a list of pngs paths found
        in the directory structure.

        :type baseDir: str
        :return: list<str>
    """
    def getAllPngsFromFilesList(baseDir, files):
        """ Functions returns all pngs within a files list.

            :type baseDir: str
            :type files: list<str>
            :return: list<str>
        """
        pngs = []
        for file in files:
            if os.path.splitext(file)[1][1:] == 'png':
                pngs.append(os.path.join(baseDir, file))
        return pngs

    allPngs = []
    for root, dirs, files in os.walk(baseDir):
        # first check that directory doesn't start with "."
        dirName = str(root).rsplit('/')[-1]
        # only look in directories which doesn't start with "."
        if dirName[0] is not '.':
            allPngs.extend(getAllPngsFromFilesList(root, files))
    return allPngs


if __name__ == '__main__':
    script_name = 'compresstms.py'
    parser = argparse.ArgumentParser(description = 'The scripts tooks a TMS cache as input and runs a compression of the contained pngs files.', prog = 'Script %s'%script_name)
    parser.add_argument('tms', metavar='TMS_DIR', type=str, help='Path to the TMS cache.')
    arguments = parser.parse_args()

    tmsPath = os.path.abspath(arguments.tms) if os.path.exists(arguments.tms) else None

    if tmsPath is None or not os.path.exists(tmsPath):
        raise 'TMS directory doesn\'t exists!'

    compressTMSCache(tmsPath)