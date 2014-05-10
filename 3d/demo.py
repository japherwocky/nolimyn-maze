#Python port of http://nehe.gamedev.net/data/lessons/lesson.asp?lesson=10


from OpenGL.GLUT import *        # Module For The GLUT Library
from OpenGL.GL import *        # Module For The OpenGL32 Library
from OpenGL.GLU import *    # Module For The GLu32 Library
import time             # Module for sleeping.
from math import *            # Module for trigonometric functions.
import sys            

def seedWorld(World):
    from world import Cube
    for x in range(-5,45):
        for z in range(-5,8):
            World.spawnCube( x,-1,z, Cube(x,-1,z))


def main():

    # Initialize our window. 
    from camera import Camera
    Camera = Camera()
    DrawGLScene = Camera

    from world import World
    World = World(Camera)
    Camera.World = World
    seedWorld( World)

    World.objects.add( Camera)

    glutDisplayFunc(DrawGLScene) #initial draw, after alt-tab, etc.
    #glutFullScreen()
    # Even if there are no events, redraw our gl scene. 
    glutIdleFunc(DrawGLScene)


    # Register the function called when our window is resized. 
    from camera import ReSizeGLScene
    glutReshapeFunc(ReSizeGLScene)


    ### INPUT HANDLING
    from inputhandler import Keymap
    K = Keymap()
    K.Camera = Camera

    # Register the function called when the keyboard is pressed. 
    glutKeyboardFunc( K.keydown)
    glutKeyboardUpFunc( K.keyup)
    # Register the function called when special keys (arrows, page down, etc) are pressed.
    glutSpecialFunc( K.keydown)
    glutSpecialUpFunc( K.keyup)

    glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF)

    glutPassiveMotionFunc( K.mousemove)
    glutMotionFunc( K.mousemove) #called when "dragging"

    glutSetCursor( GLUT_CURSOR_NONE)


    def tick(x):
        #proc keypresses
        K.prockeys()

        #load the next TimerFunc
        glutTimerFunc( 50, tick, x+1)

    glutTimerFunc( 1000, tick, 5)


    # Start Event Processing Engine 
    glutMainLoop()

if __name__=="__main__":
    main()

