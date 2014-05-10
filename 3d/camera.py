#Python port of http://nehe.gamedev.net/data/lessons/lesson.asp?lesson=10


from OpenGL.GLUT import *        # Module For The GLUT Library
from OpenGL.GL import *        # Module For The OpenGL32 Library
from OpenGL.GLU import *    # Module For The GLu32 Library
import time             # Module for sleeping.
from math import *            # Module for trigonometric functions.
import sys            
import Image            #Image Loading
import array


# The number of our GLUT window
window = None

texture = range(3)       # storage for 3 textures;

light = 0           # lighting on/off
blend = 0        # blending on/off

LightAmbient  = [0.5, 0.5, 0.5, 1.0]
LightDiffuse  = [1.0, 1.0, 1.0, 1.0]
LightPosition = [0.0, 0.0, 2.0, 1.0]

filter = 0       # texture filtering method to use (nearest, linear, linear + mipmaps)


# Image type - contains height, width, and data
class Imaged:
    sizeX = 0
    sizeY = 0
    data = None


def ImageLoad(filename):
    #PIL makes life easy...

    image = Imaged()

    I = Image.open(filename)
    
    image.sizeX = I.size[0]
    image.sizeY = I.size[1]
    image.data = I.convert('RGB').tostring("raw", "RGBX", 0, -1)
    return image


# Load Bitmaps And Convert To Textures
def LoadGLTextures():
    global texture

    # Load Texture
    image1 = ImageLoad( "Data/lesson10/logo.png" )


    # Create Textures
    texture = glGenTextures(3)

    # texture 1 (poor quality scaling)
    glBindTexture(GL_TEXTURE_2D, texture[0])   # 2d texture (x and y size)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)  # cheap scaling when image bigger than texture
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)  # cheap scaling when image smalled than texture

    # 2d texture, level of detail 0 (normal), 3 components (red, green, blue), x size from image, y size from image,
    # border 0 (normal), rgb color data, unsigned byte data, and finally the data itself.
    glTexImage2D(GL_TEXTURE_2D, 0, 4, image1.sizeX, image1.sizeY, 0, GL_RGBA, GL_UNSIGNED_BYTE, image1.data)
    

    # texture 2 (linear scaling)
    glBindTexture(GL_TEXTURE_2D, texture[1])    # 2d texture (x and y size)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)  # scale linearly when image bigger than texture
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)  # scale linearly when image smalled than texture
    glTexImage2D(GL_TEXTURE_2D, 0, 4, image1.sizeX, image1.sizeY, 0, GL_RGBA, GL_UNSIGNED_BYTE, image1.data);
    

    # texture 3 (mipmapped scaling)
    glBindTexture(GL_TEXTURE_2D, texture[2])    # 2d texture (x and y size)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)  # scale linearly when image bigger than texture
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST)  # scale linearly + mipmap when image smalled than texture
    glTexImage2D(GL_TEXTURE_2D, 0, 4, image1.sizeX, image1.sizeY, 0, GL_RGBA, GL_UNSIGNED_BYTE, image1.data)

    # 2d texture, 3 colors, width, height, RGB in that order, byte data, and the data.
    gluBuild2DMipmaps(GL_TEXTURE_2D, 4, image1.sizeX, image1.sizeY, GL_RGBA, GL_UNSIGNED_BYTE, image1.data)

    #return texture
    


# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL(Width, Height):    # We call this right after our OpenGL window is created.

    LoadGLTextures()                           # load the textures.
    glEnable(GL_TEXTURE_2D)                    # Enable texture mapping.

    glBlendFunc(GL_SRC_ALPHA, GL_ONE)          # Set the blending function for translucency (note off at init time)
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                       # type of depth test to do.
    glEnable(GL_DEPTH_TEST)                    # enables depth testing.

    glShadeModel(GL_SMOOTH)            # Enables Smooth Color Shading

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                # Reset The Projection Matrix
    gluPerspective(45.0,Width/Height,0.1,100.0)    # Calculate The Aspect Ratio Of The Window
    glMatrixMode(GL_MODELVIEW)

    # set up lights.
    glLightfv(GL_LIGHT1, GL_AMBIENT, LightAmbient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, LightDiffuse)
    glLightfv(GL_LIGHT1, GL_POSITION, LightPosition)
    glEnable(GL_LIGHT1)


# The function called when our window is resized (which shouldn't happen, because we're fullscreen)
def ReSizeGLScene(Width, Height):

    if (Height==0):                # Prevent A Divide By Zero If The Window Is Too Small
        Height=1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(45.0,float(Width)/float(Height),0.1,100.0)
    glMatrixMode(GL_MODELVIEW)



