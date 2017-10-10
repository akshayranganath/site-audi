#!/usr/env/python
import csv
import json

def openPropertiesFile(fileName):
	propertyCpCodes = {}
	with open(fileName, "rb") as csvfile:
		properties = csv.reader(csvfile)
		for pmProperty in properties:
			for cpcode in pmProperty[17].split(','):
				try:
					propertyCpCodes[int(cpcode)] = {
						'propertyName' : pmProperty[0],
						'propertyProduct' : pmProperty[4]
						}			
				except ValueError:
					pass

	return propertyCpCodes

def openCpCodeFile(fileName):
	cpcodes = {}
	with open(fileName, "rb") as csvfile:
		cpCodes = csv.reader(csvfile)
		for cpCode in cpCodes:					
			try:
				cpcodes[ int(cpCode[2]) ] = cpCode[4].split('|')				
			except ValueError:
					pass
	return cpcodes


def compareProducts(cpcodes, propertyCpCodes): 
	for cpcode in propertyCpCodes:
		if cpcode in cpcodes:
			if propertyCpCodes[cpcode]['propertyProduct'] not in cpcodes[cpcode]:
				print cpcode,propertyCpCodes[cpcode]['propertyName'], propertyCpCodes[cpcode]['propertyProduct'], cpcodes[cpcode][0]

def findCpCodeMisMatch(cpcodeFile, propertyFile):
	cpcodes =  openCpCodeFile(cpcodeFile)

	propertyCpCodes =  openPropertiesFile(propertyFile)
	
	compareProducts(cpcodes,propertyCpCodes)

if __name__ == "__main__":
	findCpCodeMisMatch('/Users/akrangan/Projects/idea/devops/site-audit/Live_Nation-1500400113/cpcodes.csv','/Users/akrangan/Projects/idea/devops/site-audit/Live_Nation-1500400113/properties.csv')
