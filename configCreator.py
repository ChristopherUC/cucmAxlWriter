#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import sys
import os  # directories
import logging
import json  # config file read/write
import socket  # download ssl cert, check IP vs hostname
import ssl  # download ssl cert
import OpenSSL  # download ssl cert
from optparse import OptionParser

confLogger = logging.getLogger(__name__)
confLogger.setLevel(logging.DEBUG)
infoHandler = logging.FileHandler('CiscoInfo.log', mode='w')
infoHandler.setLevel(logging.INFO)
debugHandler = logging.FileHandler('CiscoDebug.log', mode='w')
debugHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
infoHandler.setFormatter(formatter)
debugHandler.setFormatter(formatter)
confLogger.addHandler(infoHandler)
confLogger.addHandler(debugHandler)
# confLogger.addHandler(logging.StreamHandler(sys.stdout))
confLogger.info("Begin configCreator Info Logging")
confLogger.debug("Begin configCreator Debug Logging")

parser = OptionParser()
parser.add_option("--ccm", action="store_const", const="ucm.cfg",
                  help="Setup config for Comm. Manager", dest="filename")
parser.add_option("--cxn", action="store_const", const="cxn.cfg",
                  help="Setup config for Voicemail", dest="filename")
(options, args) = parser.parse_args()

if not options.filename:
    parser.error("No option selected. Use -h or --help for help")
    sys.exit()


class configCreator:
    # generates a config file for UC apps

    __newCfgFileName = ''
    __newCertFileName = ''
    __newHost = ''
    __newUsername = ''
    __newPassword = ''
    __newVerify = ''
    __localDir = os.getcwd()

    def __init__(self, cfgFileName):
        self.__newCfgFileName = cfgFileName
        newCfgFileFound = self.checkFileExists(self.__newCfgFileName,
                                               self.__localDir)
        if not newCfgFileFound:
            print("The specified Config file was not found.")
            print("Generating a new config file.")
            self.__buildNewCfgFile(options.filename)
        self.__newCfgFileName = os.path.join(self.__localDir,
                                             self.__newCfgFileName)
        self.__loadNewCfgFile(self.__newCfgFileName)
        print("Current username is: ", self.getNewUsername())
        print("Current password is: ", self.getNewPassword())
        print("Current url is: ", self.getNewHost())
        print("Current verify mode is: ", self.getNewVerify())
        print("Current Cert File  is: ", self.getNewCert())

    def checkFileExists(self, filename, directory):
        if not filename.startswith(directory):
            fileLocation = os.path.join(directory, filename)
        else:
            fileLocation = filename
        confLogger.debug("Checking for %s file in %s", filename, directory)
        fileExists = os.path.isfile(fileLocation)
        confLogger.debug("%s Exists=%s", filename, fileExists)
        if not fileExists:
            confLogger.debug("%s NOT Found", fileLocation)
            return fileExists
        confLogger.debug("%s file found", filename)
        return fileExists

    def getNewUsername(self):
        return self.__newUsername

    def __setNewUsername(self, username):
        self.__newUsername = username

    def getNewPassword(self):
        return self.__newPassword

    def __setNewPassword(self, password):
        self.__newPassword = password

    def getNewHost(self):
        return self.__newHost

    def __setnewHost(self, ipOrHostname):
        self.__newHost = ipOrHostname

    def getNewVerify(self):
        return self.__newVerify

    def __setNewVerify(self, verify):
        self.__newVerify = verify
        if self.getNewVerify():
            certFileExists = self.checkFileExists(self.__newCertFileName,
                                                  self.__localDir)
            if not certFileExists:
                self.__downloadNewCert()

    def getNewCert(self):
        return self.__newCertFileName

    def __downloadNewCert(self):
        hostname = self.getNewHost()
        port = 443
        confLogger.debug("using %s:%s to download cert", hostname, port)
        cert = ssl.get_server_certificate((hostname, port))
        x509 = OpenSSL.crypto.load_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, cert)
        certExport = OpenSSL.crypto.dump_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, x509)
        certFileName = os.path.join(self.__localDir,
                                    '{0}.pem'.format(hostname))
        with open(certFileName, 'wb') as certFile:
            certFile.write(certExport)
            confLogger.debug("Cert file saved to %s", certFileName)
        self.__setNewCert(certFileName)

    def __setNewCert(self, certFileName):
        self.__newCertFileName = certFileName

    def getNewCfgFileName(self):
        return self.__newCfgFileName

    def __loadNewCfgFile(self, filename):
        confLogger.debug("Reading from file")
        try:
            with open(filename) as newCfgFile:
                newCfg = json.load(newCfgFile)
                self.__setNewUsername(newCfg['username'])
                self.__setNewPassword(newCfg['password'])
                self.__setnewHost(newCfg['url'])
                self.__setNewVerify(newCfg['verify'])
                self.__setNewCert(newCfg['verifyFile'])
                confLogger.debug("File Read successfully")
        except Exception as e:
            confLogger.debug("Unable to open Config file")
            os.remove(self.getNewCfgFileName())

    def __buildNewCfgFile(self, buildFilename):
        confLogger.debug("Building new config file")

        # TODO: Try block for sanitization
        username = input("API Username: ")

        # TODO: Try block for sanitization
        password = input("API Password: ")

        print("NOTE: Certificates cannot be used if an IP Address is provided")
        # TODO: Try block for sanitization
        url = input("Server hostname or IP Address: ")
        self.__setnewHost(url)  # temp workaround so cert download will work
        # consider refactoring

        # check if valid IP address by borrowing from socket
        try:
            socket.inet_aton(url)
            confLogger.debug("Bypassing certificate download")
            verify = False
        except socket.error:
            # TODO: Try block for sanitization
            verify = input("Use Certificates (y/n): ")
            if verify == 'y':
                confLogger.debug("Downloading certificate")
                self.__downloadNewCert()
                certFileExists = self.checkFileExists(self.getNewCert(),
                                                      self.__localDir)
                if certFileExists:
                    verify = True
                else:
                    verify = False
            else:
                confLogger.debug("Bypassing certificate download")
                verify = False

        data = {'username': username, 'password': password, 'url': url,
                'verify': verify, 'verifyFile': self.getNewCert()}
        with open(buildFilename, 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)


print("Generating a new ", options.filename)

myConfig = configCreator(options.filename)
