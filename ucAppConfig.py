#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import os  # directories
import sys
import logging  # debug
import json  # config file read/write

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('ucAppConfigDebug.log', mode='w')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Begin ucAppConfig Logging")


class ucAppConfig:
    # holds config data for connection to UC Apps

    # default /axlsqltoolkit/schema/current/AXLAPI.wsdl
    __wsdlFileName = 'axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
    __appCfgFileName = ''
    __appCertFileName = ''
    __appUrl = ''
    __appUsername = ''
    __appPassword = ''
    __appVerify = ''
    __localDir = os.getcwd()

    def __init__(self, cfgFileName):
        self.__appCfgFileName = cfgFileName
        appCfgFileFound = self.checkFileExists(self.__appCfgFileName,
                                               self.__localDir)
        if not appCfgFileFound:
            print("The specified Config file was not found.")
            print("Generate a new config file using configCreator.py")
            raise Exception("Config File NOT found. Unrecoverable error.")
        self.__appCfgFileName = os.path.join(self.__localDir,
                                             self.__appCfgFileName)
        self.__loadAppCfgFile(self.__appCfgFileName)

        if 'ucm' in self.__appCfgFileName:
            wsdlFileFound = self.checkFileExists(self.__wsdlFileName,
                                                 self.__localDir)
            if not wsdlFileFound:
                logger.error("This version of cucmAxlWriter is expecting" +
                             " the UCM 11.5 WSDL file.")
                logger.error("If you choose to use a different version of" +
                             "the WSDL your results may vary.")
                logger.error("The 11.5 version WSDL file must be placed in %s",
                             os.path.join(self.__localDir,
                                          self.__wsdlFileName))
                raise Exception("WSDL File NOT found. Unrecoverable error.")
            else:
                self.__wsdlFileName = os.path.join(self.__localDir,
                                                   self.__wsdlFileName)

    def checkFileExists(self, filename, directory):
        if not filename.startswith(directory):
            fileLocation = os.path.join(directory, filename)
        else:
            fileLocation = filename
        logger.debug("Checking for %s file in %s", filename, directory)
        fileExists = os.path.isfile(fileLocation)
        logger.debug("%s Exists=%s", filename, fileExists)
        if not fileExists:
            logger.debug("%s NOT Found", fileLocation)
            return fileExists
        logger.debug("%s file found", filename)
        return fileExists

    def getwsdlFileName(self):
        return self.__wsdlFileName

    def getAppUsername(self):
        return self.__appUsername

    def __setAppUsername(self, username):
        self.__appUsername = username

    def getAppPassword(self):
        return self.__appPassword

    def __setAppPassword(self, password):
        self.__appPassword = password

    def getAppHost(self):
        return self.__appHost

    def __setAppHost(self, ipOrHostname):
        self.__appHost = ipOrHostname

    def getAppApiUrl(self):
        if 'ucm.cfg' in self.getAppCfgFileName():
            return 'https://{0}:8443/axl/'.format(self.getAppHost())
        if 'cxn.cfg' in self.getAppCfgFileName():
            return 'https://{0}/vmrest/'.format(self.getAppHost())

    def __setAppUrl(self, ipOrHostname):
        self.__appUrl = ipOrHostname

    def getAppVerify(self):
        return self.__appVerify

    def __setAppVerify(self, verify):
        self.__appVerify = verify

    def getAppCert(self):
        return self.__appCertFileName

    def __setAppCert(self, certFileName):
        self.__appCertFileName = certFileName

    def getAppCfgFileName(self):
        return self.__appCfgFileName

    def __loadAppCfgFile(self, filename):
        logger.debug("Reading from file")
        try:
            with open(filename) as appCfgFile:
                newCfg = json.load(appCfgFile)
                self.__setAppUsername(newCfg['username'])
                self.__setAppPassword(newCfg['password'])
                self.__setAppHost(newCfg['url'])
                self.__setAppVerify(newCfg['verify'])
                self.__setAppCert(newCfg['verifyFile'])
                logger.debug("File Read successfully")
        except Exception as e:
            logger.debug("Unable to open Config file")
            # os.remove(self.getAppCfgFileName())
            sys.exit(e)
