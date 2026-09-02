import cv2
import math
import random


class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.randint(20, 60)
        self.max_life = self.life
        self.radius = random.randint(2, 6)
        if color:
            self.color = color
        else:
            self.color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.life -= 1

    def draw(self, frame):
        if self.life > 0:
            alpha = self.life / self.max_life
            r = int(self.radius * alpha)
            if r > 0:
                cv2.circle(frame, (int(self.x), int(self.y)), r, self.color, -1)

    def is_dead(self):
        return self.life <= 0


class ParticleSystem:
    def __init__(self, max_particles=500):
        self.particles = []
        self.max_particles = max_particles

    def emit(self, x, y, count=5, color=None):
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                self.particles.append(Particle(x, y, color))

    def emit_fire(self, x, y, count=3):
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                p = Particle(x, y)
                p.vx = random.uniform(-2, 2)
                p.vy = random.uniform(-4, -1)
                b = random.randint(0, 80)
                g = random.randint(50, 180)
                r = random.randint(150, 255)
                p.color = (b, g, r)
                p.radius = random.randint(2, 5)
                self.particles.append(p)

    def emit_sparkle(self, x, y, count=8):
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                p = Particle(x, y)
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 4)
                p.vx = math.cos(angle) * speed
                p.vy = math.sin(angle) * speed
                p.color = (255, 255, 255)
                p.radius = random.randint(1, 3)
                self.particles.append(p)

    def emit_magic(self, x, y, count=10):
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                p = Particle(x, y)
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.5, 3)
                p.vx = math.cos(angle) * speed
                p.vy = math.sin(angle) * speed
                colors = [
                    (255, 0, 255),
                    (0, 255, 255),
                    (255, 255, 0),
                    (0, 255, 0),
                    (255, 0, 0),
                ]
                p.color = random.choice(colors)
                p.radius = random.randint(2, 5)
                self.particles.append(p)

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, frame):
        for p in self.particles:
            p.draw(frame)

    def clear(self):
        self.particles.clear()


class TrailSystem:
    def __init__(self, max_points=50):
        self.trails = {}
        self.max_points = max_points

    def add_point(self, hand_id, x, y, color=(0, 255, 0)):
        if hand_id not in self.trails:
            self.trails[hand_id] = []
        self.trails[hand_id].append((x, y, color))
        if len(self.trails[hand_id]) > self.max_points:
            self.trails[hand_id].pop(0)

    def draw(self, frame):
        for hand_id, points in self.trails.items():
            for i in range(1, len(points)):
                thickness = int(2 + (i / len(points)) * 6)
                color = points[i][2]
                cv2.line(
                    frame,
                    (points[i - 1][0], points[i - 1][1]),
                    (points[i][0], points[i][1]),
                    color,
                    thickness,
                )

    def clear(self):
        self.trails.clear()
