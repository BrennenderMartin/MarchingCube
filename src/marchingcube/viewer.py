import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

BITMAP_FONT = globals().get("GLUT_BITMAP_HELVETICA_18") or globals().get("GLUT_BITMAP_HELVETICA_12") or globals().get("GLUT_BITMAP_8_BY_13")

# ==============================================================================
# 1. SZENE-DATEN UND HELFER
# ==============================================================================


def normalize_color(color):
    if color is None:
        return (1.0, 1.0, 1.0)
    if len(color) == 3:
        return tuple(float(component) for component in color)
    if len(color) == 4:
        return tuple(float(component) for component in color[:3])
    raise ValueError("Farbe muss aus 3 oder 4 Werten bestehen.")


def _normalize_offset(offset):
    if offset is None:
        return (0.08, 0.08, 0.08)
    return tuple(float(component) for component in offset)


def _centroid(points):
    count = float(len(points))
    return (
        sum(point[0] for point in points) / count,
        sum(point[1] for point in points) / count,
        sum(point[2] for point in points) / count,
    )

# ==============================================================================
# 2. GLOBALER KAMERA- UND MAUS-ZUSTAND
# ==============================================================================

camera_angle_x = 45.0  # Vertikaler Neigungswinkel der Kamera (Blick von oben/unten)
camera_angle_y = 45.0  # Horizontaler Drehwinkel der Kamera (Kreisen um das Objekt)
camera_distance = 6.0  # Abstand der Kamera vom Mittelpunkt (Radius der Umlaufbahn)

last_mouse_x = 0       # Speichert die letzte bekannte X-Pixelposition der Maus
last_mouse_y = 0       # Speichert die letzte bekannte Y-Pixelposition der Maus
mouse_button_pressed = False  # Trackt, ob die linke Maustaste gerade gehalten wird

# ==============================================================================
# 3. RENDERING-FUNKTIONEN
# ==============================================================================

def draw_scene():
    """Zeichnet alle per Methode registrierten Punkte und Dreiecke."""

    def draw_label(label, position, color):
        if not label or BITMAP_FONT is None:
            return
        glDisable(GL_DEPTH_TEST)
        glColor3fv(color)
        glRasterPos3f(position[0], position[1], position[2])
        for character in str(label):
            glutBitmapCharacter(BITMAP_FONT, ord(character))
        glEnable(GL_DEPTH_TEST)

    for rectangle in scene.rectangles:
        glColor3fv(rectangle["color"])
        if rectangle["filled"]:
            glBegin(GL_QUADS)
        else:
            glBegin(GL_LINE_LOOP)
        for point in rectangle["points"]:
            glVertex3fv(point)
        glEnd()
        draw_label(rectangle["label"], tuple(center + offset for center, offset in zip(_centroid(rectangle["points"]), rectangle["label_offset"])), rectangle["label_color"])

    for triangle in scene.triangles:
        glColor3fv(triangle["color"])
        if triangle["filled"]:
            glBegin(GL_TRIANGLES)
        else:
            glBegin(GL_LINE_LOOP)
        for point in triangle["points"]:
            glVertex3fv(point)
        glEnd()
        draw_label(triangle["label"], tuple(center + offset for center, offset in zip(_centroid(triangle["points"]), triangle["label_offset"])), triangle["label_color"])

    for point in scene.points:
        glPointSize(point["size"])
        glColor3fv(point["color"])
        glBegin(GL_POINTS)
        glVertex3fv(point["position"])
        glEnd()
        draw_label(point["label"], tuple(center + offset for center, offset in zip(point["position"], point["label_offset"])), point["label_color"])


def display():
    """Haupt-Rendering-Funktion. Wird von GLUT aufgerufen, wenn das Bild neu gezeichnet werden muss."""
    global camera_angle_x, camera_angle_y, camera_distance
    
    # Löscht den Farbpuffer (Hintergrund) und den Tiefenpuffer (3D-Ebenen-Gedächtnis)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Setzt die aktuelle Modell- und Kamera-Matrix auf den Standardwert zurück
    glLoadIdentity()
    
    # --- Schritt C: Berechnung der 3D-Kamera-Position aus Winkeln (Kugelkoordinaten) ---
    # Die mathematischen Funktionen sin() und cos() benötigen Winkel im Bogenmaß (Radiant)
    rad_x = math.radians(camera_angle_x)
    rad_y = math.radians(camera_angle_y)
    
    # Berechnung der X, Y, Z Position der Kamera auf einer unsichtbaren Kugeloberfläche
    cam_x = camera_distance * math.cos(rad_x) * math.sin(rad_y)
    cam_y = camera_distance * math.sin(rad_x)
    cam_z = camera_distance * math.cos(rad_x) * math.cos(rad_y)
    
    # Verhindert, dass die Kamera-Ausrichtung invertiert, wenn man über den Nord-/Südpol schaut
    up_y = 1.0 if math.cos(rad_x) >= 0 else -1.0
    
    # Platziert und richtet die virtuelle Kamera aus:
    # Parameter 1-3: Wo befindet sich die Kamera im Raum? (cam_x, cam_y, cam_z)
    # Parameter 4-6: Worauf blickt die Kamera? (Mittelpunkt des Würfels: 0.0, 0.0, 0.0)
    # Parameter 7-9: Wo ist bei der Kamera 'Oben'? (Standardmäßig die positive Y-Achse)
    gluLookAt(cam_x, cam_y, cam_z, 0.0, 0.0, 0.0, 0.0, up_y, 0.0)
    
    # Ruft unsere Szene auf, um alle registrierten Primitive darzustellen
    draw_scene()
    
    # Tauscht den unsichtbaren Hintergrund-Puffer mit dem sichtbaren Vordergrund-Puffer.
    # Dies verhindert störendes Bildschirmflackern beim Bildaufbau (Double Buffering).
    glutSwapBuffers()

