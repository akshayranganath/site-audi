'''
// Good luck with this code. Do praise if its good.
// And dont curse if its bad :)
Author: Vreddhi Bhat and Bhavin Dutia
Contact: vbhat@akamai.com and bdutia@akamai.com
'''

import originpapitools
import configparser
import requests, logging, json
from akamai.edgegrid import EdgeGridAuth
import json
import argparse
import os
import csv
from xlsxwriter.workbook import Workbook


#Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')
logFile = os.path.join('logs', 'origin_log.log')

#Set the format of logging in console and file seperately
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleFormatter = logging.Formatter("%(message)s")
rootLogger = logging.getLogger()

logfileHandler = logging.FileHandler(logFile, mode='w')
logfileHandler.setFormatter(logFormatter)
rootLogger.addHandler(logfileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(consoleFormatter)
rootLogger.addHandler(consoleHandler)
#Set Log Level to DEBUG, INFO, WARNING, ERROR, CRITICAL
rootLogger.setLevel(logging.INFO)

try:
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser("~"),'.edgerc'))
    client_token = config['papi']['client_token']
    client_secret = config['papi']['client_secret']
    access_token = config['papi']['access_token']
    access_hostname = config['papi']['host']
    session = requests.Session()
    session.auth = EdgeGridAuth(
                client_token = client_token,
                client_secret = client_secret,
                access_token = access_token
                )
except (NameError, AttributeError, KeyError):
    rootLogger.info("\nError parsing credentials: Please check that your '~/.edgerc' file exists and contains a [papi] section.\n")
    exit()

parser = argparse.ArgumentParser()
parser.add_argument("-generateAudit",help="Generate origin server details for all property configurations", action="store_true")

#parser.add_argument("-generateAuditForOneConfig",help="Generates audit for a config",action="store_true")

#Additional arguments
#parser.add_argument("-propertyName",help="Enter name of property")
#parser.add_argument("-version",help="Enter version of property")
#parser.add_argument("-propertyId",help="Enter propertyId of property")
#parser.add_argument("-groupId",help="Enter groupId of property")
#parser.add_argument("-contractId",help="Enter contractId of property")



args = parser.parse_args()

if not args.generateAudit:
    rootLogger.info("Use -h to know the options to run program")
    exit()

#Recursive function to crawl rules and find origin behavior
def getChildRules(parentRule,propertyName):
    for eachRule in parentRule:
        ruleName = eachRule['name']
        for eachBehavior in eachRule['behaviors']:     
            if eachBehavior['name'] == 'origin' :
                #print("Inside recursive function of rule ",ruleName)
                writeOriginInfo(eachBehavior,propertyName)

        if len(eachRule['children']) != 0:
            getChildRules(eachRule['children'],propertyName)


