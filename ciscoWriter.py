#!/usr/bin/env python3.6
__version__ = '0.4'
__author__ = 'Christopher Phillips'

import sys
import logging
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
                  dest="site", help="Site of jabber user")
parser.add_option("-g", "--pin", action="store", type="string",
                  dest="pin", help="User PIN for VM and MeetMe")
parser.add_option("-v", "--voicemail", action="store", type="string",
                  dest="vm", help="jabber user Voicemail T/F")
parser.add_option("-b", "--emailaddress", action="store", type="string",
                  dest="emailaddress", help="jabber user Email Address")
parser.add_option("-p", "--vmprofile", action="store", type="string",
                  dest="vmprofile", help="jabber user Voicemail T/F")
parser.add_option("-c", "--classofservice", action="store", type="string",
                  dest="cos", help="Class of Service for jabber user")
parser.add_option("-r", "--singlenumberreach", action="store", type="string",
                  dest="snr", help="jabber user Single Number Reach T/F")
parser.add_option("-m", "--snrdid", action="store", type="string",
                  dest="snrphone", help="Mobile Phone of jabber SNR user")
(options, args) = parser.parse_args()

# myCiscoWriter = cucmJabberWriter(sAMAccountName, DID, EpriseExt, Site,
#                                  VM, VMprofile, CoS, SNR, SNRphone)
# myJabber = cucmJabberWriter('fernando', '5097148870', '118870',
#                             'Seattle', 'True', 'NA', 'INTL', 'False', 'NA')
''' ./ciscoWriter.py -a create -u patrick -f Christopher -l Phillips -e 223611
 -d 2065551234 -s Tampa -g 54321 -v True -b patrick@fakedomain.com
 -p voicemailusertemplate -c International -r False -m 4255551212'''
'''./ciscoWriter.py -a create -u patrick -f GetAD! -l GetAD! -e 223611
 -d 2065551234 -s Tampa -g 54321 -v True -b patrick@fakedomain.com
  -p voicemailusertemplate -c International -r False -m 4255551212'''
'''./ciscoWriter.py -a create -u tdurden -e 223611 -d 2065551234 -s Tampa
 -g 54321 -v True -b tdurden@apitest.org -p voicemailusertemplate
  -c International -r False -m 4255551212'''

if not options.firstname:
    options.firstname = 'GetAD!'
if not options.lastname:
    options.lastname = 'GetAD!'

myJabber = cucmJabberWriter(sAMAccountName=options.username,
                            DID=options.did,
                            EpriseExt=options.extension,
                            Site=options.site,
                            VM=options.vm,
                            VMprofile=options.vmprofile,
                            CoS=options.cos,
                            SNR=options.snr,
                            SNRphone=options.snrphone,
                            PIN=options.pin,
                            gFirstName=options.firstname,
                            gLastName=options.lastname)

myVoicemail = cupiRestWriter(Alias=options.username,
                             Extension=options.extension,
                             FirstName=options.firstname,
                             LastName=options.lastname,
                             EmailAddress=options.emailaddress)

status = {}
if options.perform == 'create':
    status.update({"ccm": myJabber.writeJabber()})
    # myVoicemail.createNewVoicemail()  # would use for non LDAP use case
    status.update({"cxn": myVoicemail.importNewVoicemail()})
    print(status)
elif options.perform == 'delete':
    status.update({"ccm": myJabber.cleanJabber()})
    status.update({"cxn": myVoicemail.deleteVoicemail()})
    print(status)
else:
    print("Invalid / No Option selected")
cwLogger.info("CiscoWriter Completed")
