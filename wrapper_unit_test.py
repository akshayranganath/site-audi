# Sample unit test scripts

import unittest
from wrapper import Wrapper

class WrapperUnitTest(unittest.TestCase):
	
	def setUp(self):
		pass

	def test_wrapper_getGroups(self):			
		self.assertNotEqual(Wrapper().getGroups(),{})		

	def test_wrapper_getContractNames(self):	
		self.assertNotEqual(Wrapper().getContractNames(),{})	

	def test_wrapper_checkIfCdnIP(self):
		w = Wrapper()
		self.assertFalse( w.checkIfCdnIP( w.getIpAddress('www.example.com') ) )

	def tearDown(self):		
		pass

if __name__ == "__main__":
	unittest.main()		