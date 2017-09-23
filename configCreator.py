#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import sys
import os  # directories
import socket  # download ssl cert, check IP vs hostname
import logging
import json
import ssl  # download ssl cert
import OpenSSL  # download ssl cert
from optparse import OptionParser
from appConfig import appConfig

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


class configCreator(appConfig):
    # builds a config file for UC apps

    def __init__(self, cfgFileName):
        appConfig.__init__(self, cfgFileName)
        self._appCfgFileName = cfgFileName
        appCfgFileFound = self.checkFileExists(self._appCfgFileName,
                                               self._localDir)
        if not appCfgFileFound:
            print("The specified Config file was not found.")
            print("Generating a new config file.")
            self._buildAppCfgFile(options.filename)
        self._appCfgFileName = os.path.join(self._localDir,
                                            self._appCfgFileName)
        self._loadAppCfgFile(self._appCfgFileName)
        print("Current username is: ", self.getAppUsername())
        print("Current password is: ", self.getAppPassword())
        print("Current url is: ", self.getAppHost())
        print("Current verify mode is: ", self.getAppVerify())
        print("Current Cert File  is: ", self.getAppCert())

    def _setAppVerify(self, verify):
        self._appVerify = verify
        if self.getAppVerify():
            certFileExists = self.checkFileExists(self._appCertFileName,
                                                  self._localDir)
            if not certFileExists:
                self._downloadAppCert()

    def _downloadAppCert(self):
        hostname = self.getAppHost()
        port = 443
        confLogger.debug("using %s:%s to download cert", hostname, port)
        cert = ssl.get_server_certificate((hostname, port))
        x509 = OpenSSL.crypto.load_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, cert)
        certExport = OpenSSL.crypto.dump_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, x509)
        certFileName = os.path.join(self._localDir,
                                    '{0}.pem'.format(hostname))
        with open(certFileName, 'wb') as certFile:
            certFile.write(certExport)
            confLogger.debug("Cert file saved to %s", certFileName)
        self._setAppCert(certFileName)

    def _buildAppCfgFile(self, buildFilename):
        confLogger.debug("Building new config file")

        # TODO: Try block for sanitization
        username = input("API Username: ")

        # TODO: Try block for sanitization
        password = input("API Password: ")

        print("NOTE: Certificates cannot be used if an IP Address is provided")
        # TODO: Try block for sanitization
        url = input("Server hostname or IP Address: ")
        self._setAppHost(url)  # temp workaround so cert download will work
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
                self._downloadAppCert()
                certFileExists = self.checkFileExists(self.getAppCert(),
                                                      self._localDir)
                if certFileExists:
                    verify = True
                else:
                    verify = False
                    self.__setAppCert(False)
            else:
                confLogger.debug("Bypassing certificate download")
                verify = False
                self.__setAppCert(False)

        data = {'username': username, 'password': password, 'url': url,
                'verify': verify, 'verifyFile': self.getAppCert()}
        with open(buildFilename, 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)


print("Generating a new ", options.filename)
myConfig = configCreator(options.filename)
