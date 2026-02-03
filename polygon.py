from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def display():
    # Set window background color (white)
    glClearColor(1.0, 1.0, 1.0, 0.0) 
    # Clear the color buffer
    glClear(GL_COLOR_BUFFER_BIT) 
    
    glBegin(GL_POLYGON) # Start drawing a polygon
    glColor3f(0.2, 0.2, 0.4) # Set polygon color
    glVertex2f(-0.3, 0.3)
    glVertex2f(0.3, 0.3)
    glVertex2f(0.6, 0.0)
    glVertex2f(0.3, -0.3)
    glVertex2f(-0.3, -0.3)
    glVertex2f(-0.6, 0.0)
    glEnd()
    
    glFlush()

def main():
    glutInit() # Initialize GLUT
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(320, 320) # Window size
    glutInitWindowPosition(50, 50) # Window position
    # The title must be a byte string (b"") on some systems
    glutCreateWindow(b"OpenGL Polygon Test") 
    glutDisplayFunc(display) # Set display callback
    glutMainLoop() # Enter the main loop

if __name__ == "__main__":
    main()