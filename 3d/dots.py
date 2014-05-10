#include <GL/gl.h>
#include <GL/glut.h>

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from random import random

def display ():

	#/* clear window */
	glClear(GL_COLOR_BUFFER_BIT)

	#/* future matrix manipulations should affect the modelview matrix */
	glMatrixMode(GL_MODELVIEW)

	#/* draw scene */
	glBegin(GL_POINTS)
	glColor4f( random(),1,1,.1) #set the current color

	for i in range( 10000):
		glVertex3f( random()*5, random()*5, random())
	glEnd()

	#/* flush drawing routines to the window */
	#glFlush()

	glutSwapBuffers()




def reshape ( width, height):
	""" triggered on window resizing """
	#/* define the viewport transformation */
	glViewport(0,0,width,height)

import sys
def keyboard( key, x, y):
	if key==27 or key=='\x1b': sys.exit(0)


def main():

	glutInit()

	#/* setup the size, position, and display mode for new windows */
	glutInitWindowSize(500,500)
	glutInitWindowPosition(0,0)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)

	C = Camera()

	#/* create and set up a window */
	glutCreateWindow("hello, teapot!")
	glutDisplayFunc(display)
	glutIdleFunc( display)
	glutReshapeFunc(reshape)
	glutKeyboardFunc( C.input)
	glutSpecialFunc( C.input)
	#glutSpecialFunc( keyboard) #grabs function keys, etc.

	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA,GL_ONE)

	C.setprojection()
	C.setview()

	#/* tell GLUT to wait for events */
	glutMainLoop()


from math import sin, cos
class Camera:
	eye = (1,1,1)
	center = (0,0,0)
	up = (0,1,0)
	sightvector = [0,0,0]
	angle = 0

	def setprojection(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()	
		glOrtho(-5.0,10.0,-5.0,10.0,-4.0,4.0)
		gluPerspective(80,1,2,13)
		glFrustum(-1.0,1.0,-1.0,1.0,.5,12.0)

	def setview(self):
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt( *(self.eye+self.center+self.up) )


	def orientMe(self, ang):

		lx = sin(ang)
		lz = -cos(ang)

		self.sightvector[0] = sin(ang)
		self.sightvector[2] = -cos(ang)

		#self.center = (self.center[0]+self.eye[0], self.center[1]+self.eye[1], self.center[2]+self.center[2])

		self.setview()

	def moveMeFlat(self, direction):
			
		eyex = self.eye[0] + (direction*(self.sightvector[0])*0.1)
		eyez = self.eye[2] + (direction*(self.sightvector[2])*0.1)

		self.eye = (eyex, self.eye[1], eyez)

		self.setview()

	def input(self, key, x, y):
		print '---'
		print self.center
		print self.eye
		print self.up
		print self.sightvector

		if key == GLUT_KEY_LEFT:
			self.angle -= .01
			self.orientMe( self.angle)
		elif key == GLUT_KEY_RIGHT:
			self.angle += .01
			self.orientMe( self.angle)
		elif key == GLUT_KEY_UP:
			self.moveMeFlat( 1)
		elif key == GLUT_KEY_DOWN:
			self.moveMeFlat( -1)

		else: keyboard( key,x,y)


if __name__=='__main__': main()


