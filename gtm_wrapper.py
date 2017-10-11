import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
import urllib

class GtmWrapper:
	"""
	A simple wrapper for the PAPI calls. Each call maps to a PAPI URL and no tampering of the results is done within the class.
	"""

	def __init__(self, logLevel=logging.INFO):

		## initialize logging as well
		FORMAT = '%(asctime)-15s %(message)s'
		logging.basicConfig(format=FORMAT)
		# logging.basicConfig()
		self.logger = logging.getLogger('gtm_audit')
		self.logger.setLevel(logLevel)
		## completed log initialization

		self.session = requests.Session()
		self.debug = False
		self.verbose = False
		self.section_name = "papi"

		# If all parameters are set already, use them.  Otherwise
		# use the config
		self.config = EdgeGridConfig({},self.section_name)

		if hasattr(self.config, "debug") and self.config.debug:
		  self.debug = True

		if hasattr(self.config, "verbose") and self.config.verbose:
		  self.verbose = True


		# Set the config options
		self.session.auth = EdgeGridAuth(
		            client_token=self.config.client_token,
		            client_secret=self.config.client_secret,
		            access_token=self.config.access_token
		)

		if hasattr(self.config, 'headers'):
		  self.session.headers.update(self.config.headers)

		self.baseurl = '%s://%s/' % ('https', self.config.host)
		self.httpCaller = EdgeGridHttpCaller(self.session, self.debug,self.verbose, self.baseurl)

	def getDomains(self):
		return self.httpCaller.getResult('/config-gtm/v1/domains/')	

	def getSingleDomain(self, domainName):
		return self.httpCaller.getResult('/config-gtm/v1/domains/'+domainName)	

	def getDomainDataCenters(self, domainName):
		self.logger.debug('Fetching data center details using URL: ' +'/config-gtm/v1/domains/'+domainName+'/datacenters' )
		return self.httpCaller.getResult('/config-gtm/v1/domains/'+domainName+'/datacenters')			

	def getDomainProperties(self, domainName):
		return self.httpCaller.getResult('/config-gtm/v1/domains/'+domainName+'/properties')					

	def extractDomainName(self, url):		
		return url.rsplit('/',1)[1]

	def getTargetDetails(self, domain):
		result = {}
		result['name'] = domain['name']
		result['trafficTargets'] = []		
		for target in domain['trafficTargets']:			
			result['trafficTargets'].append({\
					'servers': target['servers'],\
					'handoutCName': target['handoutCName'],\
					'weight': target['weight'],\
					'enabled': target['enabled']
				})
		self.trafficTargets =  result
		if 'livenessTests' in domain and len(domain['livenessTests'])>=1:
			self.livenessTests = domain['livenessTests'][0]
		else:
			self.livenessTests = None

	def getTrafficTargets(self):
		return self.trafficTargets

	def getLivenessTests(self):
		return self.livenessTests

class DataCenter:
	def __init__(self):
		self.datacenterId = 0
		self.nickname = None
		self.city = None
		self.stateOrProvince = None
		self.country = None
		self.continent = None		
		self.latitude = 0.0
		self.longitude = 0.0
		self.defaultLoadObject = {
			"loadObject": None,
			"loadObjectPort": 0,
			"loadServers": None
		}

	def setDataCenterDetails(self, dataCenterObject):
		self.datacenterId = dataCenterObject['datacenterId']
		self.nickname = datacenterId['nickname']
		self.city = datacenterId['city']
		self.stateOrProvince = datacenterId['stateOrProvince']
		self.country = datacenterId['country']
		self.continent = datacenterId['continent']		
		self.latitude = datacenterId['latitude']
		self.longitude = datacenterId['longitude']
		self.defaultLoadObject = {
			"loadObject": datacenterId['defaultLoadObject']['loadObject'],
			"loadObjectPort": datacenterId['defaultLoadObject']['loadObjectPort'],
			"loadServers": datacenterId['defaultLoadObject']['loadServers']
		}

	def printDataCenterDetails(self):
		print ( json.dumps(self) )

	
if __name__=="__main__":
	gtm = GtmWrapper()
	#print gtm.getDomains()
	print ( json.dumps(gtm.getSingleDomain( gtm.extractDomainName('https://akab-eyt7c2nuge444oiq-dhyxfhoxgujxsoji.luna.akamaiapis.net/config-gtm/v1/domains/aws-origin.akadns.net') ),indent=4,sort_keys=True) )
	#print gtm.extractDomainName('https://akab-eyt7c2nuge444oiq-dhyxfhoxgujxsoji.luna.akamaiapis.net/config-gtm/v1/domains/aws-origin.akadns.net')
	#print gtm.getDomainDataCenters( gtm.extractDomainName('https://akab-eyt7c2nuge444oiq-dhyxfhoxgujxsoji.luna.akamaiapis.net/config-gtm/v1/domains/gcs.akadns.net') )