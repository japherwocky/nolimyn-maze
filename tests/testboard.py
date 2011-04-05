import unittest

class TestBoard(unittest.TestCase):
	"""
	What it is
	"""
	def setUp(self):
		import board
		self.B = board.Board( 13)
		pass

	def tearDown(self):
		pass

	def testRenders(self):
		#silly sanity check
		self.assert_( True)

		from board import Body

		FooBody = Body()
		self.B.spawn( FooBody)

		self.assert_( self.B.renderViewAscii( FooBody) )

		self.assert_( self.B.renderViewHtml( FooBody)  )



if __name__=='__main__': unittest.main()

