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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('writerDebug.log', mode='w')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Begin cucmAxlWriter Info Logging")
logger.debug("Begin cucmAxlWriter Debug Logging")


class cucmAxlWriter:
    # uses cucmAxlConfig to create factory and service for CUCM AXL Writing

    factory = ''
    service = ''

    def __init__(self):
        myCucmConfig = cucmAxlConfig()

        logger.debug("current CUCM username is %s",
                     myCucmConfig.getCucmUsername())
        logger.debug("current CUCM password is %s",
                     myCucmConfig.getCucmPassword())
        logger.debug("current CUCM url is %s", myCucmConfig.getCucmUrl())
        logger.debug("current CUCM axlurl is %s", myCucmConfig.getCucmAxlUrl())
        logger.debug("current CUCM verify mode is %s",
                     myCucmConfig.getCucmVerify())
        logger.debug("current CUCM Cert File  is %s",
                     myCucmConfig.getCucmCert())

        zeeplogger = logging.getLogger('zeep.transports')
        zeeplogger.setLevel(logging.DEBUG)
        zeephandler = logging.FileHandler('zeepDebug.log', mode='w')
        zeephandler.setLevel(logging.DEBUG)
        zeepformatter = logging.Formatter('%(asctime)s - %(name)s - \
                            %(levelname)s - %(message)s')
        zeephandler.setFormatter(zeepformatter)
        zeeplogger.addHandler(zeephandler)
        zeeplogger.info('Begin zeep Logging')

        cache = SqliteCache(path='/tmp/wsdlsqlite.db', timeout=60)
        transport = Transport(cache=cache)
        client = Client(myCucmConfig.getwsdlFileName(), transport=transport)

        session = Session()
        if myCucmConfig.getCucmVerify():
            logger.info("Session Security ENABLED")
            session.verify = myCucmConfig.getCucmCert()
        else:
            logger.info("Session Security DISABLED")
            session.verify = myCucmConfig.getCucmVerify()
        logger.info("Session Created")
        session.auth = HTTPBasicAuth(myCucmConfig.getCucmUsername(),
                                     myCucmConfig.getCucmPassword())
        logger.info("Auth Created")

        client = Client(wsdl=myCucmConfig.getwsdlFileName(),
                        transport=Transport(session=session))
        logger.info("Client Created")

        self.factory = client.type_factory('ns0')
        logger.info("Factory Created")

        self.service = client.create_service(
            "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
            myCucmConfig.getCucmAxlUrl())
        logger.info("Service Created")