# ==============================================================================
# 4. MAUS-INTERAKTION (INTERACTIVITY)
# ==============================================================================

def mouse_click(button, state, x, y):
    """Wird aufgerufen, sobald eine Maustaste gedrückt oder losgelassen wird."""
    global last_mouse_x, last_mouse_y, mouse_button_pressed
    
    # Prüfen, ob die Aktion von der linken Maustaste stammt
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            # Taste gedrückt: Maus-Tracking aktivieren und Start-Pixelposition sichern
            mouse_button_pressed = True
            last_mouse_x = x
            last_mouse_y = y
        elif state == GLUT_UP:
            # Taste losgelassen: Tracking deaktivieren
            mouse_button_pressed = False


def mouse_move(x, y):
    """Wird aufgerufen, wenn sich die Maus bewegt, während eine Taste gedrückt ist."""
    global last_mouse_x, last_mouse_y, camera_angle_x, camera_angle_y
    
    if mouse_button_pressed:
        # Ermittelt den Pixel-Abstand zwischen der vorherigen und der neuen Mausposition.
        # Reihenfolge 'last - aktuell' sorgt für die intuitive, nicht-invertierte Steuerung.
        delta_x = last_mouse_x - x
        delta_y = last_mouse_y - y
        
        # Rechnet die Pixelbewegung in Grad-Winkel um (0.5 steuert die Empfindlichkeit)
        camera_angle_y += delta_x * 0.5
        camera_angle_x += delta_y * 0.5
        
        # Begrenzt den vertikalen Winkel auf knapp unter 90 Grad.
        # Dies verhindert ein "Umkippen" oder mathematische Fehler direkt am Nord-/Südpol.
        if camera_angle_x > 89.0: camera_angle_x = 89.0
        if camera_angle_x < -89.0: camera_angle_x = -89.0
        
        # Aktualisiert die Koordinaten, damit die Bewegung im nächsten Frame flüssig anknüpft
        last_mouse_x = x
        last_mouse_y = y
        
        # Teilt GLUT mit, dass sich Daten geändert haben und das Fenster neu gerendert werden muss
        glutPostRedisplay()

# ==============================================================================
# 5. FENSTER- UND SYSTEMVERWALTUNG
# ==============================================================================

def reshape(width, height):
    """Wird aufgerufen, wenn das Fenster geöffnet oder in der Größe verändert wird."""
    # Verhindert eine Division durch Null, falls das Fenster extrem minimiert wird
    if height == 0: height = 1
    
    # Setzt den Viewport (Anzeigebereich) auf die kompletten neuen Fenstermaße
    glViewport(0, 0, width, height)
    
    # Wechselt in den Projektionsmodus, um die Kameralinse (Perspektive) zu definieren
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Richtet das Sichtfeld ein:
    # Parameter: 45 Grad vertikaler Blickwinkel, Seitenverhältnis des Fensters,
    # nahe Abschneidegrenze (0.1), ferne Abschneidegrenze (50.0 Einheiten)
    gluPerspective(45, float(width) / float(height), 0.1, 50.0)
    
    # Wechselt zurück in den Modellansichtsmodus für alle kommenden Objekt-Zeichnungen
    glMatrixMode(GL_MODELVIEW)


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

"""
Edges:
0 mit 1,3,4
1 mit 2,5
2 mit 3,7
3 mit 6
4 mit 5,6
5 mit 7
6 mit 7
7 mit -
"""

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

def main():
    """Hauptprogramm: Initialisiert GLUT und startet das Fenster."""
    if not scene.triangles and not scene.rectangles and not scene.points:
        for i, item in enumerate(vertices):
            scene.add_point(item, label=f"V {i}")
        for i, item in enumerate(faces):
            scene.add_rectangle(item, label=f"F {i}")

    # Übergibt System-Argumente an GLUT
    glutInit(sys.argv)
    
    # Konfiguriert das Anzeige-Verfahren:
    # GLUT_DOUBLE: Nutzt Double Buffering gegen Flackern.
    # GLUT_RGB: Aktiviert Standard-Farbmodus.
    # GLUT_DEPTH: Aktiviert den Tiefenpuffer, um zu wissen, welche Flächen vorne liegen.
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    
    # Setzt die Fenstergröße beim Start auf 800x600 Pixel
    glutInitWindowSize(800, 600)
    
    # Erstellt das Betriebssystem-Fenster (Achtung: Titel MUSS ein Byte-String `b"..."` sein)
    glutCreateWindow(b"Scene Viewer: Punkte und Dreiecke")

    # Aktiviert den Hardware-Z-Buffer (Tiefentest).
    # Ohne diesen Test würden hintere Würfelflächen einfach über vordere Flächen gezeichnet werden.
    glEnable(GL_DEPTH_TEST)

    # Registriert die Event-Funktionen (Callbacks) im GLUT-System.
    # GLUT weiß nun selbstständig, welche Funktion bei welchem Ereignis aufgerufen werden muss.
    glutDisplayFunc(display)  # Wenn neu gezeichnet werden muss
    glutReshapeFunc(reshape)  # Wenn die Fenstergröße geändert wird
    glutMouseFunc(mouse_click)  # Wenn geklickt wird
    glutMotionFunc(mouse_move)  # Wenn die Maus bei gedrückter Taste zieht

    # Startet die unendliche GLUT-Ereignisschleife.
    # Ab diesem Punkt übernimmt GLUT das Programm, fängt Events ab und rendert das Bild.
    glutMainLoop()

if __name__ == "__main__":
    main()