import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Scene:
    def __init__(self):
        self.points = []
        self.rectangles = []
        self.triangles = []

    def clear(self):
        self.points.clear()
        self.rectangles.clear()
        self.triangles.clear()

    def add_point(self, cords, color=(1.0, 1.0, 1.0), size=6.0, label=None, label_color=(1.0, 1.0, 1.0), label_offset=(0.08, 0.08, 0.08)):
        self.points.append({
            "position": (float(cords[0]), float(cords[1]), float(cords[2])),
            "color": normalize_color(color),
            "size": float(size),
            "label": label,
            "label_color": normalize_color(label_color),
            "label_offset": _normalize_offset(label_offset),
        })

    def add_triangle(self, points, color=(1.0, 1.0, 1.0), filled=True, label=None, label_color=(1.0, 1.0, 1.0), label_offset=(0.08, 0.08, 0.08)):
        points = (
            tuple(float(component) for component in points[0]),
            tuple(float(component) for component in points[1]),
            tuple(float(component) for component in points[2]),
        )
        self.triangles.append({
            "points": points,
            "color": normalize_color(color),
            "filled": bool(filled),
            "label": label,
            "label_color": normalize_color(label_color),
            "label_offset": _normalize_offset(label_offset),
        })

    def add_rectangle(self, points, color=(1.0, 1.0, 1.0), filled=False, label=None, label_color=(1.0, 1.0, 1.0), label_offset=(0.08, 0.08, 0.08)):
        points = (
            tuple(float(component) for component in points[0]),
            tuple(float(component) for component in points[1]),
            tuple(float(component) for component in points[2]),
            tuple(float(component) for component in points[3]),
        )
        self.rectangles.append({
            "points": points,
            "color": normalize_color(color),
            "filled": bool(filled),
            "label": label,
            "label_color": normalize_color(label_color),
            "label_offset": _normalize_offset(label_offset),
        })

scene = Scene()

vertices = [
    (1.0, -1.0, -1.0),  # Punkt 0: Vorne unten rechts
    (1.0, 1.0, -1.0),   # Punkt 1: Vorne oben rechts
    (-1.0, 1.0, -1.0),  # Punkt 2: Vorne oben links
    (-1.0, -1.0, -1.0), # Punkt 3: Vorne unten links
    (1.0, -1.0, 1.0),   # Punkt 4: Hinten unten rechts
    (1.0, 1.0, 1.0),    # Punkt 5: Hinten oben rechts
    (-1.0, -1.0, 1.0),  # Punkt 6: Hinten unten links
    (-1.0, 1.0, 1.0)    # Punkt 7: Hinten oben links
]

faces = [
    (
        vertices[0],
        vertices[1],
        vertices[2],
        vertices[3],
    ),
    (
        vertices[4],
        vertices[5],
        vertices[7],
        vertices[6],
    ),
    (
        vertices[0],
        vertices[3],
        vertices[6],
        vertices[4],
    ),
    (
        vertices[0],
        vertices[1],
        vertices[5],
        vertices[4],
    ),
    (
        vertices[1],
        vertices[2],
        vertices[7],
        vertices[5],
    ),
    (
        vertices[2],
        vertices[3],
        vertices[6],
        vertices[7],
    ),
]

def create_objects():
    if not scene.triangles and not scene.rectangles and not scene.points:
        for i, item in enumerate(vertices):
            scene.add_point(item, label=f"V {i}")
        for i, item in enumerate(faces):
            scene.add_rectangle(item, label=f"F {i}")