def writeOriginInfo(behavior,propertyName):

    try:
        if propertyName is not None:
            #print ("Property Name is ",propertyName)
            originLine = propertyName + ','

        #Start with default value then update it    
        originType = 'Unknown'
        if 'originType' in behavior['options'] is not None: 
            originType = behavior['options']['originType']
            if originType == 'CUSTOMER':
                originType = 'Customer'

            if originType == 'NET_STORAGE':
                originType = 'NetStorage'


        originLine += originType + ','
    

        hostname = 'Undefined'
        forwardHostHeader = 'Undefined'
        cacheKeyHostname = 'Undefined'
        verificationMode = 'N/A'
        originSni = 'N/A'
        customValidCnValuesList = 'N/A'
        originCertsToHonor = 'N/A'
        akamaiCertificateStoreEnabled = 'N/A'
        thirdPartyCertificateStoreEnabled = 'N/A'
        pinCertificateAuthority = 'No'
        pinSpecificCertificates = 'No'
        httpPort = 'Undefined'
        httpsPort = 'N/A'


        if 'hostname' in behavior['options'] is not None:
            #print ("Hostname is ",behavior['options']['hostname'])
            #originLine += behavior['options']['hostname']
            hostname = behavior['options']['hostname']

        if 'forwardHostHeader' in behavior['options'] is not None:
            #print ("Hostname is ",behavior['options']['hostname'])
            #originLine += behavior['options']['hostname']
            forwardHostHeader = behavior['options']['forwardHostHeader']

            if forwardHostHeader == 'REQUEST_HOST_HEADER':
                forwardHostHeader = 'Incoming Host Header'

            elif forwardHostHeader == 'ORIGIN_HOSTNAME':
                forwardHostHeader = 'Origin Hostname'

            elif forwardHostHeader == 'CUSTOM':
                forwardHostHeader = 'Custom Value'


        if 'cacheKeyHostname' in behavior['options'] is not None:
            #print ("Hostname is ",behavior['options']['hostname'])
            #originLine += behavior['options']['hostname']
            cacheKeyHostname = behavior['options']['cacheKeyHostname']

            if cacheKeyHostname == 'REQUEST_HOST_HEADER':
                cacheKeyHostname = 'Incoming Host Header'

            elif cacheKeyHostname == 'ORIGIN_HOSTNAME':
                cacheKeyHostname = 'Origin Hostname'

            elif cacheKeyHostname == 'CUSTOM':
                cacheKeyHostname = 'Custom'

        if 'verificationMode' in behavior['options'] is not None:
            #print ("Hostname is ",behavior['options']['hostname'])
            #originLine += behavior['options']['hostname']
            verificationMode = behavior['options']['verificationMode']

            if verificationMode == 'PLATFORM_SETTINGS':
                verificationMode = 'Use Platform Settings'

            elif verificationMode == 'THIRD_PARTY':
                verificationMode = 'Third Party Settings'

            elif verificationMode == 'CUSTOM':
                verificationMode = 'Choose Your Own (Recommended)'



        if 'originSni' in behavior['options'] is not None:
            #print ("Hostname is ",behavior['options']['hostname'])
            #originLine += behavior['options']['hostname']
            originSni = behavior['options']['originSni']  
            if  originSni == 'true':
                originSni = 'Yes'
            else:
                originSni = 'No'


        if 'netStorage' in behavior['options'] is not None :
            netStorage = behavior['options']['netStorage']
            if netStorage is not None:
                if netStorage['downloadDomainName'] is not None :
                    #print ("Netstorage domain is ",netStorage['downloadDomainName'])  
                    #originLine += netStorage['downloadDomainName']
                    hostname = netStorage['downloadDomainName']
                    cacheKeyHostname='Origin Hostname'
                    forwardHostHeader='Origin Hostname'
                    httpPort='80'
                    httpsPort='443'
                else:
                    #print ("Hostname Undefined")
                    #originLine += 'Undefined'
                    hostname = 'Undefined'

        if 'customValidCnValues' in behavior['options'] is not None: 
            customValidCnValuesList = '' 
            for customValidCnValues in behavior['options']['customValidCnValues']:
                #print ("Custom Valid CN Value is ",customValidCnValues) 
                customValidCnValuesList += customValidCnValues + ' '
        #originLine += customValidCnValuesList + ','      

        if 'originCertsToHonor' in behavior['options'] is not None:
            originCertsToHonor = behavior['options']['originCertsToHonor']

            if originCertsToHonor == 'STANDARD_CERTIFICATE_AUTHORITIES':
                originCertsToHonor = 'Akamai-Managed Certificate Authorities Sets'

            if originCertsToHonor == 'CUSTOM_CERTIFICATE_AUTHORITIES':
                originCertsToHonor = 'Custom Certificate Authority Set'

            if originCertsToHonor == 'CUSTOM_CERTIFICATES':
                originCertsToHonor = 'Specific Certificates (pinning)'

            if originCertsToHonor == 'COMBO':
                originCertsToHonor = 'Satisfies any of the trust options below'


        if 'standardCertificateAuthorities' in behavior['options'] is not None:
            akamaiCertificateStoreEnabled = 'Disabled'
            thirdPartyCertificateStoreEnabled = 'Disabled'

            #for standardCertificateAuthorities in behavior['options']['standardCertificateAuthorities']:
            standardCertificateAuthorities = behavior['options']['standardCertificateAuthorities']
            
            if 'akamai-permissive' in standardCertificateAuthorities:
                akamaiCertificateStoreEnabled = 'Enabled'

            if 'THIRD_PARTY_AMAZON' in standardCertificateAuthorities:
                thirdPartyCertificateStoreEnabled = 'Enabled'

        if 'customCertificateAuthorities' in behavior['options'] is not None:
            pinAuthorityCount = len(behavior['options']['customCertificateAuthorities'])
            if pinAuthorityCount > 0:
                pinCertificateAuthority = 'Yes'

        if 'customCertificates' in behavior['options'] is not None:
            pinSpecificCount = len(behavior['options']['customCertificates'])
            if pinSpecificCount > 0:
                pinSpecificCertificates = 'Yes'

        if 'httpPort' in behavior['options'] is not None:
            httpPort = str(behavior['options']['httpPort'])

        if 'httpsPort' in behavior['options'] is not None:
            httpsPort = str(behavior['options']['httpsPort'])



            #print ("Origin Certs to honor ",originCertsToHonor)
            #originLine += originCertsToHonor
        #originLine += ','         

        
        originLine += hostname+ ',' + forwardHostHeader + ',' + cacheKeyHostname + ',' + verificationMode + ',' + originSni + ',' + customValidCnValuesList + ',' + originCertsToHonor + ',' + akamaiCertificateStoreEnabled + ',' + thirdPartyCertificateStoreEnabled + ',' + pinCertificateAuthority + ',' + pinSpecificCertificates + ',' + httpPort + ',' + httpsPort + ','

        #originLine += ','         

    except KeyError:
            rootLogger.info('Error with behavior being passed to write function')    

    with open(os.path.join('output',originAuditCSVFile),'a') as fileHandler:
                    fileHandler.write(originLine)
                    fileHandler.write('\n')



