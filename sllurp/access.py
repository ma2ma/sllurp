from __future__ import print_function
import argparse
import logging
# import pprint
import time
from twisted.internet import reactor, defer

import sllurp.llrp as llrp
import pickle
import os
startTime = None
endTime = None

tagReport = 0
is_filter = True
taghash = {}
filterhash = {}
logger = logging.getLogger('sllurp')

args = None

def startTimeMeasurement():
    global startTime
    startTime = time.time()

def stopTimeMeasurement():
    global endTime
    endTime = time.time()

def finish (_):
    global startTime
    global endTime
    global taghash

    # stop runtime measurement to determine rates
    stopTimeMeasurement()
    runTime = (endTime - startTime) if (endTime > startTime) else 0
    fw = open('tags.txt','wb')
    pickle.dump(taghash,fw)
    fw.close()
    logger.info('total # of tags seen: %d (%d tags/second)', tagReport, tagReport/runTime)
    logger.info('record %d tags', len(taghash))
    if reactor.running:
        reactor.stop()

def access (proto):
    readSpecParam = None
    if args.read_words:
        readSpecParam = {
            'OpSpecID': 0,
            'MB': 2,
            'WordPtr': 0,
            'AccessPassword': 0,
            'WordCount': args.read_words
        }

    writeSpecParam = None
    if args.write_words:
        if args.write_words > 1:
            writeSpecParam = {
                'OpSpecID': 0,
                'MB': 3,
                'WordPtr': 0,
                'AccessPassword': 0,
                'WriteDataWordCount': args.write_words,
                'WriteData': '\xde\xad\xbe\xef', # XXX allow user-defined pattern
            }
        else:
            writeSpecParam = {
                'OpSpecID': 0,
                'MB': 3,
                'WordPtr': 0,
                'AccessPassword': 0,
                'WriteDataWordCount': args.write_words,
                'WriteData': '\xbe\xef', # XXX allow user-defined pattern
            }

    return proto.startAccess(readWords=readSpecParam,
            writeWords=writeSpecParam)

def politeShutdown (factory):
    return factory.politeShutdown()

def tagReportCallback (llrpMsg):
    """Function to run each time the reader reports seeing tags."""
    global tagReport
    global taghash
    global filterhash
    global is_filter
    tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
    if len(tags):
        # logger.info('saw tag(s): %s', pprint.pformat(tags))
        pass
    else:
        # logger.info('no tags seen')
        return
    for tag in tags:
        if 'OpSpecResult' in tag.keys():
            epc_96=tag['EPC-96'][8:]
            if ( not tag['EPC-96'] in taghash ) and ( (not is_filter) or epc_96 in filterhash ) and (tag['OpSpecResult']['ReadData'].encode('hex') != ''):
                if epc_96 in filterhash:
                    taghash[tag['EPC-96']] =[  tag['OpSpecResult']['ReadData'].encode('hex'),filterhash[epc_96] ]
                    logger.info('tid:%r,:epc:%r,name:%r',tag['OpSpecResult']['ReadData'].encode('hex'),tag['EPC-96'],filterhash[epc_96])
                else:
                    taghash[tag['EPC-96']] =[  tag['OpSpecResult']['ReadData'].encode('hex'),"" ]
                    logger.info('tid:%r,:epc:%r,name:%r',tag['OpSpecResult']['ReadData'].encode('hex'),tag['EPC-96'],"")
        tagReport += tag['TagSeenCount'][0]

