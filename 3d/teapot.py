#include <GL/gl.h>
#include <GL/glut.h>

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def display ():

	#/* clear window */
	glClear(GL_COLOR_BUFFER_BIT)

	#/* future matrix manipulations should affect the modelview matrix */
	glMatrixMode(GL_MODELVIEW)

	#/* draw scene */
	#glutWireTeapot(.5)
	glutWireDodecahedron()

	#/* flush drawing routines to the window */
	glFlush()


def reshape ( width, height):

	#/* define the viewport transformation */
	glViewport(0,0,width,height)


def main():

	glutInit()

	#/* setup the size, position, and display mode for new windows */
	glutInitWindowSize(750,500)
	glutInitWindowPosition(0,0)
	glutInitDisplayMode(GLUT_RGB)

	#/* create and set up a window */
	glutCreateWindow("hello, teapot!")
	glutDisplayFunc(display)
	glutReshapeFunc(reshape)

	#/* define the projection transformation */
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	#glOrtho(-2.0,2.0,-2.0,2.0,-4.0,4.0)
	#gluPerspective(80,1,2,13)
	glFrustum(-1.0,1.0,-1.0,1.0,.5,12.0)

	#/* define the viewing transformation */
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	#eye x/y/z, center x/y/z, up x/y/z
	gluLookAt(3.0,3.0,3.0,0.0,0.0,0.0,0.0,1.0,0.0)

	#/* tell GLUT to wait for events */
	glutMainLoop()

if __name__=='__main__': main()
