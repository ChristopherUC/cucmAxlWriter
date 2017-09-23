#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import os  # directories
import sys
import logging
import json  # config file read/write

appConfLogger = logging.getLogger(__name__)
appConfLogger.setLevel(logging.DEBUG)
infoHandler = logging.FileHandler('CiscoInfo.log', mode='w')
infoHandler.setLevel(logging.INFO)
debugHandler = logging.FileHandler('CiscoDebug.log', mode='w')
debugHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
infoHandler.setFormatter(formatter)
debugHandler.setFormatter(formatter)
appConfLogger.addHandler(infoHandler)
appConfLogger.addHandler(debugHandler)
# appConfLogger.addHandler(logging.StreamHandler(sys.stdout))
appConfLogger.info("Begin configCreator Info Logging")
appConfLogger.debug("Begin configCreator Debug Logging")


class appConfig:
    # holds a config file for UC apps

    _appCfgFileName = ''
    _appCertFileName = ''
    _appHost = ''
    _appUsername = ''
    _appPassword = ''
    _appVerify = ''
    _localDir = os.getcwd()

    def __init__(self, cfgFileName):
        self._appCfgFileName = cfgFileName
        appCfgFileFound = self.checkFileExists(self._appCfgFileName,
                                               self._localDir)

        if appCfgFileFound:
            self._appCfgFileName = os.path.join(self._localDir,
                                                self._appCfgFileName)
            self._loadAppCfgFile(self._appCfgFileName)
        else:
            print("The specified Config file was not found.")
            print("You must generate a new config file with configCreator.")

    def checkFileExists(self, filename, directory):
        if not filename.startswith(directory):
            fileLocation = os.path.join(directory, filename)
        else:
            fileLocation = filename
        appConfLogger.debug("Checking for %s file in %s", filename, directory)
        fileExists = os.path.isfile(fileLocation)
        appConfLogger.debug("%s Exists=%s", filename, fileExists)
        if not fileExists:
            appConfLogger.debug("%s NOT Found", fileLocation)
            return fileExists
        appConfLogger.debug("%s file found", filename)
        return fileExists

    def getAppUsername(self):
        return self._appUsername

    def _setAppUsername(self, username):
        self._appUsername = username

    def getAppPassword(self):
        return self._appPassword

    def _setAppPassword(self, password):
        self._appPassword = password

    def getAppHost(self):
        return self._appHost

    def _setAppHost(self, ipOrHostname):
        self._appHost = ipOrHostname

    def getAppVerify(self):
        return self._appVerify

    def _setAppVerify(self, verify):
        self._appVerify = verify
        if self.getAppVerify():
            certFileExists = self.checkFileExists(self._appCertFileName,
                                                  self._localDir)
            if not certFileExists:
                raise Exception("Verify=True but no cert file exists: %s",
                                self._appCertFileName)

    def getAppCert(self):
        return self._appCertFileName

    def _setAppCert(self, certFileName):
        self._appCertFileName = certFileName

    def getAppCfgFileName(self):
        return self._appCfgFileName

    def _loadAppCfgFile(self, filename):
        appConfLogger.debug("Reading from file")
        try:
            with open(filename) as appCfgFile:
                appCfg = json.load(appCfgFile)
                self._setAppUsername(appCfg['username'])
                self._setAppPassword(appCfg['password'])
                self._setAppHost(appCfg['url'])
                self._setAppCert(appCfg['verifyFile'])
                self._setAppVerify(appCfg['verify'])
                appConfLogger.debug("File Read successfully")
        except Exception as e:
            appConfLogger.debug("Unable to open Config file")
            # os.remove(self.getAppCfgFileName())
            sys.exit(e)
