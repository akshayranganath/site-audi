from wrapper import Wrapper
import json
import csv, pprint
from time import gmtime, strftime
import subprocess
from origin_settings import Origin_Settings 
import os
import time


class MisMatchFinder:

	def __init__(self):
		self.wrapper = Wrapper()

	def getGroups(self):
		self.groups = self.wrapper.getGroups()

	def getContracts(self):		
		self.contracts = self.wrapper.getContractNames()		

	def getProperties(self):
		for group in self.groups['groups']['items']:
			groupId = group['groupId']
			if 'contractIds' in group:				
				for contractId in group['contractIds']:
					location_result = self.wrapper.getProperties(groupId, contractId)
					if 'properties' in location_result:					
						for config_details in location_result['properties']['items']:
							# Assign values to variables here for readability and will be used in rest of function.  
							propertyName = config_details['propertyName']
							groupId = config_details['groupId']
							contractId = config_details['contractId']
							propertyId = config_details['propertyId']
							productionVersion = config_details['productionVersion']
							stgVersion = config_details['stagingVersion']
							latestVersion = config_details['latestVersion']
							firstVersion = 1
							productId = None

							
							property_details = self.wrapper.getPropertyVersions(propertyId,groupId,contractId)										
							#print json.dumps(property_details)
							productId = property_details['versions']['items'][0]['productId'][4:]
							origin_settings = Origin_Settings()							
							rules = self.wrapper.getConfigRuleTree(propertyId,str(latestVersion), groupId,contractId)
							cpcodes = origin_settings.findOrigins(rules, 'cpCode')
							for cpcode in cpcodes:
								if cpcode['products'] != None:
									if cpcode['products'].find(productId) < 0:
										print propertyName, productId, cpcode['id'], cpcode['products']

if __name__=="__main__":
	m = MisMatchFinder()
	m.getGroups()
	m.getContracts()
	m.getProperties()