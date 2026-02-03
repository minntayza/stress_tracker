from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Function to initialize some settings
def init_graphics():
    # Set the background color to black
    glClearColor(0.0, 0.0, 0.0, 1.0)
    # Set the drawing color to white
    glColor3f(1.0, 1.0, 1.0)
    # Set the viewport to cover the entire window
    glViewport(0, 0, 500, 500)
    
    # Setup a simple 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Define the clipping volume (left, right, bottom, top, near, far)
    # Coordinates will range from -10 to 10 in both X and Y
    gluOrtho2D(-10.0, 10.0, -10.0, 10.0) 
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    # 1. Clear the color buffer (reset the screen)
    glClear(GL_COLOR_BUFFER_BIT)
    
    # 2. Begin drawing a primitive (a triangle)
    glBegin(GL_TRIANGLES)
    
    # Set the color for the vertices (Red)
    glColor3f(1.0, 0.0, 0.0) 
    glVertex2f(0.0, 5.0)    # Top vertex
    
    # Set the color for the vertices (Green)
    glColor3f(0.0, 1.0, 0.0) 
    glVertex2f(-5.0, -5.0)  # Bottom-left vertex
    
    # Set the color for the vertices (Blue)
    glColor3f(0.0, 0.0, 1.0) 
    glVertex2f(5.0, -5.0)   # Bottom-right vertex
    
    glEnd() # End drawing primitive

    # 3. Force execution of GL commands (draw the buffer to the screen)
    glFlush()

# --- Main Program ---
glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Rainbow Triangle")

init_graphics() # Call the setup function

glutDisplayFunc(display)
glutMainLoop()