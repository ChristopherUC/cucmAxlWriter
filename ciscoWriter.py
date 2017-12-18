#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import sys
import logging
import json
from optparse import OptionParser
from cucmJabberWriter import cucmJabberWriter
from cupiRestWriter import cupiRestWriter

cwLogger = logging.getLogger(__name__)
cwLogger.setLevel(logging.DEBUG)
infoHandler = logging.FileHandler('CiscoInfo.log', mode='w')
infoHandler.setLevel(logging.INFO)
debugHandler = logging.FileHandler('CiscoDebug.log', mode='w')
debugHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
infoHandler.setFormatter(formatter)
debugHandler.setFormatter(formatter)
cwLogger.addHandler(infoHandler)
cwLogger.addHandler(debugHandler)
cwLogger.addHandler(logging.StreamHandler(sys.stdout))
cwLogger.info("Begin CiscoWriter Info Logging")
cwLogger.debug("Begin CiscoWriter Debug Logging")

parser = OptionParser()
parser.add_option("-a", "--action", action="store", type="string",
                  dest="perform", help="create/delete")
parser.add_option("-u", "--username", action="store", type="string",
                  dest="username", help="username of jabber user")
parser.add_option("-f", "--firstname", action="store", type="string",
                  dest="firstname", help="First Name of jabber user")
parser.add_option("-l", "--lastname", action="store", type="string",
                  dest="lastname", help="Last Name of jabber user")
parser.add_option("-e", "--ext", action="store", type="string",
                  dest="extension", help="extension of jabber user")
parser.add_option("-d", "--did", action="store", type="string",
                  dest="did", help="DID of jabber user")
parser.add_option("-s", "--site", action="store", type="string",
                  dest="city", help="Site of jabber user")
parser.add_option("-i", "--subsite", action="store", type="string",
                  dest="building", help="Site of jabber user")
parser.add_option("-g", "--pin", action="store", type="string",
                  dest="pin", help="User PIN for VM and MeetMe")
parser.add_option("-v", "--voicemail", action="store", type="string",
                  dest="vm", help="jabber user Voicemail T/F")
parser.add_option("-b", "--emailaddress", action="store", type="string",
                  dest="emailaddress", help="jabber user Email Address")
parser.add_option("-p", "--vmprofile", action="store", type="string",
                  dest="vmprofile", help="UCM user Voicemail profile")
# if a specific profile is to be provided, it must be provided
# if system default profile of "<None>" is desired, omit the -p switch
parser.add_option("-t", "--vmtemplate", action="store", type="string",
                  dest="vmtemplate", help="CXN user Voicemail template")
parser.add_option("-c", "--classofservice", action="store", type="string",
                  dest="cos", help="Class of Service for jabber user")
parser.add_option("-r", "--singlenumberreach", action="store", type="string",
                  dest="snr", help="jabber user Single Number Reach T/F")
parser.add_option("-m", "--snrdid", action="store", type="string",
                  dest="snrphone", help="Mobile Phone of jabber SNR user")
(options, args) = parser.parse_args()

'''./ciscoWriter.py -a create -u tdurden -e 223611 -d 2065551234 -s Tampa
 -i Northwoods -g 54321 -v True -p CUST-No-Voicemail -b tdurden@apitest.org
 -t voicemailusertemplate -c International -r False -m 4255551212'''

if not options.firstname:
    options.firstname = 'GetAD!'
if not options.lastname:
    options.lastname = 'GetAD!'

'''
Device Pools will have following naming convention:
"<Building Name> <Floor> DP"	e.g.  "Uptempo 1W DP"
Line Calling Search Space
"<City> <CoS> CSS"	e.g.  "Beaverton International CSS"
'''

myJabber = cucmJabberWriter(sAMAccountName=options.username,
                            DID=options.did,
                            EpriseExt=options.extension,
                            Building=options.building,
                            City=options.city,
                            VM=options.vm,
                            VMprofile=options.vmprofile,
                            CoS=options.cos,
                            SNR=options.snr,
                            SNRphone=options.snrphone,
                            PIN=options.pin,
                            gFirstName=options.firstname,
                            gLastName=options.lastname)

myVoicemail = cupiRestWriter(Alias=options.username,
                             Extension="+1" + options.did,
                             FirstName=options.firstname,
                             LastName=options.lastname,
                             EmailAddress=options.emailaddress,
                             Template=options.vmtemplate)

status = {}
if options.perform == 'create':
    status.update({"ccm": myJabber.writeJabber()})
    # myVoicemail.createNewVoicemail()  # would use for non LDAP use case
    if options.vm.lower() in ['true', '1', 't', 'y', 'yes']:
        status.update({"cxn": myVoicemail.importNewVoicemail()})
    print(json.dumps(status))
elif options.perform == 'delete':
    status.update({"ccm": myJabber.cleanJabber()})
    status.update({"cxn": myVoicemail.deleteVoicemail()})
    print(json.dumps(status))
else:
    print("Invalid / No Option selected")
cwLogger.info("CiscoWriter Completed")
