from wrapper import Wrapper
import json
import pprint
from time import gmtime, strftime
import subprocess
from origin_settings import Origin_Settings 
import os
import time


class Aggregator:
	def __init__(self):
		self.wrapper = Wrapper()

	def createFolder(self,accountName):
		self.md_path =  accountName.replace(' ','_') + '-' + str(int(time.time())) + '/'
		try:
			os.stat(self.md_path)
		except:
			os.mkdir(self.md_path)
		

	def getProducts(self, contractId):
		"""
		Return the set of products within a contract as a comma seperated list
		"""

		products = self.wrapper.getProducts(contractId)		
		productNames = []

		
		if 'products' in products:
			for product in products['products']['items']:
				productNames.append(product['productName'])

		if len(productNames) > 1:
			return ",".join(productNames)
		else:
			return ''

	def printAccountTable(self):
		"""
		Gets a holistic view of the account.
		Print the Account details, Contracts and Groups as one spread sheet
		"""
		groups = self.wrapper.getGroups()
		#also save the groups for later functions
		self.groups = groups

		md_file_path = self.createFolder(groups['accountName'])
		with open(self.md_path+"account.md","w") as mdfile:
			fileWriter = mdfile
			
			# write the account details
			fileWriter.write('''
| Account Id | Account Name |
| ---------- | ------------ |
''' )
			fileWriter.write('|' + '|'.join( [ groups['accountId'][4:] , groups['accountName'] ] ) + '|' )			
			fileWriter.write("\n\n" )
			# write the contract details
			contracts = self.wrapper.getContractNames()		
			fileWriter.write('''
| Contract Id | Contract Name | Products |
| ----------- | ------------- | -------- |
''')
			for contract in contracts['contracts']['items']:	
				products = self.getProducts(contract['contractId'])
				fileWriter.write('|' + '|'.join([ contract['contractId'][4:], contract['contractTypeName'], products ]) + '|')		
			fileWriter.write("\n\n" )

			#write the group details
			fileWriter.write('''
| Group Id | Group Name |
| -------- | ---------- |
''' )
			for group in groups['groups']['items']:				
				fileWriter.write( '|' + group['groupId'][4:] + '|' +  group['groupName'] +'|')		
		
	def printCPCodes(self):
		"""
		Prints the CP Code details for the account. For each CP Code, it will print the Group Id, Contract Id, CP Code, CP Code Name and Products associated with the CP Code.
		"""
		with open(self.md_path+"cpcodes.md","w") as mdfile:
			fileWriter = mdfile
			fileWriter.write('''
| Group Id | Contract Id | CP Code Id | CP Code Name | CP Code Products |
| -------- | ----------- | ---------- | ------------ | ---------------- |
''')
			#now loop through the groups and get the CP Codes
			for group in self.groups['groups']['items']:
				groupId = group['groupId']
				if 'contractIds' in group:
					for contractId in group['contractIds']:
						cpcodes = self.wrapper.getCPCodes(groupId, contractId)
						#print the details
						if 'cpcodes' in cpcodes:
							for cpcode in cpcodes['cpcodes']['items']:
								#remove the leading prd_
								products = []
								for product in cpcode['productIds']:
									products.append(product[4:])
								fileWriter.write( '|' + '|'.join ( [groupId[4:], contractId[4:], cpcode['cpcodeId'][4:], cpcode['cpcodeName'], "|".join(products)] ) + '|' + "\n" )

	def printEdgeHostNames(self):
		with open(self.md_path+"edgehostnames.md","w") as mdfile:
			fileWriter = mdfile
			fileWriter.write('''
| Group Id | Contract Id | Edge Host Id | Edge Host Name | Edge Host Domain Suffix | Secure | IPVersion |
| -------- | ----------- | ------------ | -------------- | ----------------------- | ------ | --------- |
''')
			#now loop through the groups and get the CP Codes
			for group in self.groups['groups']['items']:
				groupId = group['groupId']
				if 'contractIds' in group:
					for contractId in group['contractIds']:							
						edgeHostNames = self.wrapper.getEdgeHostNames(groupId, contractId)
						if 'edgeHostnames' in edgeHostNames:
							for edgeHostName in edgeHostNames['edgeHostnames']['items']:
								fileWriter.write('|' +  '|'.join ([groupId[4:], contractId[4:], edgeHostName['edgeHostnameId'][4:], edgeHostName['edgeHostnameDomain'], edgeHostName['domainSuffix'], str( edgeHostName['secure'] ), edgeHostName['ipVersionBehavior'] ] ) + "|\n" )
		

	def printPropertiesDetails(self, *args):
		"""
		Prints the configuration details.
		"""
		print('Start time is ',strftime("%Y-%m-%d %H:%M:%S", gmtime()))
		print('generating config data.....')
		propertyDict = {}
		total_groups  = len(self.groups['groups']['items'])
		for group in self.groups['groups']['items']:
			groupId = group['groupId']
			print ("Fetching configs for group: " + groupId)
			print (str(total_groups) + " groups remaining...")
			total_groups -= 1
			if 'contractIds' in group:				
				for contractId in group['contractIds']:
					location_result = self.wrapper.getProperties(groupId, contractId)
					if 'properties' in location_result:					
						for config_details in location_result['properties']['items']:
							# Assign values to variables here for readability and will be used in rest of function.  
							groupId = config_details['groupId']
							contractId = config_details['contractId']
							propertyId = config_details['propertyId']
							productionVersion = config_details['productionVersion']
							stgVersion = config_details['stagingVersion']
							latestVersion = config_details['latestVersion']
							firstVersion = 1
							productId = None

							#Populate the propertyDict which we will  used in rest of the function.
							propertyDict[config_details['propertyName']] = {
								'groupId': groupId, 
								'contractId': contractId, 
								'propertyId': propertyId, 
								'productionVersion': productionVersion, 
								'stagingVersion': stgVersion, 
								'latestVersion': latestVersion,
								'firstVersion': firstVersion,						
								'productId': productId
								}
							
							if args:
								for config_env in args:
									config_version = propertyDict[config_details['propertyName']][config_env]
									if config_version is not None:								
										get_version = self.wrapper.getVersionDetails(propertyId,groupId,contractId,str(config_version))
										if 'versions' in get_version:
											for item in get_version['versions']['items']:
												propertyDict[config_details['propertyName']].update({ 
												 config_env + '_Updated_User': item['updatedByUser'], 
												 config_env + '_Updated_Time': item['updatedDate'],
												#add the product information							
												})
												if productId == None:
													productId = item['productId']
													# print ('************' , propertyDict  , '***********')
													# print (config_env , ' is the the env and  prod id is' , productId )
									else:
										propertyDict[config_details['propertyName']].update({
										 		config_env + '_Updated_User' : 'No_' + config_env  , 
										 		config_env +'_Updated_Time' : 'No_' + config_env,
										 	})

							#now set the property product informtion
							propertyDict[config_details['propertyName']]['productId'] = productId
							# get latest prperty version details

							## Now find the prod version, else stage else latest version and pass that to get the host names and the origin details
							pmProperty = propertyDict[config_details['propertyName']]
							version = pmProperty['latestVersion']
							# print(pmProperty['productionVersion']) gives None 
							#print(type(pmProperty['productionVersion'])) gives <class 'NoneType'>
							if ('productionVersion' in pmProperty) and (pmProperty['productionVersion'] is not None):
								version = pmProperty['productionVersion']
							else:
								if ('stagingVersion' in pmProperty) and (pmProperty['stagingVersion'] is not None):
									version = pmProperty['stagingVersion']
							# now get the host names
							pmProperty['hostnames'] = self.getPropertyHostDetails(pmProperty['groupId'],pmProperty['contractId'],pmProperty['propertyId'], str(version))
							pmProperty['origins'] = self.getPropertyOriginDetails(pmProperty['groupId'],pmProperty['contractId'],pmProperty['propertyId'], str(version))
							pmProperty['behaviors'] =self.getBehaviorDetails()


		#print('Final Dict value is ' ,propertyDict)				
		print('Number of config is the account is ' ,len (propertyDict))
		print('Done generating config data.....')
		with open(self.md_path+"properties.md","w") as mdfile:
			fileWriter = mdfile
			fileWriter.write('''
| Config Name | Property ID | Group ID | Contract Id | Product | Prod Version | Prod version updatedby | Prod version updated at| latest Version | latest Version updatedby | latest Version updated at | staging Version | staging Version updatedby | staging version updated at | First version updated by | First Version Created at | Behaviors|
''')
			for Configkey, ConfigValue in propertyDict.items():
				#adding a try block to ignore the 'KeyError: 'firstVersion_Updated_User' exception
				#try:
				
				op = '|' + '|'.join( [Configkey, ConfigValue['propertyId'][4:], ConfigValue['groupId'][4:], ConfigValue['contractId'][4:], \
					ConfigValue['productId'][4:], str(ConfigValue['productionVersion']), str(ConfigValue['productionVersion_Updated_User']), str(ConfigValue['productionVersion_Updated_Time']), \
					str(ConfigValue['latestVersion']), str(ConfigValue['latestVersion_Updated_User']), str(ConfigValue['latestVersion_Updated_Time']), \
					str(ConfigValue['stagingVersion']) ,  str(ConfigValue['stagingVersion_Updated_User']), str(ConfigValue['stagingVersion_Updated_Time']), str(ConfigValue['firstVersion_Updated_User']), \
					str(ConfigValue['firstVersion_Updated_Time']), ConfigValue['behaviors'] ] ) + "|\n"
				#print '************** writing a row to property file: ' + op + ' ***********'
				fileWriter.write(op)
				#except Exception:
				#	pass
		
		print('properties.md generated')
		print ('Now fetching origin details...')
		self.printPropertyOrigins(propertyDict)
		print ('Fetching Origin details is now complete')
		print ('Fetching Host name details')
		self.printPropertyHostNames(propertyDict)
		print ('Fetching Hosts is now complete')		
		# print the host name details		 
		print('End time is', (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

	def printPropertyOrigins(self, propertyDict):
		# print the origin details
		with open(self.md_path+"origins.md","w") as mdfile:
			fileWriter = mdfile
			fileWriter.write('''
Config Name | Group ID | Contract Id | Origin Host Name | Origin Type|
''')			
			for Configkey, ConfigValue in propertyDict.items():
				for origin in ConfigValue['origins']:
					fileWriter.write('|' + '|'.join([ Configkey, ConfigValue['groupId'][4:], ConfigValue['contractId'][4:], origin['hostname'], origin['originType'] ] ) + "|\n")

	def printPropertyHostNames(self, propertyDict):
		# now write the host name details
		with open(self.md_path+"hostnames.md","w") as mdfile:
			fileWriter = mdfile
			fileWriter.write('''
Config Name | Group ID | Contract Id | Host Name | Defined CNAMED | Actual CNAME | Secure| 
''')	
			for Configkey, ConfigValue in propertyDict.items():	
				for host in ConfigValue['hostnames']:	
					fileWriter.write('|' + '|'.join ( [Configkey, ConfigValue['groupId'][4:], ConfigValue['contractId'][4:], host['host'], str(host['cname_defined']), host['cname_actual'], str( host["secure"] ) ]) + "|\n" )


	def getPropertyHostDetails(self, groupId, contractId, propertyId, propertyVersion):
		# for the property, get the host names, origin names and if the host names are CNAMED to Akamai	
		#print ("getting property details for " + propertyId)
		hostdetailsJSON = self.wrapper.getPropertyHostNames(propertyId, propertyVersion, groupId, contractId)		
		hostnames = []
		
		if 'hostnames' in hostdetailsJSON:
			for hostname in hostdetailsJSON['hostnames']['items']:			
				host = ""
				cname_defined = ""

				if 'cnameFrom' in hostname:
					host = hostname['cnameFrom']
				
				if 'cnameTo' in hostname:
					cname_defined = hostname['cnameTo']

				cname_actual = "None" if self.getCNAME(host)==None else self.getCNAME(host)
				
						
				if cname_actual is not None and len(cname_actual) > 0 and (cname_actual.endswith('.akamaiedge.net') or cname_actual.endswith('.edgekey.net') ):
					secureHostName = True			
				else:
					secureHostName = False	

				hostnames.append({ 'host': host, \
					 'cname_defined': cname_defined, \
					 'cname_actual': cname_actual, \
					 'secure' : secureHostName
					})

		return hostnames		

	def getPropertyOriginDetails(self, groupId, contractId, propertyId, propertyVersion):
		#print ("getting origin details for " + propertyId)
		#first get the configuration rules
		self.rules = self.wrapper.getConfigRuleTree(propertyId, propertyVersion, groupId, contractId)
		self.origin = Origin_Settings()
		origin_details = self.origin.findOrigins(self.rules)

		#replace origin for GTM with the word GTM
		for origin in origin_details:
			if origin['hostname'].endswith('akadns.net'):
				origin['originType'] = 'GTM'

		return origin_details

	def getBehaviorDetails(self):
		return ", ".join( self.origin.findOrigins(self.rules, 'behaviors') )

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

	def getEnrollments(self):
		"""
		get a list enrollments  using CPS API for a contract and returns a list of enrollments 
		"""
		contracts = self.wrapper.getContractNames()
		enrollments_list = []
		for contract in contracts['contracts']['items']:
			print(contract['contractId'][4:])
			enrollment_results = self.wrapper.getEnrollements(contract['contractId'][4:])
			if 'enrollments' in enrollment_results:
				for i in enrollment_results['enrollments']:
					cn = i['csr']['cn']
					sans = i['csr']['sans']
					mustHaveCiphers = i['networkConfiguration']['mustHaveCiphers']
					preferredCiphers = i['networkConfiguration']['preferredCiphers']
					networkType = i['networkConfiguration']['networkType']
					certifcateAuthority = i['ra']
					certificateType = i['certificateType']
					enrollments_list.append([contract['contractId'][4:], cn,sans,mustHaveCiphers, preferredCiphers,networkType, certifcateAuthority, certificateType])
		self.printEnrollments(enrollments_list)

	def printEnrollments (self, enrollments_list):
		"""
		prints the certificate details from the enrollement list from getEnrollments method
		"""
		with open(self.md_path+"certificates.md","w") as mdfile:
			fileWriter = mdfile
			fileWriter.write('''
| Contract Id | Common Name | ALT names | MustHave Ciphers | Preferred Ciphers | Deployment Location | Certifcate Type | Certifcate Authority |
| ----------- | ----------- | --------- | ---------------- | ----------------- | ------------------- | --------------- | -------------------- |
''')	
			if len(enrollments_list) > 1:
				for certs in enrollments_list:
					fileWriter.write('|' + '|'.join( certs ) + "|\n")
			else:
				fileWriter.write("\n__No certificates deployed on Akamai network__\n")

if __name__=="__main__":
	
	a = Aggregator()		
	a.printAccountTable()
	print ("Created the account summary table")
	a.printCPCodes()	
	print ("Created the CP Code summary table")
	a.printEdgeHostNames()
	print ("Created the edge host name summary table")
	print ("Now creating Property summary. It may take a while..")
	a.printPropertiesDetails('productionVersion','stagingVersion', 'latestVersion','firstVersion')
	print ("Property summary complete.")
	a.getEnrollments()
	'''
	print "Now finding host names and origin mapping details for each configuration. This may take a while.."	
	print a.getPropertyHostDetails('grp_63802','ctr_C-1ED34DY', 'prp_370965','4')
	#a.getCNAME('www.macys.com')
	'''
	
