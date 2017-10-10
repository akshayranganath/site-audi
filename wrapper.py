import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
import urllib
import socket
import subprocess
import os

class Wrapper:
	"""
	A simple wrapper for the PAPI calls. Each call maps to a PAPI URL and no tampering of the results is done within the class.
	"""

	def __init__(self): 
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

	def getGroups(self):
		"""Return the group and contract details based on PAPI credentials.

			Keyword arguments:
				None

			Return type:
				List of groups
		"""
		return self.httpCaller.getResult('/papi/v0/groups/')
		

	def getContractNames(self):	
		"""
		Returns the contract id and contract name for a given contract Id

			Keyword arguments:
				None

			Return parameter:
				Hash of contractId and contract name. Same as the output from the raw API call to "/papi/v0/groups/"
		"""
		return self.httpCaller.getResult('/papi/v1/contracts/')	

	def getProducts(self, contractId):
		"""
		Returns the contract information for the contractId

			Keyword arguments:
				contractId 

			Return parameter:
				Contract details
		"""
		return self.httpCaller.getResult('/papi/v0/products/?contractId='+contractId)
		

	def getCPCodes(self, groupId, contractId):
		"""
		Return the CP Code details for a groupId-contractId combination

			Keyword arguments:
				groupId
				contractId
				
			Return parameter:
				List of CP Codes
		"""
		return self.httpCaller.getResult('/papi/v0/cpcodes/?groupId='+groupId+'&contractId='+contractId) 


	def getEdgeHostNames(self,groupId, contractId):
		"""
		Returns the edgehostnames by groupId. If all groups for an account are passed to this function, it will return all the Edge host names associated with the account.

			Keyword arguments:
				groupId
				contractId

			Return parameter:
				List of edge hostnames
		"""			
		return self.httpCaller.getResult('/papi/v0/edgehostnames/?groupId='+groupId+'&contractId='+contractId)				

	def getProperties(self, groupId, contractId):
		"""
		Returns the names of properties associated with a group. If all groups for an account are passed to this function, it will return all the properties associated with the account.

			Keyword arguments:
				groupId
				contractId

			Return parameter:
				List of properties
		"""
		return self.httpCaller.getResult('/papi/v0/properties/?groupId='+groupId+'&contractId='+contractId)		

	def getPropertyVersions(self, propertyId, groupId, contractId):
		"""
		Returns the property versions. This can be used to find the audit trail details for a configuration

			Keyword arguments:
				propertId
				groupId
				contractId

			Return parameters:
				List of property versions
		"""
		return self.httpCaller.getResult('/papi/v0/properties/'+propertyId+'/versions/?groupId='+groupId+'&contractId='+contractId)		


	def getavailableBehavior(self, propertyId,propertyVersion, contractId, groupId ):
		return self.httpCaller.getResult('/papi/v1/properties/'+propertyId+'/versions/'+propertyVersion+'/available-behaviors?contractId='+contractId+'&groupId='+groupId)			

	def getVersionDetails(self, propertyId, groupId, contractId, propertyVersion=1):
		"""
		Returns information about a specific property version

			Keyword arguments:
				propertyVersion: Default version is 1, the first version.
				propertId
				groupId
				contractId

			Return parameters:
				Details on a specific property version
		"""
		return self.httpCaller.getResult('/papi/v0/properties/'+propertyId+'/versions/'+propertyVersion+'?groupId='+groupId+'&contractId='+contractId)		

	def getLatestVersionDetails(self, propertyId, groupId, contractId):
		"""
		Returns information about a specific property version

			Keyword arguments:
				propertyVersion: Default version is 1, the first version.
				propertId
				groupId
				contractId

			Return parameters:
				Details on a specific property version
		"""
		return self.httpCaller.getResult('/papi/v0/properties/latest/versions/'+propertyVersion+'?groupId='+groupId+'&contractId='+contractId)		

	def getConfigRuleTree(self, propertyId, versionNumber, groupId, contractId):
		"""
		Returns all the Property Manager rule details. It will not retrieve advanced code.

			Keyword arguments:
				propertyId
				versionNumber - Specific version for which we need the rules
				groupId
				contractId

			Return parameters:
				Configuration tree rule for a given configuration
		"""
		return self.httpCaller.getResult('/papi/v0/properties/'+propertyId+'/versions/'+versionNumber+'/rules/?groupId='+groupId+'&contractId='+contractId)


	def getPropertyHostNames(self, propertyId, versionNumber, groupId, contractId):
		"""
		Returns the host names associated with a configuration.

			Keyword arguments:
				propertyId
				versionNumber - Specific version for which we need the rules
				groupId
				contractId

			Return parameters:
				List of host names belonging to the configuration			
		"""
		return self.httpCaller.getResult('/papi/v0/properties/'+propertyId+'/versions/'+versionNumber+'/hostnames/?groupId='+groupId+'&contractId='+contractId)


	def getEnrollements(self, contractId):
		"""
		Returns the enrollements associated with a contractId.

			Keyword arguments:
				contractId
				
			Return parameters:
				List of enrollments associated with a contractId			
		"""
		return self.httpCaller.getResult('/cps/v2/enrollments?contractId='+contractId, headers='cps')


	def getCNAME(self, hostname):
		"""
		Runs a dig command to find the CNAME for a given host name.
		If a CNAME is found, it returns it. Else returns a None.

			Keyword arguments:
				hostname: The host name for which we need the CNAME
		"""

		resp = subprocess.check_output(['dig','+short',hostname,'CNAME'])		
		if resp is None or len(resp) == 0:
			resp = None
		else:
			resp = resp.decode().strip().strip('.')
		return resp

	def checkIfCdnIP(self, ipaddress):
		"""
		Returns if an IP address blongs to Akamai or if it is not an Akamai IP. It uses the OS command "host" on systems
		that supports it. Else, it uses the command nslookup.

			Keyword arguments:
				ipaddress

			Return parameters:
				A boolean flag based on whether the call returns a true or a false.
		"""
		result = False
		# don't use the Akamai service. It is impossibly slow.
		#replaced it with simple reverse lookup
		#resp = self.httpCaller.getResult('/diagnostic-tools/v2/ip-addresses/'+ipaddress+'/is-cdn-ip')
		#if 'isCdnIp' in resp and resp['isCdnIp']==True:
		#	result = True		

		try:
			if os.name =="nt":
				resp = str ( subprocess.check_output(['nslookup',ipaddress]) )
				if resp.find('akamai'):
					result=True
			else:
				resp = str( subprocess.check_output(['host', ipaddress]) )
				#print (resp)
				resp = resp.split(' ')
				if len(resp) >=5:
					if resp[4].find('akamai') > -1:
						result=True
		except subprocess.CalledProcessError:
			pass		
		return result

	def getIpAddress(self, hostname):
		result = "0.0.0.0"
		try:
			result =  socket.gethostbyname(hostname)
		except Exception:
			pass
		return result

if __name__=="__main__":
	w = Wrapper()
	#groupdetils =  w.getGroups()
	#print groupdetils
	#print w.getContractNames()
	#cpcodes = getCPCodes(groupdetils)
	#print cpcodes
	#edgeHostNames = getEdgeHostNames(groupdetils)
	#properties = getProperties(groupdetils)
	#productList = getContractProducts(groupdetils)
	#print getContractNames()
	#print w.getProducts('ctr_C-1ED34DY')
	#print json.dumps(w.getCPCodes('grp_63802','ctr_C-1ED34DY'))
	#print json.dumps(w.getEdgeHostNames('grp_63802','ctr_C-1ED34DY'))
	#print (json.dumps(w.getPropertyHostNames('prp_370965','4','grp_63802','ctr_C-1ED34DY')))
	#print ( w.checkIfCdnIP(w.getIpAddress('www.cnn.com')) )
	print ( w.getCNAME('www.example.com') )
