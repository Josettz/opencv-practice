import cv2
import math


class VirtualDrawer:
    def __init__(self):
        self.drawing = False
        self.lines = []
        self.current_line = []
        self.brush_color = (0, 255, 255)
        self.brush_size = 4
        self.shapes = []
        self.mode = "draw"
        self.undo_stack = []

    def start_draw(self, x, y):
        self.drawing = True
        self.current_line = [(x, y)]

    def add_point(self, x, y):
        if self.drawing:
            self.current_line.append((x, y))

    def end_draw(self):
        if self.drawing and len(self.current_line) > 1:
            self.lines.append(
                {
                    "points": list(self.current_line),
                    "color": self.brush_color,
                    "size": self.brush_size,
                }
            )
        self.current_line = []
        self.drawing = False

    def add_circle(self, x, y, radius=50):
        self.shapes.append(
            {"type": "circle", "center": (x, y), "radius": radius, "color": self.brush_color}
        )

    def add_rectangle(self, x1, y1, x2, y2):
        self.shapes.append(
            {"type": "rect", "pt1": (x1, y1), "pt2": (x2, y2), "color": self.brush_color}
        )

    def undo(self):
        if self.lines:
            self.undo_stack.append(self.lines.pop())
        elif self.shapes:
            self.undo_stack.append(("shape", self.shapes.pop()))

    def redo(self):
        if self.undo_stack:
            item = self.undo_stack.pop()
            if isinstance(item, dict):
                self.lines.append(item)
            elif isinstance(item, tuple) and item[0] == "shape":
                self.shapes.append(item[1])

    def clear_all(self):
        self.lines.clear()
        self.shapes.clear()
        self.current_line = []
        self.undo_stack.clear()

    def draw(self, frame):
        for shape in self.shapes:
            if shape["type"] == "circle":
                cv2.circle(frame, shape["center"], shape["radius"], shape["color"], 2)
            elif shape["type"] == "rect":
                cv2.rectangle(frame, shape["pt1"], shape["pt2"], shape["color"], 2)

        for line in self.lines:
            points = line["points"]
            for i in range(1, len(points)):
                cv2.line(frame, points[i - 1], points[i], line["color"], line["size"])

        if self.current_line and len(self.current_line) > 1:
            for i in range(1, len(self.current_line)):
                cv2.line(
                    frame,
                    self.current_line[i - 1],
                    self.current_line[i],
                    self.brush_color,
                    self.brush_size,
                )

    def set_color(self, color):
        self.brush_color = color

    def set_size(self, size):
        self.brush_size = size


class GestureInterpreter:
    def __init__(self):
        self.prev_x = None
        self.prev_y = None
        self.click_cooldown = 0
        self.last_gesture = "none"

    def interpret(self, gesture, x, y, drawer):
        result = ""

        if self.click_cooldown > 0:
            self.click_cooldown -= 1

        if gesture == "open":
            if not drawer.drawing:
                drawer.start_draw(x, y)
            drawer.add_point(x, y)
            result = "Drawing"

        elif gesture == "fist":
            if drawer.drawing:
                drawer.end_draw()
            result = "Stop"
#-
        elif gesture == "point":
            if self.prev_x is not None and self.click_cooldown == 0:
                dx = x - self.prev_x
                dy = y - self.prev_y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 5:
                    drawer.add_circle(x, y, radius=20)
                    self.click_cooldown = 15
                    result = "Stamp"
            if drawer.drawing:
                drawer.end_draw()

        elif gesture == "peace":
            if self.click_cooldown == 0:
                drawer.undo()
                self.click_cooldown = 20
                result = "Undo"
            if drawer.drawing:
                drawer.end_draw()

        elif gesture == "thumbs_up":
            if self.click_cooldown == 0:
                drawer.clear_all()
                self.click_cooldown = 30
                result = "Clear"
            if drawer.drawing:
                drawer.end_draw()

        elif gesture == "pinch":
            colors = [
                (0, 255, 255),
                (255, 0, 255),
                (255, 255, 0),
                (0, 255, 0),
                (0, 0, 255),
                (255, 255, 255),
            ]
            if self.click_cooldown == 0:
                idx = colors.index(drawer.brush_color) if drawer.brush_color in colors else 0
                drawer.set_color(colors[(idx + 1) % len(colors)])
                self.click_cooldown = 20
                result = "Color"
            if drawer.drawing:
                drawer.end_draw()
        else:
            if drawer.drawing:
                drawer.end_draw()

        self.prev_x = x
        self.prev_y = y
        self.last_gesture = gesture
        return result