from world import Cube
cubes = [ Cube(0,0,2), ]


vertices = array.array('f', 
    [     -1,-1,1, 
        -1,1,1, 
        1,1,1, 
        1,-1,1, 
        -1,-1,-1, 
        -1,1,-1,  
        1,1,-1, 
        1,-1,-1 ] )

colors = array.array('f', 
    [     0, 0, 0, .5, 
        1, 0, 0, .5,
        1, 1, 0, .5, 
        0, 1, 0, .5, 
        0, 0, 1, .5, 
        1, 0, 1, .5, 
        1, 1, 1, .5, 
        0, 1, 1, .5,
        ] )

cIndices = array.array('B', 
    [    0, 3, 2, 1,  
        2, 3, 7, 6,  
        0, 4, 7, 3,  
        1, 2, 6, 5,  
        4, 5, 6, 7,  
        0, 1, 5, 4 ] )

"""
textures = array.array('f',
    [
    ])
"""

def init(  ):
    #   Initialize GLUT state - glut will take any command line arguments that pertain to it or
    #   X Windows - look at its documentation at http:reality.sgi.com/mjk/spec3/spec3.html 
    glutInit(sys.argv)

    # ALPHA?
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_ALPHA)
    #glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH )

    # get a 640 x 480 window 
    glutInitWindowSize(800, 600)
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)

    # Open a window 
    window = glutCreateWindow("Foo")



    if not (glColorPointer and glVertexPointer and glDrawElements):
        print ''' Error: no vertex array support'''
        sys.exit( )
    glClearColor ( 0, 0, 0, 0 )
    glEnable(GL_DEPTH_TEST)
    glShadeModel( GL_SMOOTH )

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                # Reset The Projection Matrix
    gluPerspective(60.0,800/600.0,0.1,1000.0)    # Calculate The Aspect Ratio Of The Window
    glMatrixMode(GL_MODELVIEW)

    # set up lights.
    glLightfv(GL_LIGHT1, GL_AMBIENT, LightAmbient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, LightDiffuse)
    glLightfv(GL_LIGHT1, GL_POSITION, LightPosition)
    glEnable(GL_LIGHT1)


class Camera:
    #X is left/right, Y is up/down, Z is fwd/back
    pos = (2,3.5,2)
    sight = (0,0,0) #reset on init by XZangle
    up = (0,1,0)

    XZangle = 0 #rotation in radians in XZ plane
    YZangle = 0 #rot in radians, applied to "up" vector

    v = 0 #vertical speed

    def __init__(self):
        #InitGL(1200,800)
        init()
    
    # The main drawing function.
    def __call__(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)        # Clear The Screen And The Depth Buffer
        glLoadIdentity() #investigate - why do we load every time? it's a clear function?

        self.Aim()
    
        glBindTexture(GL_TEXTURE_2D, texture[filter])    # pick the texture.

        ## magic

        glEnableClientState( GL_COLOR_ARRAY )
        glEnableClientState( GL_VERTEX_ARRAY )

        # so, we want to build up all the arrays into one master list,
        # for minimum opengl calls.  So look in the world for all the 
        # cubes, do some culling

        # imagine two buffers of quads then, visible and invisible?
        # one thread renders and updates visible, another can crank
        # on invisible, doing sims.. or just hit one sim iteration
        # per render cycle

            #
            # which in turns hit one round on an obj, with a timestamp.
            # so on approaching border zones, iterate quickly through sims?
            #
        self.World.gravity()

        for c in self.World.cull( self): 
            c.render()

        glDisableClientState( GL_COLOR_ARRAY )
        glDisableClientState( GL_VERTEX_ARRAY )
        ##


        
        # since this is double buffered, swap the buffers to display what just got drawn.
        glutSwapBuffers()


    def Aim(self):
        #point the camera with LookAt

        """
        if the camera rotates ang degrees in the xz plane, the new lookingat vector
        is:
            lx = sin(ang)
            lz = cos(ang)
        """
        self.sight = ( sin(self.XZangle)+self.pos[0], 
                            sin(self.YZangle)+self.pos[1], 
                            cos(self.XZangle)+self.pos[2]
                            )

        #normalize the vector
        #d = sum( [x**2 for x in self.sight])**.5
        #self.sight= tuple([10*x/d for x in self.sight])

        gluLookAt( *self.pos+self.sight+self.up)

    @property
    def feet(self):
        self.pos = p
        return (p[0],p[1]-2,p[2])
    

