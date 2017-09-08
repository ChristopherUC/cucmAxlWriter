#! /usr/local/bin/python3
# cucmAxlConfig.py
# Christopher Phillips - 2017-08-30

import os  # directories
import logging  # debug
import json  # config file read/write

import socket  # download ssl cert, check IP vs hostname
import ssl  # download ssl cert
import OpenSSL  # pip install pyopenssl, # download ssl cert

logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s- %(message)s')
# logging.disable(logging.DEBUG)


class cucmAxlConfig:
    # holds config data for CUCM
    def __init__(self):
        # default /axlsqltoolkit/schema/current/AXLAPI.wsdl
        self.__wsdlFileName = '/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
        # default /ucm.cfg
        self.__cucmCfgFileName = '/ucm.cfg'
        self.__cucmCertFileName = ''
        self.__cucmUrl = ''
        self.__cucmUsername = ''
        self.__cucmPassword = ''
        self.__cucmVerify = ''
        self.__localDir = os.getcwd()
        self.factory = ''
        self.service = ''

        wsdlFileFound = self.checkFileExists(self.__wsdlFileName,
                                             self.__localDir)
        if not wsdlFileFound:
            print("This version of cucmAxlWriter is expecting" +
                  " the UCM 11.5 WSDL file.")
            print("If you choose to use a different version of" +
                  "the WSDL your results may vary.")
            print("The 11.5 version CUCM WSDL file must be placed in {0}"
                  .format(self.__localDir+self.__wsdlFileName))
            exit(-1)
        else:
            self.__wsdlFileName = self.__localDir + self.__wsdlFileName

        cucmCfgFileFound = self.checkFileExists(self.__cucmCfgFileName,
                                                self.__localDir)
        if not cucmCfgFileFound:
            print("The CUCM Cfg file was not found.")
            print("Generating a new config file.")
            self.__buildCucmCfgFile()
        self.__cucmCfgFileName = self.__localDir + self.__cucmCfgFileName
        self.__loadCucmCfgFile(self.__cucmCfgFileName)

        from zeep import Client
        from zeep.cache import SqliteCache
        from zeep.transports import Transport
        logging.getLogger('zeep.transports').setLevel(logging.DEBUG)

        cache = SqliteCache(path='/tmp/wsdlsqlite.db', timeout=60)
        transport = Transport(cache=cache)
        client = Client(self.getwsdlFileName(), transport=transport)

        from requests import Session
        from requests.auth import HTTPBasicAuth

        session = Session()
        if self.getCucmVerify():
            logging.info("Session Security ENABLED")
            session.verify = self.getCucmCert()
        else:
            logging.info("Session Security DISABLED")
            session.verify = self.getCucmVerify()
        logging.info("Session Created")
        session.auth = HTTPBasicAuth(self.getCucmUsername(),
                                     self.getCucmPassword())
        logging.info("Auth Created")

        client = Client(wsdl=self.getwsdlFileName(),
                        transport=Transport(session=session))
        logging.info("Client Created")

        self.factory = client.type_factory('ns0')
        logging.info("Factory Created")

        self.service = client.create_service(
            "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
            self.getCucmAxlUrl())
        logging.info("Service Created")

    def checkFileExists(self, filename, directory):
        if directory not in filename:
            fileLocation = directory + filename
        else:
            fileLocation = filename
        logging.debug("Checking for {0} file in {1}"
                      .format(filename, directory))
        fileExists = os.path.isfile(fileLocation)
        logging.debug("Exists={0}".format(fileExists))
        if not fileExists:
            logging.debug("{0} NOT Found".format(fileLocation))
            return fileExists
        logging.debug("{0} file found".format(filename))
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
        logging.debug("using {0}:{1} to download cert".format(hostname, port))
        cert = ssl.get_server_certificate((hostname, port))
        x509 = OpenSSL.crypto.load_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, cert)
        certExport = OpenSSL.crypto.dump_certificate(
                                            OpenSSL.crypto.FILETYPE_PEM, x509)
        certFileName = self.__localDir+'/{0}.pem'.format(hostname)
        with open(certFileName, 'wb') as certFile:
            certFile.write(certExport)
            logging.debug("Cert file saved to {0}".format(certFileName))
        self.__setCucmCert(certFileName)

    def __setCucmCert(self, certFileName):
        self.__cucmCertFileName = certFileName

    def getCucmCfgFileName(self):
        return self.__cucmCfgFileName

    def __loadCucmCfgFile(self, filename):
        logging.debug("Reading from file")
        try:
            with open(filename) as cucmCfgFile:
                cucmCfg = json.load(cucmCfgFile)
                self.__setCucmUsername(cucmCfg['username'])
                self.__setCucmPassword(cucmCfg['password'])
                self.__setCucmUrl(cucmCfg['url'])
                self.__setCucmVerify(cucmCfg['verify'])
                self.__setCucmCert(cucmCfg['verifyFile'])
                logging.debug("File Read successfully")
        except Exception as e:
            logging.debug("Unable to open Config file")
            os.remove(self.getCucmCfgFileName())

    def __buildCucmCfgFile(self):
        logging.debug("Building new config file")

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
            logging.debug("Bypassing certificate download")
            verify = False
        except socket.error:
            # TODO: Try block for sanitization
            verify = input("Use Certificates (y/n): ")
            if verify == 'y':
                logging.debug("Downloading certificate")
                self.__downloadCucmCert()
                certFileExists = self.checkFileExists(self.getCucmCert(),
                                                      self.__localDir)
                if certFileExists:
                    verify = True
                else:
                    verify = False
            else:
                logging.debug("Bypassing certificate download")
                verify = False

        data = {'username': username, 'password': password, 'url': url,
                'verify': verify, 'verifyFile': self.getCucmCert()}
        with open('ucm.cfg', 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)
