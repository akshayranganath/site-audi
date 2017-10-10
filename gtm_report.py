from gtm_wrapper import GtmWrapper
import json
import csv
import os
import logging
import argparse

def createFile(fileName='gtm'):
	try:
		os.stat('gtm')
	except:
		os.mkdir('gtm')

def getDomains(gtm):
	gtmDdomains = []
	for gtmDomain in gtm.getDomains()['items']:
		gtm_url = gtmDomain['links'][0]['href']
		gtmDdomains.append( gtm.extractDomainName(gtm_url) )
	return gtmDdomains

def getDomainDetails(gtm, gtmDomains):
	gtmProperties = []
	for gtmDomain in gtmDomains:		
		domain = gtm.getSingleDomain(gtmDomain)		
		gtmTarget = {}
		gtmTarget['name'] = domain['name']		
		gtmTarget['properties'] = []
		for target in domain['properties']:
			gtm.getTargetDetails( target )			
			gtmTarget['properties'].append( gtm.getTrafficTargets() )
			gtmTarget['livenessTests'] = gtm.getLivenessTests()
		# add the LIF and property type details
		gtmTarget['loadImbalancePercentage'] = domain['loadImbalancePercentage']
		logger.debug(domain['name'] + ' has a LIF of ' + str(gtmTarget['loadImbalancePercentage']))
		gtmTarget['type'] = domain['type']
		logger.debug(domain['name'] + ' is a setup of type: ' + gtmTarget['type'])
		gtmProperties.append(gtmTarget)
	return gtmProperties

def getDCDetails(gtm, gtmDomain):
	return gtm.getDomainDataCenters(gtmDomain)

def printCSV(domainDetails):
	createFile()
	domainName 	= None	
	for domain in domainDetails:
		domainName = domain['name']			
		with open('gtm/'+domainName+'.csv','w') as csvfile:
			fileWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			fileWriter.writerow(['GTM Property','Weight','Servers','CNAME', 'Imbalance Factor', 'Type'])
			for property in domain['properties']:
				logger.debug( json.dumps(domain, indent=2) )
				propertyName = property['name']
				for target in property['trafficTargets']:					
					if target['enabled']:
						fileWriter.writerow([ propertyName + '.' + domainName, target['weight'], '|'.join( target['servers'] ), target['handoutCName'],domain['loadImbalancePercentage'],domain['type'] ])
			fileWriter = None
	
		if 'livenessTests' in domain and domain['livenessTests']!=None:
			with open('gtm/'+domainName+'_liveness.csv','w') as csvfile:
				fileWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				fileWriter.writerow(['GTM Property','Name','Host','Path','Protocol','Interval','Return Code'])
				liveness = domain['livenessTests']
				returnCode = '200'			
				if liveness['httpError3xx']!=None:
					returnCode += ', 3xx'
				if liveness['httpError4xx']!=None:
					returnCode += ', 4xx'
				if liveness['httpError5xx']!=None:				
					returnCode += ', 4xx'				
				fileWriter.writerow([domain['name'],liveness['name'],liveness['hostHeader'],liveness['testObject'],liveness['testObjectProtocol'],liveness['testInterval'],returnCode])

		# now get the data center details and pring it
		logger.debug('Fetching dc details for: ' + domain['name'])
		dcDetails = getDCDetails(gtm, domain['name'])
		logger.debug(dcDetails)

		if dcDetails != None and dcDetails!= {}:
			with open('gtm/'+domainName+"_dcdetails.csv",'w') as csvfile:
				fileWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				fileWriter.writerow(['GTM Property', 'DC Nick-Name', 'Lat', 'Long', 'City', 'State/Province','Country', 'Continent'])
				for datacenter in dcDetails['items']:
					fileWriter.writerow([ domainName, datacenter['nickname'],str(datacenter['latitude']),str(datacenter['longitude']),datacenter['stateOrProvince'],datacenter['city'],datacenter['country'],datacenter['continent'] ])
					

if __name__=="__main__":
	FORMAT = '%(asctime)-15s %(message)s'
	logging.basicConfig(format=FORMAT)
	# logging.basicConfig()
	logger = logging.getLogger('gtm_audit')
	logger.setLevel(logging.INFO)
	parser = argparse.ArgumentParser(
		description="A GTM auditing script that will fetch the names of GTM, the associated data center details, liveness object information and the server details.")
	parser.add_argument('-v', '--verbose', help="Enable debug mode for more granular visibility",
						action="store_true",
						required=False)
	args = parser.parse_args()
	if args.verbose == True:
		logger.info('Bumping up logging level to DEBUG mode')
		logger.setLevel(logging.DEBUG)

	gtm = GtmWrapper(logLevel=args.verbose)
	#first get the names of the domains
	gtmDomains = getDomains(gtm)	
	#for the domains, get the target details
	domainDetails = getDomainDetails(gtm, gtmDomains)
	#print json.dumps(domainDetails, indent=4, sort_keys=4)
	printCSV(domainDetails)
	logger.info('GTM Reporting generation is now complete.')
