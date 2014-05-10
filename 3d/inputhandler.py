#Python port of http://nehe.gamedev.net/data/lessons/lesson.asp?lesson=10


from OpenGL.GLUT import *        # Module For The GLUT Library
from OpenGL.GL import *        # Module For The OpenGL32 Library
from OpenGL.GLU import *    # Module For The GLu32 Library
import time             # Module for sleeping.
from math import *            # Module for trigonometric functions.
import sys            
import Image            #Image Loading

# ascii codes for various special keys
ESCAPE = 27
PAGE_UP = 73
PAGE_DOWN = 81
UP_ARROW = 72
DOWN_ARROW = 80
LEFT_ARROW = 75
RIGHT_ARROW = 77

ESCAPE = '\x1b'
LEFT_ARROW = 100
RIGHT_ARROW = 102

light = 0           # lighting on/off
blend = 0        # blending on/off

xrot = 0            # x rotation
yrot = 0            # y rotation
xspeed = 0          # x rotation speed
yspeed = 0          # y rotation speed

walkbias = 0
walkbiasangle = 0

lookupdown = 0.0
piover180 = 0.0174532925


filter = 0       # texture filtering method to use (nearest, linear, linear + mipmaps)

class Keymap:

    #gets self.Camera on init

    keyboard = set()

    #mouse coords
    lastx = 0
    lasty = 0

    specialkeys = set(
        [
        GLUT_KEY_PAGE_UP, 
        GLUT_KEY_PAGE_DOWN,
        GLUT_KEY_UP,
        GLUT_KEY_DOWN,
        GLUT_KEY_LEFT,
        GLUT_KEY_RIGHT,
        ])

    windowcenter = (glutGet(GLUT_WINDOW_WIDTH) >> 1, glutGet(GLUT_WINDOW_HEIGHT) >> 1)

    jump = 0

    def keydown(self, key, x, y):
        self.keyboard.add( key)

        """
        if key in self.specialkeys:
            specialKeyPressed(key, x, y)
        else:
            keyPressed( key, x, y)
            #self.prockeys( key, x, y)
        """


    def keyup(self, key, x, y):
        self.keyboard.remove(key)

        if key == ' ': 
            Vpos = self.Camera.pos
            self.Camera.v = self.jump
            self.jump = 0

    def prockeys(self):
        Vpos = self.Camera.pos
        Vsight = self.Camera.sight
        XZangle = self.Camera.XZangle

        for key in self.keyboard:
            if key == '\x1b': sys.exit()
    
            if key == 100: #rotate left
                XZangle += .1
                if XZangle < 0: XZangle += 2*pi

            elif key == 102: #rotate right
                XZangle -= .1

            elif key == 101 or key == 'w': #forward
                ang = self.Camera.XZangle
                speed = 1
                Vpos = (Vpos[0]+(speed*sin(ang)), Vpos[1], Vpos[2]+(speed*cos(ang)))    

            elif key == 103 or key == 's': #backward
                ang = self.Camera.XZangle + pi
                speed = 1
                Vpos = (Vpos[0]+(speed*sin(ang)), Vpos[1], Vpos[2]+(speed*cos(ang)))    

            elif key == 'a': #strafe left
                ang = self.Camera.XZangle + (.5*pi)
                speed = 1
                Vpos = (Vpos[0]+(speed*sin(ang)), Vpos[1], Vpos[2]+(speed*cos(ang)))    

            elif key == 'd': #strafe left
                ang = self.Camera.XZangle + (1.5*pi)
                speed = 1
                Vpos = (Vpos[0]+(speed*sin(ang)), Vpos[1], Vpos[2]+(speed*cos(ang)))    

            elif key == ' ':
                self.jump += .1
            else: print key



        self.Camera.pos = Vpos
        self.Camera.XZangle = XZangle

        self.resetcursor()

        if self.keyboard:
            pass
            #print 'pos:%s  sight:%s XZAngle:%s'%(Vpos, Vsight,XZangle)

    def mousemove(self, x, y):

        self.Camera.XZangle -= ( .001 * (x-self.windowcenter[0] ))
        self.Camera.YZangle -= ( .001 * (y-self.windowcenter[1] ))


    def resetcursor(self):
        glutWarpPointer( *self.windowcenter)
        pass
        
            
        
#arcballs for mouse support:
#http://rainwarrior.thenoos.net/dragon/arcball.html    
            
            


# The function called whenever a normal key is pressed.
def keyPressed(key, x, y):
    global blend, filter, light
    
    if ord(key) == ESCAPE: sys.exit()

    if key == 'B' or key == 'b': # switch the blending
        print("B/b pressed; blending is: %d\n"%(blend))
        blend = 0 if blend else 1 #toggle blend value
        
        if (blend):
            glEnable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)
        else:
            glDisable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
    

    elif key =='F' or key == 'f': # switch the filter
        print("F/f pressed; filter is: %d\n"%(filter))
        filter+=1                           # switch the current value of filter, between 0/1/2;
        if (filter > 2):
            filter = 0
    
        print("Filter is now: %d\n"%(filter))

    elif key == 'L' or key == 'l': # switch the lighting
        print("L/l pressed; lighting is: %d\n"% (light))
        if light:        # switch the current value of light, between 0 and 1.
            light = 0
        else:
            light = 1
        
        if (light):
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
    
        print("Lighting is now: %d\n"%(light))

    else:
        print("Key %d pressed. No action there yet.\n"%(ord(key)))
    


def specialKeyPressed(key, x, y):
    global lookupdown, walkbiasangle, walkbias, yrot, xpos, zpos, z

    # avoid thrashing this procedure
    #time.sleep(0.1)

    if key == GLUT_KEY_PAGE_UP: # tilt up
        z -= 0.2
        lookupdown -= 0.2

    elif key == GLUT_KEY_PAGE_DOWN: # tilt down
        z += 0.2
        lookupdown += 1.0

    elif key == GLUT_KEY_UP: # walk forward (bob head)
        xpos -= sin(yrot*piover180) * 0.05
        zpos -= cos(yrot*piover180) * 0.05
        if (walkbiasangle >= 359.0):
            walkbiasangle = 0.0
        else:
            walkbiasangle+= 10

        walkbias = sin(walkbiasangle * piover180)/20.0

    elif key ==GLUT_KEY_DOWN: # walk back (bob head)
        xpos += sin(yrot*piover180) * 0.05
        zpos += cos(yrot*piover180) * 0.05
        if (walkbiasangle <= 1.0):
            walkbiasangle = 359.0
        else:
            walkbiasangle-= 10
        walkbias = sin(walkbiasangle * piover180)/20.0


    elif key == GLUT_KEY_LEFT: # look left
        yrot += 1.5

    elif key == GLUT_KEY_RIGHT: # look right
        yrot -= 1.5

    else:
        print("Special key %d pressed. No action there yet.\n"%(key))
    


