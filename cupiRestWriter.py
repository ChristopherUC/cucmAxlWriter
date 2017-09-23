#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

# import sys
import logging
import requests
from ucAppConfig import cxnAppConfig

import urllib3  # imported to disable the SAN warning for the cert
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

cupiRLogger = logging.getLogger(__name__)
cupiRLogger.setLevel(logging.DEBUG)
infoHandler = logging.FileHandler('cupiInfo.log', mode='w')
infoHandler.setLevel(logging.INFO)
debugHandler = logging.FileHandler('cupiDebug.log', mode='w')
debugHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
infoHandler.setFormatter(formatter)
debugHandler.setFormatter(formatter)
cupiRLogger.addHandler(infoHandler)
cupiRLogger.addHandler(debugHandler)
# cupiRLogger.addHandler(logging.StreamHandler(sys.stdout))
cupiRLogger.info("Begin CUPI Writer Info Logging")
cupiRLogger.debug("Begin CUPI Writer Debug Logging")


class cupiRestWriter:

    headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
    # server accepts XML, we request JSON in response
    template = 'voicemailusertemplate'
    myCxnConfig = ''
    __baseUrl = ''
    __newUserXml = ''
    __auth = ''

    def __init__(self, Alias, Extension, FirstName, LastName, EmailAddress):
        cupiRLogger.info("Rest Writer Started")
        self.myCxnConfig = cxnAppConfig('cxn.cfg')

        self.__newUserXml = self.genNewUserXML(FirstName,
                                               LastName,
                                               Alias,
                                               EmailAddress,
                                               Extension)
        cupiRLogger.debug(self.__newUserXml)
        self.__baseUrl = self.myCxnConfig.getAppApiUrl()
        self.__auth = (self.myCxnConfig.getAppUsername(),
                       self.myCxnConfig.getAppPassword())

    def genNewUserXML(self, FirstName, LastName, Alias, EmailAddress,
                      DtmfAccessId):
        DisplayName = FirstName + " " + LastName
        SmtpAddress = Alias + "@" + self.myCxnConfig.getAppHost()

        newUserXml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <User>
            <FirstName>{0}</FirstName>
            <LastName>{1}</LastName>
            <Alias>{2}</Alias>
            <DisplayName>{3}</DisplayName>
            <EmailAddress>{4}</EmailAddress>
            <SmtpAddress>{5}</SmtpAddress>
            <DtmfAccessId>{6}</DtmfAccessId>
        </User>'''.format(FirstName, LastName, Alias, DisplayName,
                          EmailAddress, SmtpAddress, DtmfAccessId)
        return newUserXml

    def createNewVoicemail(self):
        cupiRLogger.info("Create Voicemail Started")
        vmCreateUrl = 'users?templateAlias=' + self.template
        url = self.__baseUrl + vmCreateUrl
        resp = requests.post(url,
                             auth=(self.myCxnConfig.getAppUsername(),
                                   self.myCxnConfig.getAppPassword()),
                             verify=False,
                             data=self.__newUserXml,
                             headers=self.headers)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST /{0} {1}'.format(url,
                                                   resp.status_code))

    def getTemplate(self):
        getTemplateUrl = 'usertemplates'
        url = self.__baseUrl + getTemplateUrl
        resp = requests.post(url,
                             auth=(self.myCxnConfig.getAppUsername(),
                                   self.myCxnConfig.getAppPassword()),
                             verify=False,
                             headers=self.headers)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST /{0} {1}'.format(getTemplateUrl,
                            resp.status_code))

    def getVmObjectId(self, alias):
        # accept = 'Accept: application/json'
        vmGetUrl = 'users?query=(alias is {0})'.format(alias)
        url = self.__baseUrl + vmGetUrl
        resp = requests.get(url,
                            auth=(self.myCxnConfig.getAppUsername(),
                                  self.myCxnConfig.getAppPassword()),
                            verify=False,
                            headers=self.headers,
                            # accept=accept
                            )
        data = resp.json()
        return data['User']['ObjectId']
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('GET /{0} {1}'.format(vmGetUrl,
                                                  resp.status_code))

    def deleteVoicemail(self, alias):
        cupiRLogger.info("Delete Voicemail Started")
        userObjectId = self.getVmObjectId(alias)
        vmDeleteUrl = 'users/' + userObjectId
        url = self.__baseUrl + vmDeleteUrl
        resp = requests.delete(url,
                               auth=(self.myCxnConfig.getAppUsername(),
                                     self.myCxnConfig.getAppPassword()),
                               verify=False,
                               headers=self.headers)
        if resp.status_code != 204:
            # This means something went wrong.
            raise Exception('Delete /{0} {1}'.format(vmDeleteUrl,
                                                     resp.status_code))
