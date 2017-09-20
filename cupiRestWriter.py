#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import sys
import logging
import requests
# from requests import Session
# from requests.auth import HTTPBasicAuth
from cupiRestConfig import cupiRestConfig

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
cupiRLogger.addHandler(logging.StreamHandler(sys.stdout))
cupiRLogger.info("Begin CUPI Writer Info Logging")
cupiRLogger.debug("Begin CUPI Writer Debug Logging")


class cupiRestWriter:

    headers = {'Content-Type': 'application/xml'}  # server accepts
    template = 'voicemailusertemplate'
    myCxnConfig = ''
    __newUserXml = ''

    def __init__(self, Alias, Extension, FirstName, LastName, EmailAddress):
        cupiRLogger.info("Rest Writer Started")
        self.myCxnConfig = cupiRestConfig()

        self.__newUserXml = self.genNewUserXML(FirstName,
                                               LastName,
                                               Alias,
                                               EmailAddress,
                                               Extension)
        cupiRLogger.debug(self.__newUserXml)

    def genNewUserXML(self, FirstName, LastName, Alias, EmailAddress,
                      DtmfAccessId):
        DisplayName = FirstName + " " + LastName
        SmtpAddress = Alias + "@" + self.myCxnConfig.getCxnUrl()

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

    def createNewVoicemail(self, newUserXml):
        vmCreateUrl = 'users?templateAlias=' + self.template
        url = self.myCxnConfig.getCxnRestlUrl() + vmCreateUrl
        resp = requests.post(url,
                             auth=(self.myCxnConfig.getCxnUsername(),
                                   self.myCxnConfig.getCxnPassword()),
                             verify=False,
                             data=newUserXml,
                             headers=self.headers)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST /{0} {1}'.format(vmCreateUrl,
                                                   resp.status_code))

    def getTemplate(self):
        getTemplateUrl = 'usertemplates'
        url = self.myCxnConfig.getCxnRestlUrl() + getTemplateUrl
        resp = requests.post(url,
                             auth=(self.myCxnConfig.getCxnUsername(),
                                   self.myCxnConfig.getCxnPassword()),
                             verify=False,
                             headers=self.headers)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST /{0} {1}'.format(getTemplateUrl,
                            resp.status_code))

    def deleteVoicemail(self):
        pass
