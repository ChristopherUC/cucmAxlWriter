#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import logging
from cucmAxlConfig import cucmAxlConfig
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3  # imported to disable the SAN warning for the cert
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

cawLogger = logging.getLogger(__name__)
cawLogger.setLevel(logging.DEBUG)
handler = logging.FileHandler('writerDebug.log', mode='w')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
handler.setFormatter(formatter)
cawLogger.addHandler(handler)
# cawLogger.addHandler(logging.StreamHandler(sys.stdout))
cawLogger.info("Begin cucmAxlWriter Info Logging")
cawLogger.debug("Begin cucmAxlWriter Debug Logging")


class cucmAxlWriter:
    # uses cucmAxlConfig to create factory and service for CUCM AXL Writing

    factory = ''
    service = ''

    def __init__(self):
        myCucmConfig = cucmAxlConfig()

        cawLogger.debug("current CUCM username is %s",
                        myCucmConfig.getCucmUsername())
        cawLogger.debug("current CUCM password is %s",
                        myCucmConfig.getCucmPassword())
        cawLogger.debug("current CUCM url is %s", myCucmConfig.getCucmUrl())
        cawLogger.debug("current CUCM axlurl is %s",
                        myCucmConfig.getCucmAxlUrl())
        cawLogger.debug("current CUCM verify mode is %s",
                        myCucmConfig.getCucmVerify())
        cawLogger.debug("current CUCM Cert File  is %s",
                        myCucmConfig.getCucmCert())

        zeeplogger = logging.getLogger('zeep.transports')
        zeeplogger.setLevel(logging.DEBUG)
        zeephandler = logging.FileHandler('zeepDebug.log', mode='w')
        zeephandler.setLevel(logging.DEBUG)
        zeepformatter = logging.Formatter('%(asctime)s - %(name)s - \
                            %(levelname)s - %(message)s')
        zeephandler.setFormatter(zeepformatter)
        zeeplogger.addHandler(zeephandler)
        zeeplogger.info("Begin zeep Logging")

        cache = SqliteCache(path='/tmp/wsdlsqlite.db', timeout=60)
        transport = Transport(cache=cache)
        client = Client(myCucmConfig.getwsdlFileName(), transport=transport)

        session = Session()
        if myCucmConfig.getCucmVerify():
            cawLogger.info("Session Security ENABLED")
            session.verify = myCucmConfig.getCucmCert()
        else:
            cawLogger.info("Session Security DISABLED")
            session.verify = myCucmConfig.getCucmVerify()
        cawLogger.info("Session Created")
        session.auth = HTTPBasicAuth(myCucmConfig.getCucmUsername(),
                                     myCucmConfig.getCucmPassword())
        cawLogger.info("Auth Created")

        client = Client(wsdl=myCucmConfig.getwsdlFileName(),
                        transport=Transport(session=session))
        cawLogger.info("Client Created")

        self.factory = client.type_factory('ns0')
        cawLogger.info("Factory Created")

        self.service = client.create_service(
            "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
            myCucmConfig.getCucmAxlUrl())
        cawLogger.info("Service Created")

    # TODO LDAP
        # check LDAP sync time (can this be checked?)
        # GetLdapDirectoryReq ?
        # getLdapSyncCustomField ?
        # getLdapSyncCustomFieldResponse ?
        # GetLdapSyncStatusReq !
        # TODO   kick off LDAP Sync (maybe just do this always)
        # TODO   Check LDAP sync time again?

    def userGet(self, username):
        try:
            obtainedUser = self.service.getUser(userid=username)
            cawLogger.debug(obtainedUser)
            return obtainedUser
        except Exception as e:
            # If user does not exist
            cawLogger.debug("User NOT found. Error=%s", e)
            return False

    def userExists(self, username):
        try:
            self.userGet(username)
            return True
        except Exception as e:
            cawLogger.debug("User NOT found. Error=%s", e)
            return False

    def userAdd(self, username):
        # TODO : build for future if needed
        # current users will be LDAP synced
        return False

    def userUpdate(self, username, extension, deviceList, partition='Phones'):
        userGroups = ['Standard CTI Enabled',
                      'Standard CCM End Users',
                      'Standard CTI Allow Control of Phones supporting '
                      + 'Connected Xfer and conf',
                      'Standard CTI Allow Control of Phones supporting '
                      + 'Rollover Mode']
        result = self.service.updateUser(
                        userid=username,
                        associatedDevices={'device': deviceList},
                        primaryExtension={'pattern': extension,
                                          'routePartitionName': partition},
                        associatedGroups={'userGroup': userGroups})
        cawLogger.info("Update User Completed")
        cawLogger.debug(result)

    def userDelete(self, username):
        return True

    def lineGet(self, extension, partition='Phones'):
        try:
            getLine = self.service.getLine(pattern=extension,
                                           routePartitionName=partition)
            cawLogger.info("getLine Completed")
            cawLogger.debug(getLine)
            return getLine
        except Exception as e:
            return False

    def lineExists(self, extension, partition='Phones'):
        cawLogger.debug("lineExists Called")
        try:
            getLine = self.service.getLine(pattern=extension,
                                           routePartitionName=partition)
            cawLogger.debug(getLine)
            cawLogger.info("Line Exists")
            return True
        except Exception as e:
            return False

    def lineAdd(self, extension, firstname, lastname, vm='False',
                partition='Phones', usage='Device'):
        if not self.lineExists(extension):
            try:
                devCss = 'Device - Seattle'
                lineCss = 'Class - International'
                vmConfig = {
                    'forwardToVoiceMail': vm,
                    'callingSearchSpaceName': devCss}
                nameString = firstname + " " + lastname

                addlinepackage = self.factory.XLine()
                addlinepackage.pattern = extension
                addlinepackage.usage = usage
                addlinepackage.routePartitionName = partition
                addlinepackage.shareLineAppearanceCssName = lineCss
                addlinepackage.callForwardAll = {
                    'forwardToVoiceMail': 'False',
                    'callingSearchSpaceName': devCss,
                    'secondaryCallingSearchSpaceName': lineCss}
                addlinepackage.callForwardBusy = vmConfig
                addlinepackage.callForwardBusyInt = vmConfig
                addlinepackage.callForwardNoAnswer = vmConfig
                addlinepackage.callForwardNoAnswerInt = vmConfig
                addlinepackage.callForwardNoCoverage = vmConfig
                addlinepackage.callForwardNoCoverageInt = vmConfig
                addlinepackage.callForwardOnFailure = vmConfig
                addlinepackage.callForwardAlternateParty = vmConfig
                addlinepackage.callForwardNotRegistered = vmConfig
                addlinepackage.callForwardNotRegisteredInt = vmConfig
                # addlinepackage.voiceMailProfileName = vmProfileName
                addlinepackage.alertingName = nameString
                addlinepackage.asciiAlertingName = nameString
                addlinepackage.description = nameString
                '''
                'e164AltNum': {
                    'numMask': None,
                    'isUrgent': 'f',
                    'addLocalRoutePartition': 'f',
                    'routePartition': {
                        '_value_1': None,
                        'uuid': None
                    },
                    'advertiseGloballyIls': 'f'
                },
                '''

                cawLogger.info("Line Factory Completed")
                cawLogger.debug(addlinepackage)

                createdLine = self.service.addLine(addlinepackage)
                cawLogger.debug("Line Created")
                cawLogger.debug(createdLine)
                cawLogger.info("Add Line Completed")
            except Exception as e:
                cawLogger.debug("Add Line Error. Server error=%s", e)
                raise Exception("Line could not be added")
        else:
            raise Exception("Line already exists")

    def lineUpdate(self, extension):
        return True

    def lineDelete(self, extension, partition='Phones'):
        try:
            result = self.service.removeLine(pattern=extension,
                                             routePartitionName=partition)
            logging.info("Remove Line Completed")
            logging.info(result)
        except Exception as e:
            logging.info(e)

    def deviceGetName(self, username, devicetype):
        if devicetype == 'CSF':
            deviceName = 'CSF'+username
        elif devicetype == 'TCT':
            deviceName = 'TCT'+username
        elif devicetype == 'BOT':
            deviceName = 'BOT'+username
        elif devicetype == 'TAB':
            deviceName = 'TAB'+username

        deviceName = deviceName.upper()
        return deviceName

    def deviceExists(self, devicename):
        try:
            getPhone = self.service.getPhone(name=devicename)
            cawLogger.info("getPhone Completed")
            cawLogger.debug(getPhone)
            return True
        except Exception as e:
            return False

    def deviceAdd(self, username, extension, site, devicetype,
                  partition='Phones'):

        deviceName = self.deviceGetName(username, devicetype)
        tempPhoneConfigName = 'Standard Common Phone Profile'

        if devicetype == 'CSF':
            tempProduct = 'Cisco Unified Client Services Framework'
            tempModel = 'Cisco Unified Client Services Framework'
        elif devicetype == 'TCT':
            tempProduct = 'Cisco Dual Mode for iPhone'
            tempModel = 'Cisco Dual Mode for iPhone'
        elif devicetype == 'BOT':
            tempProduct = 'Cisco Dual Mode for Android'
            tempModel = 'Cisco Dual Mode for Android'
        elif devicetype == 'TAB':
            tempProduct = 'Cisco Jabber for Tablet'
            tempModel = 'Cisco Jabber for Tablet'
        else:
            raise Exception("Invalid Device Type Specified, unrecoverable")

        if not self.deviceExists(deviceName):
            try:
                #  create device
                #  join line to device
                # directory number / line, required for a PhoneLine
                # line must allready exist
                tempDirN1 = self.factory.XDirn()
                tempDirN1.pattern = extension
                tempDirN1.routePartitionName = partition
                cawLogger.debug(tempDirN1)

                # PhoneLine is how a DirectoryNumber and a Phone are merged
                tempPhoneLine1 = self.factory.XPhoneLine()
                tempPhoneLine1.index = 1
                tempPhoneLine1.dirn = tempDirN1
                cawLogger.debug(tempPhoneLine1)

                addphonepackage = self.factory.XPhone()
                addphonepackage.name = deviceName
                addphonepackage.product = tempProduct
                addphonepackage.model = tempModel
                addphonepackage['class'] = 'Phone'
                addphonepackage.protocol = 'SIP'
                addphonepackage.commonPhoneConfigName = tempPhoneConfigName
                addphonepackage.locationName = 'Hub_None'
                addphonepackage.devicePoolName = site
                addphonepackage.lines = {'line': tempPhoneLine1}
                addphonepackage.ownerUserName = username
                addphonepackage.callingSearchSpaceName = 'Device - ' + site
                cawLogger.debug(addphonepackage)

                createdPhone = self.service.addPhone(addphonepackage)
                cawLogger.debug(createdPhone)
                cawLogger.debug("Phone Created")
                cawLogger.info("Add Phone Completed")
            except Exception as e:
                cawLogger.debug("Add Phone Error. Server error=%s", e)
                # raise Exception("Phone could not be added")
                raise Exception(e)

    def deviceUpdate(self, username):
        return True

    def deviceDelete(self, username, devicetype):
        deviceName = self.deviceGetName(username, devicetype)
        try:
            result = self.service.removePhone(name=deviceName)
            logging.info("Remove Phone Completed")
            logging.info(result)
        except Exception as e:
            logging.info(e)