def getOriginInfo(OriginPapiToolsObject,propertyName,version,propertyId,groupId,contractId):
    rootLogger.info('Fetching origin details for property: '+propertyName)
    '''
    print ("====================================================")
    rootLogger.info('Fetching ' + propertyName + ' Origin Info')
    rootLogger.info('Fetching ' + propertyId + ' PropertyId Info')
    rootLogger.info('Fetching ' + groupId + ' groupId Info')
    rootLogger.info('Fetching ' + contractId + ' contractId Info')
    '''

    RulesObject = OriginPapiToolsObject.getPropertyRulesfromPropertyId(session, propertyId, version, contractId, groupId)
    if RulesObject.status_code != 200:
       rootLogger.info('Some problem.. Lets start breaking our head now...')
       exit()
    else:
        #Lets start updating the username and password now
        propertyJson = RulesObject.json()
        try:
            rootLogger.debug('Parsing the rules of: ' + propertyName + ' version: ' + str(version))
            #print('Property Name is ',propertyName)
            #print('Property Version is',str(version))
            defaultBehavior = propertyJson['rules']['behaviors']
            for eachDefaultBehavior in defaultBehavior:
                if eachDefaultBehavior['name'] == 'origin' :
                    #print('Behavior Name is ',eachDefaultBehavior['name'])
                    #print('Default Origin type is ',eachDefaultBehavior['options']['originType'])
                    writeOriginInfo(eachDefaultBehavior,propertyName)
        except KeyError:
            print("Looks like there are no default rules")            


        try:
            RulesList = propertyJson['rules']['children']
            for eachRule in RulesList:
                ruleName = eachRule['name']
                for eachBehavior in eachRule['behaviors']:
                    #print ('Child Behavior name is ',eachChildBehavior['name'])
                    if eachBehavior['name'] == 'origin' :
                        #print ('**********Printing Origin Behaviors*****************')
                        #print ('Rule name corresponding to origin behavior ',ruleName)
                        writeOriginInfo(eachBehavior,propertyName)
                        #print ('**********End Origin Info ***********')

                if len(eachRule['children']) != 0:
                    getChildRules(eachRule['children'],propertyName)

        except KeyError:
            print("Looks like there are no rules other than default rule")        

if  args.generateAudit:
    originAuditCSVFile = 'origin-audit.csv'
    originAuditXLSXFile = 'origin-audit.xlsx'

    if not os.path.exists('output'):
        os.makedirs('output')
    with open(os.path.join('output',originAuditCSVFile),'w') as fileHandler:
       fileHandler.write('Property Name,Origin Type,Origin Server Hostname,Forward Host Header,Cache Key Hostname,Verification Settings,Use SNI TLS Extension,Match CN/SAN To,Trust,Akamai Certificate Store Enabled,Third Party Certificate Store Enabled,Pin Custom Certificate Authority Set, Pin Specific Certificates, HTTP Port,HTTPS Port\n')

    OriginPapiToolsObject = originpapitools.Originpapitools(access_hostname=access_hostname)
    rootLogger.info('Getting property list....')
    propertyDetailsMap = OriginPapiToolsObject.populateDetailsInMemory(session)
    print('Total number of properties are ',len(propertyDetailsMap))

    for everyPropertyDetail in propertyDetailsMap:
        version = everyPropertyDetail['latestVersion']
        propertyName = everyPropertyDetail['propertyName']
        propertyId = everyPropertyDetail['propertyId']
        groupId = everyPropertyDetail['groupId']
        contractId = everyPropertyDetail['contractId']

        #print("Contract ID is ",contractId)
        #print("propertyName  is ",propertyName)

        getOriginInfo(OriginPapiToolsObject, propertyName, version, propertyId, groupId, contractId)

    # Merge CSV files into XLSX
    workbook = Workbook(os.path.join('output',originAuditXLSXFile))
    worksheet = workbook.add_worksheet('Origin Audit')
    with open(os.path.join('output',originAuditCSVFile), 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()

    rootLogger.info('Success: File written to output/' + originAuditXLSXFile)
    os.remove(os.path.join('output', originAuditCSVFile))

