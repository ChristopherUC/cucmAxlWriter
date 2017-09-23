#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import os  # directories
import logging  # debug
from appConfig import appConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('ucAppConfigDebug.log', mode='w')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Begin ucAppConfig Logging")


class ccmAppConfig(appConfig):
    # holds config data for connection to UC Apps

    # default /axlsqltoolkit/schema/current/AXLAPI.wsdl
    _wsdlFileName = 'axlsqltoolkit/schema/10.5/AXLAPI.wsdl'

    def __init__(self, cfgFileName):
        appConfig.__init__(self, cfgFileName)
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

    def getwsdlFileName(self):
        return self.__wsdlFileName

    def getAppApiUrl(self):
        return 'https://{0}:8443/axl/'.format(self.getAppHost())

    def __setAppUrl(self, ipOrHostname):
        self.__appUrl = ipOrHostname


class cxnAppConfig(appConfig):
    # holds config data for connection to UC Apps

    def __init__(self, cfgFileName):
        appConfig.__init__(self, cfgFileName)
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

    def getAppApiUrl(self):
        return 'https://{0}/vmrest/'.format(self.getAppHost())

    def __setAppUrl(self, ipOrHostname):
        self.__appUrl = ipOrHostname
