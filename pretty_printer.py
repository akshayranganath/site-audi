#! /usr/bin/env python
###############
# Author: akshayranganath
# Gihub link: https://github.com/akshayranganath/python_pretty_printer
###############
import json
import argparse

def getFileData(fileName):
	"""
		Open a file, and read the contents. The with..open operation will auto-close the file as well.
	"""
	with open(fileName) as handle:
		data = handle.read()

	return data

def prettyPrint(data, outfile):
	"""
		Pretty print and write the file back to the argument 'outfile'
	"""	
	with open(outfile, "wb") as handle:
		handle.write ( json.dumps(json.loads(data), indent=4, sort_keys=True) )


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Pretty print JSON')
	parser.add_argument('--file', help="JSON file. If no --outfile is provided, this file will be over-written",required=True )
	parser.add_argument('--outfile', help="Output file to pretty print the JSON", required=False )

	args = parser.parse_args()        
	outfile = args.file if args.outfile is None else args.outfile

	jsondata = getFileData(args.file)
	prettyPrint(jsondata, outfile)
	print 'Pretty printer complete.'