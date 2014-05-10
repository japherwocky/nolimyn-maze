import sys											
import pygame									 
from random				import choice 
from pygame.locals import *			 # Imports the constant symbols from 
																	#	 pygame.locals - like OPENGL, K_1, etc...
from OpenGL.GL		 import *			 # This is so we can just do glXXXX() 
																	#	 instead of OpenGL.GL.glXXXXX()

from OpenGL.GLUT import glutWireDodecahedron as glutdodec
from OpenGL.GLUT import *

# Colors for the inner rectangle
square1 = { 'colors': [[1,0,0,1],[0,1,0,1],[0,0,1,1],[1,1,1,1]],
				'vertices': [[-64,-64],[64,-64],[64,64],[-64,64]],
				'rot':0,
				'direction':0,
				'location':(500,200,0),
				}

# Texture coordinates for the outer rectangle
square2 = { 'TexCoords': [[0,0],[1,0],[1,1],[0,1]],
				'location':(150,150,0),
				'colors': [ [.2,0,0,.2], [0,.2,0,.2], [0,0,.2,.2], [.2,.2,.2,.2]],
				'vertices': [[-128,-128],[128,-128],[128,128],[-128,128]],
				'rot':0,
				'direction':0,
				}

def drawsquare( square):

	#Selecting and saving the MODELVIEW matrix.
	glMatrixMode(GL_MODELVIEW)	
	glPushMatrix()							

	glTranslatef( *square['location'])		         # Translate 200 units to the right and back
	glRotatef(square['rot'],0,0,1)		# Rotate square2 around (200,200,1)
	square['rot']=(square['rot']+square['direction'])%360	# Update square2['rot'] value

	# Tell OpenGL that we will use color and vertex arrays
	glEnableClientState(GL_COLOR_ARRAY)			 
	glColorPointerf(square['colors']) #color rgba array

	glEnableClientState(GL_VERTEX_ARRAY)	#We load the VERTEX_ARRAY with our vertices
	glVertexPointerf(square['vertices'])				 
	glBegin(GL_QUADS)								#Then construct a QUAD	
	[glArrayElement(i) for i in range(4)] 	#feeding it points from VERTEX ARRAY
	glEnd()

	glPopMatrix() 					# Restore the MODELVIEW matrix

def drawdodec():

	glutdodec()

def glutmain():
	glutInit()
	glutInitWindowSize(500,500);
	glutInitWindowPosition(0,0);
	glutInitDisplayMode(GLUT_RGB);

	glutCreateWindow("hello, teapot!");

	def display ():

		glClear(GL_COLOR_BUFFER_BIT)
		glutSolidTeapot(.5)
		drawsquare( square1)

		glFlush()

	glutDisplayFunc(draw)

	glutMainLoop();

def draw ():
	glClearColor(0.0,0.0,0.0,0.0)
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

	global square1,square2

	"""
	drawsquare( square1)
	drawsquare( square2)
	"""

	drawdodec()

	glFlush()						# Flush everything to screen ASAP
	pygame.display.flip()		# Flip the double-buffer


def main():
	pygame.init()	# kickstart pygame
	# we want a 700x700, SDL surface that supports doublebuffered OpenGL
	pygame.display.set_mode((700,700),OPENGL|DOUBLEBUF)
	#set up clipping planes / zoom
	glOrtho (0,700,0,700,-1,1)

	while 1:
		event=pygame.event.poll ()
	
		if event.type is QUIT:
			sys.exit(0)
	
		draw()
	
		if event.type is KEYDOWN:
			if event.key is K_ESCAPE:
				sys.exit(0)
			if event.key is K_1:
				square1['direction']+=2
			if event.key is K_2:
				square1['direction']+=-2
			if event.key is K_3:
				square1['direction']= square1['direction'] / 2

if __name__=="__main__": glutmain()



def mkTexture():
	"""
	We can ignore this for now - sets up the other square for a texture
	"""

	# create the partially transparent texture
	# pixel format is: \xRR\xGG\xBB\xAA Red,Green,Blue,Alpha
	tex=""
	for i in xrange(512):
		tex+="\xff\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\x7f"
		tex+="\xff\xff\xff\x3f\xff\xff\xff\x3f\xff\xff\xff\x3f\xff\xff\xff\x3f"
	
	glTexImage2D(GL_TEXTURE_2D,0,4,64,64,0,GL_RGBA,GL_UNSIGNED_BYTE,tex)
	
	# Clamp our texture
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP)				
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP)				
	
	# Magnification / Minification filters are linear
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)	 
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)	 
	
	# Texture will not be affected by current color state
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)			 
	glDisable(GL_DEPTH_TEST)				# No depth testing
	
	glMatrixMode(GL_PROJECTION) 			# Select GL_PROJECTION matrix
	glLoadIdentity()							# Reset GL_PROJECTION matrix

	
