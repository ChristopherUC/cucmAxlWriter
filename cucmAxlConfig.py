#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import os  # directories
import logging  # debug
import json  # config file read/write
import socket  # download ssl cert, check IP vs hostname
import ssl  # download ssl cert
import OpenSSL  # download ssl cert

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('configDebug.log', mode='w')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Begin cucmAxlConfig Logging")


class cucmAxlConfig:
    # holds config data for AXL connection to CUCM

    # default /axlsqltoolkit/schema/current/AXLAPI.wsdl
    __wsdlFileName = 'axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
    __cucmCfgFileName = 'ucm.cfg'
    __cucmCertFileName = ''
    __cucmUrl = ''
    __cucmUsername = ''
    __cucmPassword = ''
    __cucmVerify = ''
    __localDir = os.getcwd()

    def __init__(self):
        wsdlFileFound = self.checkFileExists(self.__wsdlFileName,
                                             self.__localDir)
        if not wsdlFileFound:
            logger.error("This version of cucmAxlWriter is expecting" +
                         " the UCM 11.5 WSDL file.")
            logger.error("If you choose to use a different version of" +
                         "the WSDL your results may vary.")
            logger.error("The 11.5 version WSDL file must be placed in %s",
                         os.path.join(self.__localDir, self.__wsdlFileName))
            raise Exception("WSDL File NOT found. Unrecoverable error.")
        else:
            self.__wsdlFileName = os.path.join(self.__localDir,
                                               self.__wsdlFileName)

        cucmCfgFileFound = self.checkFileExists(self.__cucmCfgFileName,
                                                self.__localDir)
        if not cucmCfgFileFound:
            print("The CUCM Cfg file was not found.")
            print("Generating a new config file.")
            self.__buildCucmCfgFile()
        self.__cucmCfgFileName = os.path.join(self.__localDir,
                                              self.__cucmCfgFileName)
        self.__loadCucmCfgFile(self.__cucmCfgFileName)

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

    def getCucmUsername(self):
        return self.__cucmUsername

    def __setCucmUsername(self, username):
        self.__cucmUsername = username

    def getCucmPassword(self):
        return self.__cucmPassword

    def __setCucmPassword(self, password):
        self.__cucmPassword = password

    def getCucmUrl(self):
        return self.__cucmUrl

    def getCucmAxlUrl(self):
        return 'https://{0}:8443/axl/'.format(self.__cucmUrl)

    def __setCucmUrl(self, ipOrHostname):
        self.__cucmUrl = ipOrHostname

    def getCucmVerify(self):
        return self.__cucmVerify

    def __setCucmVerify(self, verify):
        self.__cucmVerify = verify
        if self.getCucmVerify():
            certFileExists = self.checkFileExists(self.__cucmCertFileName,
                                                  self.__localDir)
            if not certFileExists:
                self.__downloadCucmCert()

    def getCucmCert(self):
        return self.__cucmCertFileName

    def __downloadCucmCert(self):
        hostname = self.getCucmUrl()
        port = 443
        logger.debug("using %s:%s to download cert", hostname, port)
        cert = ssl.get_server_certificate((hostname, port))
        x509 = OpenSSL.crypto.load_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, cert)
        certExport = OpenSSL.crypto.dump_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, x509)
        certFileName = os.path.join(self.__localDir,
                                    '{0}.pem'.format(hostname))
        with open(certFileName, 'wb') as certFile:
            certFile.write(certExport)
            logger.debug("Cert file saved to %s", certFileName)
        self.__setCucmCert(certFileName)

    def __setCucmCert(self, certFileName):
        self.__cucmCertFileName = certFileName

    def getCucmCfgFileName(self):
        return self.__cucmCfgFileName

    def __loadCucmCfgFile(self, filename):
        logger.debug("Reading from file")
        try:
            with open(filename) as cucmCfgFile:
                cucmCfg = json.load(cucmCfgFile)
                self.__setCucmUsername(cucmCfg['username'])
                self.__setCucmPassword(cucmCfg['password'])
                self.__setCucmUrl(cucmCfg['url'])
                self.__setCucmVerify(cucmCfg['verify'])
                self.__setCucmCert(cucmCfg['verifyFile'])
                logger.debug("File Read successfully")
        except Exception as e:
            logger.debug("Unable to open Config file")
            os.remove(self.getCucmCfgFileName())

    def __buildCucmCfgFile(self):
        logger.debug("Building new config file")

        # TODO: Try block for sanitization
        username = input("UCM AXL Username: ")

        # TODO: Try block for sanitization
        password = input("UCM Password: ")

        print("NOTE: Certificates cannot be used if an IP Address is provided")
        # TODO: Try block for sanitization
        url = input("UCM hostname or IP Address: ")
        self.__setCucmUrl(url)  # temp workaround so cert download will work
        # consider refactoring

        # check if valid IP address by borrowing from socket
        try:
            socket.inet_aton(url)
            logger.debug("Bypassing certificate download")
            verify = False
        except socket.error:
            # TODO: Try block for sanitization
            verify = input("Use Certificates (y/n): ")
            if verify == 'y':
                logger.debug("Downloading certificate")
                self.__downloadCucmCert()
                certFileExists = self.checkFileExists(self.getCucmCert(),
                                                      self.__localDir)
                if certFileExists:
                    verify = True
                else:
                    verify = False
            else:
                logger.debug("Bypassing certificate download")
                verify = False

        data = {'username': username, 'password': password, 'url': url,
                'verify': verify, 'verifyFile': self.getCucmCert()}
        with open('ucm.cfg', 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)
