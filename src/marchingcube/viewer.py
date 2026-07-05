import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Viewer:
    BITMAP_FONT = (
        globals().get("GLUT_BITMAP_HELVETICA_18")
        or globals().get("GLUT_BITMAP_HELVETICA_12")
        or globals().get("GLUT_BITMAP_8_BY_13")
    )

    DEFAULT_VERTICES = [
        (1.0, -1.0, -1.0),
        (1.0, 1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, 1.0),
    ]

    DEFAULT_EDGES = [
        (DEFAULT_VERTICES[0], DEFAULT_VERTICES[1]),
        (DEFAULT_VERTICES[0], DEFAULT_VERTICES[3]),
        (DEFAULT_VERTICES[0], DEFAULT_VERTICES[4]),
        (DEFAULT_VERTICES[1], DEFAULT_VERTICES[2]),
        (DEFAULT_VERTICES[1], DEFAULT_VERTICES[5]),
        (DEFAULT_VERTICES[2], DEFAULT_VERTICES[3]),
        (DEFAULT_VERTICES[2], DEFAULT_VERTICES[7]),
        (DEFAULT_VERTICES[3], DEFAULT_VERTICES[6]),
        (DEFAULT_VERTICES[4], DEFAULT_VERTICES[5]),
        (DEFAULT_VERTICES[4], DEFAULT_VERTICES[6]),
        (DEFAULT_VERTICES[5], DEFAULT_VERTICES[7]),
        (DEFAULT_VERTICES[6], DEFAULT_VERTICES[7]),
    ]

    DEFAULT_MIDPOINTS = [
        (1.0, 0, -1.0),
        (0, -1.0, -1.0),
        (1.0, -1.0, 0),
        (0, 1.0, -1.0),
        (1.0, 1.0, 0),
        (-1.0, 0, -1.0),
        (-1.0, 1.0, 0),
        (-1.0, -1.0, 0),
        (1.0, 0, 1.0),
        (0, -1.0, 1.0),
        (0, 1.0, 1.0),
        (-1.0, 0, 1.0),
    ]

    DEFAULT_FACES = [
        (
            DEFAULT_VERTICES[0],
            DEFAULT_VERTICES[1],
            DEFAULT_VERTICES[2],
            DEFAULT_VERTICES[3],
        ),
        (
            DEFAULT_VERTICES[4],
            DEFAULT_VERTICES[5],
            DEFAULT_VERTICES[7],
            DEFAULT_VERTICES[6],
        ),
        (
            DEFAULT_VERTICES[0],
            DEFAULT_VERTICES[3],
            DEFAULT_VERTICES[6],
            DEFAULT_VERTICES[4],
        ),
        (
            DEFAULT_VERTICES[0],
            DEFAULT_VERTICES[1],
            DEFAULT_VERTICES[5],
            DEFAULT_VERTICES[4],
        ),
        (
            DEFAULT_VERTICES[1],
            DEFAULT_VERTICES[2],
            DEFAULT_VERTICES[7],
            DEFAULT_VERTICES[5],
        ),
        (
            DEFAULT_VERTICES[2],
            DEFAULT_VERTICES[3],
            DEFAULT_VERTICES[6],
            DEFAULT_VERTICES[7],
        ),
    ]

    def __init__(self):
        self.points = []
        self.lines = []
        self.triangles = []
        self.rectangles = []

        self.camera_angle_x = 45.0
        self.camera_angle_y = 45.0
        self.camera_distance = 6.0

        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_button_pressed = False

    @staticmethod
    def _centroid(points):
        count = float(len(points))
        return (
            sum(point[0] for point in points) / count,
            sum(point[1] for point in points) / count,
            sum(point[2] for point in points) / count,
        )

    @staticmethod
    def _normalize_color(color):
        if color is None:
            return (1.0, 1.0, 1.0)
        if len(color) == 3:
            return tuple(float(component) for component in color)
        if len(color) == 4:
            return tuple(float(component) for component in color[:3])
        raise ValueError("Farbe muss aus 3 oder 4 Werten bestehen.")

    @staticmethod
    def _normalize_offset(offset):
        if offset is None:
            return (0.08, 0.08, 0.08)
        return tuple(float(component) for component in offset)

    def clear(self):
        self.points.clear()
        self.rectangles.clear()
        self.triangles.clear()
        self.lines.clear()

    def _draw_label(self, label, position, color):
        if not label or self.BITMAP_FONT is None:
            return
        glDisable(GL_DEPTH_TEST)
        glColor3fv(color)
        glRasterPos3f(position[0], position[1], position[2])
        for character in str(label):
            glutBitmapCharacter(self.BITMAP_FONT, ord(character))
        glEnable(GL_DEPTH_TEST)

    def draw_scene(self):
        for rectangle in self.rectangles:
            glColor3fv(rectangle["color"])
            if rectangle["filled"]:
                glBegin(GL_QUADS)
            else:
                glBegin(GL_LINE_LOOP)
            for point in rectangle["points"]:
                glVertex3fv(point)
            glEnd()
            self._draw_label(
                rectangle["label"],
                tuple(
                    center + offset
                    for center, offset in zip(
                        self._centroid(rectangle["points"]), rectangle["label_offset"]
                    )
                ),
                rectangle["label_color"],
            )

        for line in self.lines:
            glColor3fv(line["color"])
            glBegin(GL_LINES)
            for point in line["points"]:
                glVertex3fv(point)
            glEnd()
            self._draw_label(
                line["label"],
                tuple(
                    center + offset
                    for center, offset in zip(
                        self._centroid(line["points"]), line["label_offset"]
                    )
                ),
                line["label_color"],
            )

        for triangle in self.triangles:
            glColor3fv(triangle["color"])
            if triangle["filled"]:
                glBegin(GL_TRIANGLES)
            else:
                glBegin(GL_LINE_LOOP)
            for point in triangle["points"]:
                glVertex3fv(point)
            glEnd()
            self._draw_label(
                triangle["label"],
                tuple(
                    center + offset
                    for center, offset in zip(
                        self._centroid(triangle["points"]), triangle["label_offset"]
                    )
                ),
                triangle["label_color"],
            )

        for point in self.points:
            glPointSize(point["size"])
            glColor3fv(point["color"])
            glBegin(GL_POINTS)
            glVertex3fv(point["position"])
            glEnd()
            self._draw_label(
                point["label"],
                tuple(
                    center + offset
                    for center, offset in zip(point["position"], point["label_offset"])
                ),
                point["label_color"],
            )

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        rad_x = math.radians(self.camera_angle_x)
        rad_y = math.radians(self.camera_angle_y)

        cam_x = self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
        cam_y = self.camera_distance * math.sin(rad_x)
        cam_z = self.camera_distance * math.cos(rad_x) * math.cos(rad_y)

        up_y = 1.0 if math.cos(rad_x) >= 0 else -1.0
        gluLookAt(cam_x, cam_y, cam_z, 0.0, 0.0, 0.0, 0.0, up_y, 0.0)

        self.draw_scene()
        glutSwapBuffers()

    def mouse_click(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self.mouse_button_pressed = True
                self.last_mouse_x = x
                self.last_mouse_y = y
            elif state == GLUT_UP:
                self.mouse_button_pressed = False

    def mouse_move(self, x, y):
        if self.mouse_button_pressed:
            delta_x = self.last_mouse_x - x
            delta_y = self.last_mouse_y - y

            self.camera_angle_y += delta_x * 0.5
            self.camera_angle_x += delta_y * 0.5

            if self.camera_angle_x > 89.0:
                self.camera_angle_x = 89.0
            if self.camera_angle_x < -89.0:
                self.camera_angle_x = -89.0

            self.last_mouse_x = x
            self.last_mouse_y = y
            glutPostRedisplay()

    def reshape(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, float(width) / float(height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)


    def run(self, argv=None):
        self._populate_defaults()

        glutInit(argv or sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        glutCreateWindow(b"Scene Viewer: Punkte und Dreiecke")

        glEnable(GL_DEPTH_TEST)

        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutMouseFunc(self.mouse_click)
        glutMotionFunc(self.mouse_move)
        glutMainLoop()


    def find_midpoint(self, edge): #Not needed anymore
        midpoint = []
        for i in range(3):
            delta = edge[0][i] - edge[1][i]
            if delta == 0:
                midpoint.append(edge[0][i])
            else:
                midpoint.append(0)
        return midpoint

    def _general_verticies(self, center=(0,0,0)):
        verticies = []
        for item in self.DEFAULT_VERTICES:
            verticies.append(
                (
                    item[0] + center[0],
                    item[1] + center[1],
                    item[2] + center[2],
                )
            )
        return verticies
    
    def _general_edges(self, verticies):
        return [
            (verticies[0], verticies[1]),
            (verticies[0], verticies[3]),
            (verticies[0], verticies[4]),
            (verticies[1], verticies[2]),
            (verticies[1], verticies[5]),
            (verticies[2], verticies[3]),
            (verticies[2], verticies[7]),
            (verticies[3], verticies[6]),
            (verticies[4], verticies[5]),
            (verticies[4], verticies[6]),
            (verticies[5], verticies[7]),
            (verticies[6], verticies[7]),
        ]


    def general_cube(self, center=(0, 0, 0)):
        ...

    def add_point(
        self,
        cords,
        color=(1.0, 1.0, 1.0),
        size=6.0,
        label=None,
        label_color=(1.0, 1.0, 1.0),
        label_offset=(0.08, 0.08, 0.08),
    ):
        self.points.append(
            {
                "position": (float(cords[0]), float(cords[1]), float(cords[2])),
                "color": self._normalize_color(color),
                "size": float(size),
                "label": label,
                "label_color": self._normalize_color(label_color),
                "label_offset": self._normalize_offset(label_offset),
            }
        )

    def add_line(
        self,
        points,
        color=(1.0, 1.0, 1.0),
        filled=True,
        label=None,
        label_color=(1.0, 1.0, 1.0),
        label_offset=(0.08, 0.08, 0.08),
    ):
        points = (
            tuple(float(component) for component in points[0]),
            tuple(float(component) for component in points[1]),
        )
        self.lines.append(
            {
                "points": points,
                "color": self._normalize_color(color),
                "filled": bool(filled),
                "label": label,
                "label_color": self._normalize_color(label_color),
                "label_offset": self._normalize_offset(label_offset),
            }
        )

    def add_triangle(
        self,
        points,
        color=(1.0, 1.0, 1.0),
        filled=False,
        label=None,
        label_color=(1.0, 1.0, 1.0),
        label_offset=(0.08, 0.08, 0.08),
    ):
        points = (
            tuple(float(component) for component in points[0]),
            tuple(float(component) for component in points[1]),
            tuple(float(component) for component in points[2]),
        )
        self.triangles.append(
            {
                "points": points,
                "color": self._normalize_color(color),
                "filled": bool(filled),
                "label": label,
                "label_color": self._normalize_color(label_color),
                "label_offset": self._normalize_offset(label_offset),
            }
        )

    def add_rectangle(
        self,
        points,
        color=(1.0, 1.0, 1.0),
        filled=False,
        label=None,
        label_color=(1.0, 1.0, 1.0),
        label_offset=(0.08, 0.08, 0.08),
    ):
        points = (
            tuple(float(component) for component in points[0]),
            tuple(float(component) for component in points[1]),
            tuple(float(component) for component in points[2]),
            tuple(float(component) for component in points[3]),
        )
        self.rectangles.append(
            {
                "points": points,
                "color": self._normalize_color(color),
                "filled": bool(filled),
                "label": label,
                "label_color": self._normalize_color(label_color),
                "label_offset": self._normalize_offset(label_offset),
            }
        )

    def _populate_defaults(self, center=(0,0,0)):
        if self.triangles or self.rectangles or self.points or self.lines:
            return
        
        verticies = self._general_verticies(center)
        edges = self._general_edges(verticies)
        midpoints = [self.find_midpoint(edge) for edge in edges]

        for i, item in enumerate(edges):
            self.add_line(item)

        for i, item in enumerate(verticies):
            self.add_point(item)
            """trigPoints = []
            for edge in edges:
                if edge[0] == item or edge[1] == item:
                    self.add_line(edge)
                    trigPoints.append(self.find_midpoint(edge))
            self.add_triangle(trigPoints, color=(1, 0, 1), filled=True, label=f"T on V {i}")"""
        
        self.add_triangle([midpoints[1], midpoints[9], midpoints[8]], color=(1, 0, 0), filled=True, label=f"T 1")
        self.add_triangle([midpoints[1], midpoints[0], midpoints[8]], color=(0, 1, 0), filled=True, label=f"T 2")
        self.add_triangle([midpoints[3], midpoints[5], midpoints[6]], color=(0, 0, 1), filled=True, label=f"T 3")

if __name__ == "__main__":
    Viewer().run()
