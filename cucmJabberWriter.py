#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

# import sys
import logging
import json
from cucmAxlWriter import cucmAxlWriter

cjwLogger = logging.getLogger(__name__)
cjwLogger.setLevel(logging.DEBUG)
infoHandler = logging.FileHandler('jabberInfo.log', mode='w')
infoHandler.setLevel(logging.INFO)
debugHandler = logging.FileHandler('jabberDebug.log', mode='w')
debugHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
infoHandler.setFormatter(formatter)
debugHandler.setFormatter(formatter)
cjwLogger.addHandler(infoHandler)
cjwLogger.addHandler(debugHandler)
# cjwLogger.addHandler(logging.StreamHandler(sys.stdout))
cjwLogger.info("Begin JabberWriter Info Logging")
cjwLogger.debug("Begin JabberWriter Debug Logging")


class cucmJabberWriter:
    # uses cucmAxlWriter to write Jabber devices lines users to CUCM
    _jabberTypes = ['CSF', 'TCT', 'BOT', 'TAB']

    # jabberWriter will take all data about user, below
    # data obtained based on given data
    _obtainedFirstName = ''  # obtained from LDAP user in CUCM
    _obtainedLastName = ''  # obtained from LDAP user in CUCM

    # data given during inital setup
    _givensAMAccountName = ''  # sAMAccountName must have a matching user
    _givenDID = ''  # DID / +e164 number (10 digit number)
    _givenEpriseExt = ''  # Extension (6 digit number)
    _givenCity = ''  # City name (for D_CSS)
    _givenBuilding = ''  # Building name (for Device Pool)
    _givenVM = ''  # Bool
    _givenVMprofile = ''  # IF T - VM Profile required to set on line
    _givenCoS = 'INTL'  # Class of Service - default INTLf
    _givenSNR = ''  # Bool
    _givenSNRphone = ''  # IF T - Cell Phone Number required
    # Meet me config? (maybe)
    myCucmAxlWriter = cucmAxlWriter()

    def __init__(self, sAMAccountName, DID, EpriseExt, Building, City, VM='f',
                 VMprofile='voicemailusertemplate', CoS='International',
                 SNR='f', SNRphone='', PIN='232323', gFirstName='GetAD!',
                 gLastName='GetAD!'):

        self._setsAMAccountName(sAMAccountName)
        self._setDID(DID)
        self._setEpriseExt(EpriseExt)
        self._setBuilding(Building)
        self._setCity(City)
        self._setVM(VM)
        self._setVMprofile(VMprofile)
        self._setCoS(CoS)
        self._setSNR(SNR)
        self._setSNRphone(SNRphone)
        user = self.myCucmAxlWriter.userGet(username=self.getsAMAccountName())
        cjwLogger.debug(user)

        if not user:
            raise Exception("User does NOT exist in CUCM, unrecoverable")
        cjwLogger.info("init getUser Completed")
        if 'GetAD!' in gFirstName:
            tempFirstName = user['return']['user']['firstName']
        else:
            tempFirstName = gFirstName
        if 'GetAD!' in gLastName:
            tempLastName = user['return']['user']['lastName']
        else:
            tempLastName = gLastName
        cjwLogger.debug('firstname: %s lastname: %s', tempFirstName,
                        tempLastName)
        self._setFirstName(tempFirstName)
        self._setLastName(tempLastName)

    def _setsAMAccountName(self, username):
        self._usersAMAccountName = username

    def getsAMAccountName(self):
        return self._usersAMAccountName

    def _setDID(self, did):
        self._userDID = did

    def getDID(self):
        return self._userDID

    def _setEpriseExt(self, extension):
        self._userEpriseExt = extension

    def getEpriseExt(self):
        return self._userEpriseExt

    def getE164Ext(self):
        return "\+1" + self._userDID

    def _setBuilding(self, building):
        self._givenBuilding = building

    def getBuilding(self):
        return self._givenBuilding

    def _setCity(self, city):
        self._givenCity = city

    def getCity(self):
        return self._givenCity

    def _setVM(self, vm):
        self._givenVM = vm

    def getVM(self):
        return self._givenVM

    def _setVMprofile(self, vmprofile):
        self._givenVMprofile = vmprofile

    def getVMprofile(self):
        return self._givenVMprofile

    def _setCoS(self, cos):
        self._givenCoS = cos

    def getCoS(self):
        return self._givenCoS

    def _setSNR(self, snr):
        self._givenSNR = snr

    def getSNR(self):
        return self._givenSNR

    def _setSNRphone(self, snrphone):
        self._givenSNRphone = snrphone

    def getSNRphone(self):
        return self._givenSNRphone

    def _setFirstName(self, firstName):
        self._obtainedFirstName = firstName

    def getFirstName(self):
        return self._obtainedFirstName

    def _setLastName(self, lastName):
        self._obtainedLastName = lastName

    def getLastName(self):
        return self._obtainedLastName

    def _deleteJabberLine(self):
        cjwLogger.info("deleteJabberLine called")
        # verify line exists
        if self.myCucmAxlWriter.lineExists(self.getE164Ext()):
            cjwLogger.info("Line exists")
            self.myCucmAxlWriter.lineDelete(self.getE164Ext())
            return "Success"  # Deleted
            cjwLogger.info("deleteJabberLine Completed")
        else:
            cjwLogger.info("Line does not exist to delete")
            return "Fail"  # Did not delete

    def _createJabberLine(self):
        cjwLogger.info("createJabberLine called")
        # verify line NOT exist
        if not self.myCucmAxlWriter.lineExists(self.getE164Ext()):
            cjwLogger.info("Line does NOT exist")
            self.myCucmAxlWriter.lineAdd(extension=self.getE164Ext(),
                                         firstname=self.getFirstName(),
                                         lastname=self.getLastName(),
                                         building=self.getBuilding(),
                                         city=self.getCity(),
                                         vm=self.getVM())
            cjwLogger.info("createJabberLine Completed")
            return "Success"  # Line Created
        else:
            cjwLogger.info("createJabberLine already exists")
            return "Fail"  # Line already exists

    def _updateJabberLine(self):
        cjwLogger.info("updateJabberLine called")
        if self.myCucmAxlWriter.lineExists(self.getE164Ext()):
            cjwLogger.info("Line exists, updating")
            self.myCucmAxlWriter.lineUpdate(extension=self.getE164Ext(),
                                            did=self.getDID())
            return "Success"  # Line Updated
        else:
            cjwLogger.info("updateJabberLine does NOT exist")
            return "Fail"  # Attempted to update a line that does not exist"

    def _deleteJabberDevices(self):
        status = {}
        cjwLogger.info("deleteJabberDevice called")
        for jabberType in self._jabberTypes:
            if self.myCucmAxlWriter.deviceExists(jabberType +
                                                 self.getsAMAccountName()):
                cjwLogger.info("%s Device exists", jabberType)
                self.myCucmAxlWriter.deviceDelete(self.getsAMAccountName(),
                                                  jabberType)
                status.update({"{0}".format(jabberType): "Success"})
                # status.update({"{0}".format(jabberType): "Fail"})
            cjwLogger.info("%s deleteJabberDevice done", jabberType)
        return status

    def _createJabberDevices(self):
        status = {}
        cjwLogger.info("createJabberDevices called")
        for jabberType in self._jabberTypes:
            if not self.myCucmAxlWriter.deviceExists(jabberType +
                                                     self.getsAMAccountName()):
                cjwLogger.info("%s Device does NOT exist", jabberType)
                self.myCucmAxlWriter.deviceAdd(self.getsAMAccountName(),
                                               firstname=self.getFirstName(),
                                               lastname=self.getLastName(),
                                               extension=self.getEpriseExt(),
                                               e164ext=self.getE164Ext(),
                                               did=self.getDID(),
                                               building=self.getBuilding(),
                                               city=self.getCity(),
                                               devicetype=jabberType)
                status.update({"{0}".format(jabberType): "Success"})
                cjwLogger.info("%s createJabberDevice done", jabberType)
            else:
                status.update({"{0}".format(jabberType): "Fail"})
        return status

    def _updateJabberUser(self):
        deviceList = []
        for jabberType in self._jabberTypes:
            deviceList.insert(0, jabberType+self.getsAMAccountName())
        self.myCucmAxlWriter.userUpdate(username=self.getsAMAccountName(),
                                        extension=self.getE164Ext(),
                                        did=self.getDID(),
                                        deviceList=deviceList,
                                        pin="232323")
        cjwLogger.info("updateJabberUser completed")
        return "Success"  # User Updated"

    def writeJabber(self):
        status = {}
        cjwLogger.info("writeJabber called")
        # create line, needed for all other associations
        status.update({"lineCreate": self._createJabberLine()})
        # required for adding an e164AltNum
        status.update({"lineUpdate": self._updateJabberLine()})
        # create ALL jabber devices in CUCM
        status.update({"deviceCreate": self._createJabberDevices()})
        # update user to associate devices
        status.update({"endUserUpdate": self._updateJabberUser()})
        # TODO cleanup after itself in failure scenario
        cjwLogger.info("writeJabber completed")
        return json.dumps(status)

    def cleanJabber(self):
        status = {}
        cjwLogger.info("cleanJabber called")
        # delete all devices
        status.update({"deviceDelete": self._deleteJabberDevices()})
        # delete line
        status.update({"lineDelete": self._deleteJabberLine()})
        cjwLogger.info("cleanJabber completed")
        return json.dumps(status)
