#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import os  # directories
import logging  # debug
import json  # config file read/write


cupiLogger = logging.getLogger(__name__)
cupiLogger.setLevel(logging.DEBUG)
handler = logging.FileHandler('configDebug.log', mode='w')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
handler.setFormatter(formatter)
cupiLogger.addHandler(handler)
cupiLogger.info("Begin cxnAxlConfig Logging")


class cupiRestConfig:
    # holds config data for REST connection to CXN

    __cxnCfgFileName = 'cxn.cfg'
    # __cxnCertFileName = ''
    __cxnUrl = ''
    __cxnUsername = ''
    __cxnPassword = ''
    __cxnVerify = 'False'
    __localDir = os.getcwd()

    def __init__(self):
        cxnCfgFileFound = self.checkFileExists(self.__cxnCfgFileName,
                                               self.__localDir)
        if not cxnCfgFileFound:
            print("The CXN Cfg file was not found.")
            print("Generating a new config file.")
            self.__buildCxnCfgFile()
        self.__cxnCfgFileName = os.path.join(self.__localDir,
                                             self.__cxnCfgFileName)
        self.__loadCxnCfgFile(self.__cxnCfgFileName)

    def checkFileExists(self, filename, directory):
        if not filename.startswith(directory):
            fileLocation = os.path.join(directory, filename)
        else:
            fileLocation = filename
        cupiLogger.debug("Checking for %s file in %s", filename, directory)
        fileExists = os.path.isfile(fileLocation)
        cupiLogger.debug("%s Exists=%s", filename, fileExists)
        if not fileExists:
            cupiLogger.debug("%s NOT Found", fileLocation)
            return fileExists
        cupiLogger.debug("%s file found", filename)
        return fileExists

    def getCxnUsername(self):
        return self.__cxnUsername

    def __setCxnUsername(self, username):
        self.__cxnUsername = username

    def getCxnPassword(self):
        return self.__cxnPassword

    def __setCxnPassword(self, password):
        self.__cxnPassword = password

    def getCxnUrl(self):
        return self.__cxnUrl

    def getCxnRestlUrl(self):
        return 'https://{0}/vmrest/'.format(self.getCxnUrl())

    def __setCxnUrl(self, ipOrHostname):
        self.__cxnUrl = ipOrHostname

    def getCxnCfgFileName(self):
        return self.__cxnCfgFileName

    def getCxnVerify(self):
        return self.__cucmVerify

    def __setCxnVerify(self, verify):
        self.__cucmVerify = verify

    def getCxnCert(self):
        return self.__cxnCertFileName

    def __setCxnCert(self, certFileName):
        self.__cxnCertFileName = certFileName

    def __loadCxnCfgFile(self, filename):
        cupiLogger.debug("Reading from file")
        try:
            with open(filename) as cxnCfgFile:
                cxnCfg = json.load(cxnCfgFile)
                self.__setCxnUsername(cxnCfg['username'])
                self.__setCxnPassword(cxnCfg['password'])
                self.__setCxnUrl(cxnCfg['url'])
                self.__setCxnVerify(cxnCfg['verify'])
                self.__setCxnCert(cxnCfg['verifyFile'])
                cupiLogger.debug("File Read successfully")
        except Exception as e:
            cupiLogger.debug("Unable to open Config file")
            os.remove(self.getCxnCfgFileName())

    def __buildCxnCfgFile(self):
        cupiLogger.debug("Building new config file")

        # TODO: Try block for sanitization
        username = input("CXN REST Username: ")

        # TODO: Try block for sanitization
        password = input("CXN Password: ")

        print("NOTE: Certificates cannot be used if an IP Address is provided")
        # TODO: Try block for sanitization
        url = input("CXN hostname or IP Address: ")
        self.__setCxnUrl(url)  # temp workaround so cert download will work
        # consider refactoring

        verify = False
        verifyFile = ''

        data = {'username': username, 'password': password, 'url': url,
                'verify': verify, 'verifyFile': verifyFile}
        with open('cxn.cfg', 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)