def parse_args ():
    global args
    parser = argparse.ArgumentParser(description='Simple RFID Reader Inventory')
    parser.add_argument('host', help='hostname or IP address of RFID reader',
            nargs='*')
    parser.add_argument('-p', '--port', default=llrp.LLRP_PORT, type=int,
            help='port to connect to (default {})'.format(llrp.LLRP_PORT))
    parser.add_argument('-t', '--time', default=10, type=float,
            help='number of seconds for which to inventory (default 10)')
    parser.add_argument('-d', '--debug', action='store_true',
            help='show debugging output')
    parser.add_argument('-n', '--report-every-n-tags', default=1, type=int,
            dest='every_n', metavar='N', help='issue a TagReport every N tags')
    parser.add_argument('-X', '--tx-power', default=0, type=int,
            dest='tx_power', help='Transmit power (default 0=max power)')
    parser.add_argument('-M', '--modulation', default='M8',
            help='modulation (default M8)')
    parser.add_argument('-T', '--tari', default=0, type=int,
            help='Tari value (default 0=auto)')
    parser.add_argument('-s', '--session', default=2, type=int,
            help='Gen2 session (default 2)')
    parser.add_argument('-P', '--tag-population', default=4, type=int,
            dest='population', help="Tag Population value (default 4)")
    parser.add_argument('-f', '--filter-epc', default=1, type=int,
            help="1 is filter epc (default 1)")

    # read or write
    op = parser.add_mutually_exclusive_group(required=True)
    op.add_argument('-r', '--read-words', type=int,
            help='Number of words to read from MB 0 WordPtr 0')
    op.add_argument('-w', '--write-words', type=int,
            help='Number of words to write to MB 0 WordPtr 0')
    parser.add_argument('-l', '--logfile')

    args = parser.parse_args()

def init_logging ():
    logLevel = (args.debug and logging.DEBUG or logging.INFO)
    logFormat = '%(asctime)s %(name)s: %(levelname)s: %(message)s'
    formatter = logging.Formatter(logFormat)
    stderr = logging.StreamHandler()
    stderr.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logLevel)
    root.handlers = [stderr,]

    if args.logfile:
        fHandler = logging.FileHandler(args.logfile)
        fHandler.setFormatter(formatter)
        root.addHandler(fHandler)

    logger.log(logLevel, 'log level: %s', logging.getLevelName(logLevel))

def read_hash():
    global taghash
    global filterhash
    if not os.path.isfile('tags.txt'):
        fw = open('tags.txt','wb')
        pickle.dump({},fw)
        fw.close()
    if not os.path.isfile('filter.txt'):
        fw = open('filter.txt','wb')
        fw.write("")
        fw.close()
    f = open('tags.txt','rb')
    f1 = open('filter.txt','rb')
    taghash= pickle.load(f)
    f.close()
    for line in f1.readlines():
        if line.strip() != "":
            f = line.strip().split(",",1)
            # print(f)
            filterhash[f[0]] =f[1]
    print(taghash)
    print("-----------------------------")
    # print(filterhash)

def main ():
    global is_filter
    parse_args()
    init_logging()
    if args.filter_epc != 1:
        is_filter = False
    # print(args.filter_epc)
    read_hash()
    # will be called when all connections have terminated normally
    onFinish = defer.Deferred()
    onFinish.addCallback(finish)

    fac = llrp.LLRPClientFactory(onFinish=onFinish,
            disconnect_when_done=True,
            modulation=args.modulation,
            tari=args.tari,
            session=args.session,
            tag_population=args.population,
            start_inventory=True,
            tx_power=args.tx_power,
            report_every_n_tags=args.every_n,
            tag_content_selector={
                'EnableROSpecID': False,
                'EnableSpecIndex': False,
                'EnableInventoryParameterSpecID': False,
                'EnableAntennaID': True,
                'EnableChannelIndex': False,
                'EnablePeakRRSI': True,
                'EnableFirstSeenTimestamp': False,
                'EnableLastSeenTimestamp': True,
                'EnableTagSeenCount': True,
                'EnableAccessSpecID': True
            })

    # tagReportCallback will be called every time the reader sends a TagReport
    # message (i.e., when it has "seen" tags).
    fac.addTagReportCallback(tagReportCallback)

    # start tag access once inventorying
    fac.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, access)

    for host in args.host:
        reactor.connectTCP(host, args.port, fac, timeout=3)

    # catch ctrl-C and stop inventory before disconnecting
    reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)

    # start runtime measurement to determine rates
    startTimeMeasurement()

    reactor.run()

if __name__ == '__main__':
    main()
