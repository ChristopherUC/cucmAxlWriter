#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

# import sys
import logging
import requests
import json
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

    myCxnConfig = ''
    __headers = {"Content-Type": "application/json",
                 "Accept": "application/json"}
    __baseUrl = ''
    __auth = ''
    __verify = ''
    __template = 'voicemailusertemplate'
    _newUserData = ''
    _alias = ''
    _extension = ''

    def __init__(self, Alias, Extension, FirstName, LastName, EmailAddress):
        cupiRLogger.info("Rest Writer Started")
        self._alias = Alias
        self._extension = Extension
        self.myCxnConfig = cxnAppConfig('cxn.cfg')

        if '!' in FirstName or '!' in LastName:
            # Get from AD User
            tempFirstName = "Fake"
            tempLastName = "User"
        else:
            tempFirstName = FirstName
            tempLastName = LastName
        self._newUserData = self.getNewUserJSON(tempFirstName,
                                                tempLastName,
                                                Alias,
                                                EmailAddress,
                                                Extension)
        cupiRLogger.debug(self._newUserData)
        self.__baseUrl = self.myCxnConfig.getAppApiUrl()
        self.__auth = (self.myCxnConfig.getAppUsername(),
                       self.myCxnConfig.getAppPassword())
        self.__verify = self.myCxnConfig.getAppCert()

    def getNewUserJSON(self, FirstName, LastName, Alias, EmailAddress,
                       DtmfAccessId):
        DisplayName = FirstName + " " + LastName
        SmtpAddress = Alias + "@" + self.myCxnConfig.getAppHost()
        return json.dumps({"FirstName": FirstName,
                           "LastName": LastName,
                           "Alias": Alias,
                           "DisplayName": DisplayName,
                           "EmailAddress": EmailAddress,
                           "SmtpAddress": SmtpAddress,
                           "DtmfAccessId": DtmfAccessId
                           })

    def createNewVoicemail(self):
        cupiRLogger.info("Create Voicemail Started")
        vmCreateUrl = 'users'
        url = self.__baseUrl + vmCreateUrl
        querystring = {"templateAlias": self.__template}

        resp = requests.post(url,
                             auth=self.__auth,
                             verify=self.__verify,
                             headers=self.__headers,
                             data=self._newUserData,
                             params=querystring)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST {0} {1}'.format(url,
                                                  resp.status_code))

    def getImportUserPkid(self):
        cupiRLogger.debug("Get Import PKID")
        vmImportUrl = 'import/users/ldap'
        url = self.__baseUrl + vmImportUrl
        query = {"limit": "1", "query": "(alias is {0})".format(self._alias)}

        resp = requests.get(url,
                            auth=self.__auth,
                            verify=self.__verify,
                            headers=self.__headers,
                            params=query)
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('GET {0} {1}'.format(url,
                                                 resp.status_code))
        data = resp.json()
        try:
            pkid = data['ImportUser']['pkid']
        except KeyError:
            return("KeyError: VM will NOT be created")
        return pkid

    def importNewVoicemail(self):
        cupiRLogger.info("Import Voicemail Started")

        pkid = self.getImportUserPkid()
        userData = json.dumps({"dtmfAccessId": self._extension, "pkid": pkid})
        vmCreateUrl = 'import/users/ldap'
        url = self.__baseUrl + vmCreateUrl
        query = {"templateAlias": self.__template}

        resp = requests.post(url,
                             auth=self.__auth,
                             verify=self.__verify,
                             headers=self.__headers,
                             data=userData,
                             params=query)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST {0} {1}'.format(url,
                                                  resp.status_code))

    def getTemplate(self):
        getTemplateUrl = 'usertemplates'
        url = self.__baseUrl + getTemplateUrl
        resp = requests.post(url,
                             auth=self.__auth,
                             verify=self.__verify,
                             headers=self.__headers)
        if resp.status_code != 201:
            # This means something went wrong.
            raise Exception('POST {0} {1}'.format(url,
                            resp.status_code))

    def getVmObjectId(self):
        vmGetUrl = 'users'
        url = self.__baseUrl + vmGetUrl
        query = {"query": "(alias is {0})".format(self._alias)}

        resp = requests.get(url,
                            auth=self.__auth,
                            verify=self.__verify,
                            headers=self.__headers,
                            params=query)
        data = resp.json()
        return data['User']['ObjectId']
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('GET {0} {1}'.format(url,
                                                 resp.status_code))

    def deleteVoicemail(self):
        cupiRLogger.info("Delete Voicemail Started")
        userObjectId = self.getVmObjectId()
        vmDeleteUrl = 'users/' + userObjectId
        url = self.__baseUrl + vmDeleteUrl
        resp = requests.delete(url,
                               auth=self.__auth,
                               verify=self.__verify,
                               headers=self.__headers)
        if resp.status_code != 204:
            # This means something went wrong.
            raise Exception('Delete {0} {1}'.format(url,
                                                    resp.status_code))
