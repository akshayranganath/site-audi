import json 

class Origin_Settings:
	"""
	Class that recursively finds and prints origin names
	"""
	
	def __init__(self):
		"""
		Initialize an empty array to hold the names of the origins
		"""
		self.origins=[]		

	def findOrigin(self,rule):
		for behavior in rule['behaviors']:
			if behavior['name']=="origin":			
				origin_type = behavior['options']['originType']
				if origin_type=='CUSTOMER':
					origin_hostname = behavior['options']['hostname']				
				else:
					origin_hostname = behavior['options']['netStorage']['downloadDomainName']
				self.origins.append( {"originType": origin_type, "hostname": origin_hostname} )


	def findChildren(self,rules):		
		if rules['children']:
			for child in rules['children']:				
				#keep looping for each child				
				self.findChildren(child)
				#when complete, check if origin is present
				self.findOrigin(child)	
		
	def getOrigins(self, format="json"):
		print json.dumps(self.origins)
		return self.origins

	def findOrigins(self, rules):
		self.findOrigin(rules['rules'])
		self.findChildren(rules['rules'])
		return self.origins

if __name__=="__main__":
	f = open('rules.js')
	rules = json.loads(f.read())
	o = Origin_Settings()
	o.findOrigin(rules['rules'])
	o.findChildren(rules['rules'])
	o.getOrigins()