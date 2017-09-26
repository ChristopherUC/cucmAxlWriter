#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

# import sys
import logging
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
    _givenSite = ''  # Site name (for Device Pool and D_CSS)
    _givenVM = ''  # Bool
    _givenVMprofile = ''  # IF T - VM Profile required to set on line
    _givenCoS = 'INTL'  # Class of Service - default INTLf
    _givenSNR = ''  # Bool
    _givenSNRphone = ''  # IF T - Cell Phone Number required
    # Meet me config? (maybe)
    myCucmAxlWriter = cucmAxlWriter()

    def __init__(self, sAMAccountName, DID, EpriseExt, Site, VM='f',
                 VMprofile='voicemailusertemplate', CoS='International',
                 SNR='f', SNRphone='', PIN='232323', gFirstName='GetAD!',
                 gLastName='GetAD!'):

        self._setsAMAccountName(sAMAccountName)
        self._setDID(DID)
        self._setEpriseExt(EpriseExt)
        self._setSite(Site)
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

    def _setSite(self, site):
        self._givenSite = site

    def getSite(self):
        return self._givenSite

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
        if self.myCucmAxlWriter.lineExists(self.getEpriseExt()):
            cjwLogger.info("Line exists")
            self.myCucmAxlWriter.lineDelete(self.getEpriseExt())
            cjwLogger.info("deleteJabberLine Completed")
        else:
            cjwLogger.info("createJabberLine already exists")

    def _createJabberLine(self):
        cjwLogger.info("createJabberLine called")
        # verify line NOT exist
        if not self.myCucmAxlWriter.lineExists(self.getEpriseExt()):
            cjwLogger.info("Line does NOT exist")
            self.myCucmAxlWriter.lineAdd(extension=self.getEpriseExt(),
                                         firstname=self.getFirstName(),
                                         lastname=self.getLastName(),
                                         site=self.getSite(),
                                         vm=self.getVM())
            cjwLogger.info("createJabberLine Completed")
        else:
            cjwLogger.info("createJabberLine already exists")

    def _updateJabberLine(self):
        cjwLogger.info("updateJabberLine called")
        if self.myCucmAxlWriter.lineExists(self.getEpriseExt()):
            cjwLogger.info("Line exists, updating")
            self.myCucmAxlWriter.lineUpdate(extension=self.getEpriseExt(),
                                            did=self.getDID())
        else:
            cjwLogger.info("updateJabberLine does NOT exist")
            raise Exception("attempted to update a line that does not exist")

    def _deleteJabberDevices(self):
        cjwLogger.info("deleteJabberDevice called")
        for jabberType in self._jabberTypes:
            if self.myCucmAxlWriter.deviceExists(jabberType +
                                                 self.getsAMAccountName()):
                cjwLogger.info("%s Device exists", jabberType)
                self.myCucmAxlWriter.deviceDelete(self.getsAMAccountName(),
                                                  jabberType)
            cjwLogger.info("%s deleteJabberDevice done", jabberType)

    def _createJabberDevices(self):
        cjwLogger.info("createJabberDevices called")
        for jabberType in self._jabberTypes:
            if not self.myCucmAxlWriter.deviceExists(jabberType +
                                                     self.getsAMAccountName()):
                cjwLogger.info("%s Device does NOT exist", jabberType)
                self.myCucmAxlWriter.deviceAdd(self.getsAMAccountName(),
                                               firstname=self.getFirstName(),
                                               lastname=self.getLastName(),
                                               extension=self.getEpriseExt(),
                                               did=self.getDID(),
                                               site=self.getSite(),
                                               devicetype=jabberType)
            cjwLogger.info("%s createJabberDevice done", jabberType)

    def _updateJabberUser(self):
        deviceList = []
        for jabberType in self._jabberTypes:
            deviceList.insert(0, jabberType+self.getsAMAccountName())
        self.myCucmAxlWriter.userUpdate(username=self.getsAMAccountName(),
                                        extension=self.getEpriseExt(),
                                        did=self.getDID(),
                                        deviceList=deviceList,
                                        pin="232323")
        cjwLogger.info("updateJabberUser completed")

    def writeJabber(self):
        cjwLogger.info("writeJabber called")
        self._createJabberLine()
        self._updateJabberLine()  # required for adding an e164AltNum
        self._createJabberDevices()  # create ALL jabber devices in CUCM
        self._updateJabberUser()  # update user to associate devices
        # TODO cleanup after itself in failure scenario
        cjwLogger.info("writeJabber completed")

    def cleanJabber(self):
        cjwLogger.info("cleanJabber called")
        self._deleteJabberDevices()  # delete all devices
        self._deleteJabberLine()  # delete line
        cjwLogger.info("cleanJabber completed")
