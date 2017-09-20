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
    __jabberTypes = ['CSF', 'TCT', 'BOT', 'TAB']

    # jabberWriter will take all data about user, below
    # data obtained based on given data
    __obtainedFirstName = ''  # obtained from LDAP user in CUCM
    __obtainedLastName = ''  # obtained from LDAP user in CUCM

    # data given during inital setup
    __givensAMAccountName = ''  # sAMAccountName must have a matching user
    __givenDID = ''  # DID / +e164 number (10 digit number)
    __givenEpriseExt = ''  # Extension (6 digit number)
    __givenSite = ''  # Site name (for Device Pool and D_CSS)
    __givenVM = ''  # Bool
    __givenVMprofile = ''  # IF T - VM Profile required to set on line
    __givenCoS = 'INTL'  # Class of Service - default INTLf
    __givenSNR = ''  # Bool
    __givenSNRphone = ''  # IF T - Cell Phone Number required
    # Meet me config? (maybe)
    myCucmAxlWriter = cucmAxlWriter()

    def __init__(self, sAMAccountName, DID, EpriseExt, Site, VM, VMprofile,
                 CoS, SNR, SNRphone):

        self.__setsAMAccountName(sAMAccountName)
        self.__setDID(DID)
        self.__setEpriseExt(EpriseExt)
        self.__setSite(Site)
        self.__setVM(VM)
        self.__setVMprofile(VMprofile)
        self.__setCoS(CoS)
        self.__setSNR(SNR)
        self.__setSNRphone(SNRphone)
        user = self.myCucmAxlWriter.userGet(username=self.getsAMAccountName())
        cjwLogger.debug(user)

        if not user:
            raise Exception("User does NOT exist in CUCM, unrecoverable")
        cjwLogger.info("init getUser Completed")
        tempFirstName = user['return']['user']['firstName']
        tempLastName = user['return']['user']['lastName']
        cjwLogger.debug('firstname: %s lastname: %s', tempFirstName,
                        tempLastName)
        self.__setFirstName(tempFirstName)
        self.__setLastName(tempLastName)

    def __setsAMAccountName(self, username):
        self.__usersAMAccountName = username

    def getsAMAccountName(self):
        return self.__usersAMAccountName

    def __setDID(self, did):
        self.__userDID = did

    def getDID(self):
        return self.__userDID

    def __setEpriseExt(self, extension):
        self.__userEpriseExt = extension

    def getEpriseExt(self):
        return self.__userEpriseExt

    def __setSite(self, site):
        self.__givenSite = site

    def getSite(self):
        return self.__givenSite

    def __setVM(self, vm):
        self.__givenVM = vm

    def getVM(self):
        return self.__givenVM

    def __setVMprofile(self, vmprofile):
        self.__givenVMprofile = vmprofile

    def getVMprofile(self):
        return self.__givenVMprofile

    def __setCoS(self, cos):
        self.__givenCoS = cos

    def getCoS(self):
        return self.__givenCoS

    def __setSNR(self, snr):
        self.__givenSNR = snr

    def getSNR(self):
        return self.__givenSNR

    def __setSNRphone(self, snrphone):
        self.__givenSNRphone = snrphone

    def getSNRphone(self):
        return self.__givenSNRphone

    def __setFirstName(self, firstName):
        self.__obtainedFirstName = firstName

    def getFirstName(self):
        return self.__obtainedFirstName

    def __setLastName(self, lastName):
        self.__obtainedLastName = lastName

    def getLastName(self):
        return self.__obtainedLastName

    def __deleteJabberLine(self):
        cjwLogger.info("deleteJabberLine called")
        # verify line exists
        if self.myCucmAxlWriter.lineExists(self.getEpriseExt()):
            cjwLogger.info("Line exists")
            self.myCucmAxlWriter.lineDelete(self.getEpriseExt())
            cjwLogger.info("deleteJabberLine Completed")
        else:
            cjwLogger.info("createJabberLine already exists")

    def __createJabberLine(self):
        cjwLogger.info("createJabberLine called")
        # verify line NOT exist
        if not self.myCucmAxlWriter.lineExists(self.getEpriseExt()):
            cjwLogger.info("Line does NOT exist")
            self.myCucmAxlWriter.lineAdd(self.getEpriseExt(),
                                         self.getFirstName(),
                                         self.getLastName(),
                                         self.getSite(),
                                         vm=self.getVM())
            cjwLogger.info("createJabberLine Completed")
        else:
            cjwLogger.info("createJabberLine already exists")

    def __updateJabberLine(self):
        cjwLogger.info("updateJabberLine called")
        if self.myCucmAxlWriter.lineExists(self.getEpriseExt()):
            cjwLogger.info("Line exists, updating")
            self.myCucmAxlWriter.lineUpdate(self.getEpriseExt(), self.getDID())
        else:
            cjwLogger.info("updateJabberLine does NOT exist")
            raise Exception("attempted to update a line that does not exist")

    def __deleteJabberDevices(self):
        cjwLogger.info("deleteJabberDevice called")
        for jabberType in self.__jabberTypes:
            if self.myCucmAxlWriter.deviceExists(jabberType +
                                                 self.getsAMAccountName()):
                cjwLogger.info("%s Device exists", jabberType)
                self.myCucmAxlWriter.deviceDelete(self.getsAMAccountName(),
                                                  jabberType)
            cjwLogger.info("%s deleteJabberDevice done", jabberType)

    def __createJabberDevices(self):
        cjwLogger.info("createJabberDevices called")
        for jabberType in self.__jabberTypes:
            if not self.myCucmAxlWriter.deviceExists(jabberType +
                                                     self.getsAMAccountName()):
                cjwLogger.info("%s Device does NOT exist", jabberType)
                self.myCucmAxlWriter.deviceAdd(self.getsAMAccountName(),
                                               self.getEpriseExt(),
                                               self.getSite(),
                                               jabberType)
            cjwLogger.info("%s createJabberDevice done", jabberType)

    def __updateJabberUser(self):
        deviceList = []
        for jabberType in self.__jabberTypes:
            deviceList.insert(0, jabberType+self.getsAMAccountName())
        self.myCucmAxlWriter.userUpdate(self.getsAMAccountName(),
                                        self.getEpriseExt(),
                                        deviceList)
        cjwLogger.info("updateJabberUser completed")

    def writeJabber(self):
        cjwLogger.info("writeJabber called")
        self.__createJabberLine()
        self.__updateJabberLine()  # required for adding an e164AltNum
        self.__createJabberDevices()  # create ALL jabber devices in CUCM
        self.__updateJabberUser()  # update user to associate devices
        # TODO cleanup after itself in failure scenario
        cjwLogger.info("writeJabber completed")

    def cleanJabber(self):
        cjwLogger.info("cleanJabber called")
        self.__deleteJabberDevices()  # delete all devices
        self.__deleteJabberLine()  # delete line
        cjwLogger.info("cleanJabber completed")
