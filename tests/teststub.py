import unittest

class TestStub(unittest.TestCase):
	"""
	What it is
	"""
	def setUp(self):
		pass
	def tearDown(self):
		pass

	def testDefaults(self):
		#silly sanity check
		self.assert_( True)


if __name__=='__main__': unittest.main()

