# The cucmAxlWriter project
This project is divided into several python files, which will be explained in further detail below.

## configCreator.py
Depends upon: appConfig

Use configCreator to build configuration files for use by ciscoWriter.

###### CLI Switches:
 * -h or --help for help.
 * --ccm to view or create a Communications Manager config file
 * --cxn to view or create a Unity Connection config file


## ciscoWriter.py
Depends upon: cucmJabberWriter and cupiRestWriter

The main application called to create a user.
Utilize CLI switches to change behavior

###### CLI Switches:
 * -h or --help for help.
 * -a or --action Choose either: create/delete
 * -u or --username for username of Jabber user (required)
 * -f or --firstname for First Name of Jabber user (optional: if not supplied, the program will use what is found in AD)
 * -l or --lastname for Last Name of Jabber user (optional: if not supplied, the program will use what is found in AD)
 * -e or --ext for extension of Jabber user (required)
 * -d or --did for DID of Jabber user (required)
 * -s or --site for Site of Jabber user (required)
 * -i or --subsite for Site of Jabber user (required)
 * -g or --pin for User PIN for VM and MeetMe (required)
 * -v or --voicemail for (T/F) for Jabber user Voicemail (required)
 * -b or --emailaddress for Jabber user Email Address
 * -p or --vmprofile for Jabber user Voicemail profile
 * -c or --classofservice for Class of Service for Jabber user
 * -r or --singlenumberreach for (T/F) Jabber user Single Number Reach T/F (required)
 * -m or --snrdid for Mobile Phone of Jabber SNR user (optional)

e.g.:  `./ciscoWriter.py -a create -u tdurden -e 223611 -d 2065551234 -s Tampa -i Northwoods -g 54321 -v True -b tdurden@apitest.org -p voicemailusertemplate
   -c International -r False -m 4255551212`

## cucmJabberWriter
Depends Upon: cucmAxlWriter

cucmJabberWriter defines a class that holds the data necessary to build Jabber Devices and associate them to a user in CUCM

This class has two public facing methods; writeJabber and cleanJabber. They are used alternately to create or remove Jabber for a given user.

## cucmAxlWriter.py
Depends upon: ucAppConfig (also, zeep, requests)

cucmAxlWriter defines methods to connect to the communications manager server as required by cucmJabberWriter

## cupiRestWriter.py
Depends upon: ucAppConfig

cupiRestWriter defines a class that holds the data necessary to connect to the voicemail server as well as import a new user

## ucAppConfig.py
Depends upon: appConfig

ucAppConfig defines two classes; ccmAppConfig and cxnAppConfig.

Each class extends appConfig with items specific to either the communications manager or voicemail system


## appConfig.py
Defines a class to hold data and methods for accessing that data for an application.

This data includes:
 * username
 * password
 * hostname / IP
 * ssl verification setting
 * ssl cert file if used

## Additional notes:
 * [CUCM Product Page](http://www.cisco.com/c/en/us/products/unified-communications/unified-communications-manager-callmanager/index.html)
 * [CUCM Admin AXL/SOAP API](https://developer.cisco.com/site/axl/)
 * [CXN Product Page](https://www.cisco.com/c/en/us/products/unified-communications/unity-connection/index.html)
 * [CXN REST API](https://developer.cisco.com/site/unity-connection/overview/)
 * [Zeep](http://docs.python-zeep.org/en/master/)
 * [Requests](http://docs.python-requests.org/en/master/)
