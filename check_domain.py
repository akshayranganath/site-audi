#!/usr/env python
import csv
from wrapper import Wrapper

hostDetails = []
with open('/Users/akrangan/Projects/idea/devops/site-audit/Advanced_Solutions_Services-1500070496/hostnames.csv','rb') as csvFile:
	csvDetails = csv.reader(csvFile)
	for hostDetail in csvDetails:
		hostDetails.append(hostDetail)



with open('/Users/akrangan/Projects/idea/devops/site-audit/Advanced_Solutions_Services-1500070496/hostnames.csv','wb') as csvFile:
	hostDetailsFile = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	header = True
	try:
		wrapper = Wrapper()
	except argparse.ArgumentError:
		pass

	for hostDetail in hostDetails:
		if header == True:
			header = False
			hostDetailsFile.writerow(hostDetail)				
		else:					
			print hostDetail[3], wrapper.getIpAddress(hostDetail[3])
			hostDetail[7] = wrapper.checkIfCdnIP( wrapper.getIpAddress(hostDetail[3]) )
			hostDetailsFile.writerow(hostDetail)

