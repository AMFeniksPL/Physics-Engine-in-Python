import math
import random
import time

import numba
import pygame
import pygame.gfxdraw
from numba import jit
from numba.experimental import jitclass
from pygame.locals import *
from threading import Thread
import numpy as np



# spec = [
#     ('velX', numba.float32),
#     ('velY', numba.float32),
#     ('x_cur', numba.float32),
#     ('y_cur', numba.float32),
#     ('x_old', numba.float32),
#     ('y_old', numba.float32),
#     ('radius', numba.float32),
#     ('accX', numba.float32),
#     ('accY', numba.float32),
# ]
# @jitclass(spec)
class Ball:

    def __init__(self, x, y, radius):
        self.velX = 0
        self.velY = 0

        self.x_cur = x
        self.y_cur = y

        self.x_old = x
        self.y_old = y

        self.radius = radius

        self.accX = 0
        self.accY = 1000


    def update_position(self, dt):
        self.velX = self.x_cur - self.x_old
        self.velY = self.y_cur - self.y_old

        self.x_old = self.x_cur
        self.y_old = self.y_cur


        self.x_cur += self.velX + self.accX * dt * dt
        self.y_cur += self.velY + self.accY * dt * dt

        self.accX = 0
        self.accY = 0


    def accelerate(self, accX, accY):
        self.accX += accX
        self.accY += accY


    def update(self, dt):
        self.update_position(dt)



    # def draw(self):
    #     # pygame.draw.circle(self.screen, self.color, (self.x_cur, self.y_cur), self.radius)
    #     pygame.gfxdraw.filled_circle(self.screen, int(self.x_cur), int(self.y_cur), int(self.radius), (255, 255, 255))
    #     pygame.gfxdraw.aacircle(self.screen, int(self.x_cur), int(self.y_cur), int(self.radius), (0, 0, 0))
class Main():




    def __init__(self, width, height):

        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.dt = 1/60
        clock = pygame.time.Clock()

        self.listOfBalls = []

        Thread(target=self.create_balls).start()
        # self.create_balls()
        substeps = 4
        running = True

        self.cellSize = 20

        self.gridW, self.gridH = int(self.width//self.cellSize) + 1, int(self.height//self.cellSize) + 1
        # self.collisionGrid = [[[] for j in range(self.gridW)] for i in range(self.gridH)]
        self.collisionGrid = [[[] for j in range(self.gridW)] for i in range(self.gridH)]

        self.background = pygame.image.load("Phoenix Wallpaper.png")
        self.background = pygame.transform.scale(self.background, (self.width, self.height)).convert_alpha()
        while running:
            physics_time = pygame.time.get_ticks()
            for i in range(substeps):
                self.apply_gravity()
                self.add_objects_to_grid()
                self.find_collision_grid()
                # self.solve_collisions()
                self.apply_constraints()
                self.update_positions(self.dt / substeps)

            physics_time = pygame.time.get_ticks() - physics_time

            render_time = pygame.time.get_ticks()
            self.screen.fill((0, 0, 0))
            pygame.draw.circle(self.screen, (100, 100, 100), (self.width/2, self.height/2), 400)
            for ball in self.listOfBalls:
                pygame.gfxdraw.filled_circle(self.screen, int(ball.x_cur), int(ball.y_cur), int(ball.radius),
                                             (255, 255, 255))
                pygame.gfxdraw.aacircle(self.screen, int(ball.x_cur), int(ball.y_cur), int(ball.radius), (0, 0, 0))


            self.screen.blit(self.background, (0, 0))
            # Stats
            render_time = pygame.time.get_ticks() - render_time
            fps = int(clock.get_fps())
            font = pygame.font.SysFont(None, 20)
            physics_text = font.render(f"Physics time: {physics_time} ms", True, (255, 255, 255))
            render_text = font.render(f"Render time: {render_time} ms", True, (255, 255, 255))
            fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
            self.screen.blit(physics_text, (10, 10))
            self.screen.blit(render_text, (10, 30))
            self.screen.blit(fps_text, (10, 50))


            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

    def create_balls(self):
        for i in range(1200):
            randRadius = 7 + (i % 8)
            # randColor = self.get_rainbow(time.time())
            self.listOfBalls.append(Ball(self.width/2 + 200, self.height/2 - 100, randRadius))
            time.sleep(0.01)

    def apply_gravity(self):
        for ball in self.listOfBalls:
            ball.accelerate(0, 2000)

    def update_positions(self, dt):
        for ball in self.listOfBalls:
            ball.update_position(dt)

    def apply_constraints(self):
        center = (self.width/2, self.height/2)
        radius = 400

        for ball in self.listOfBalls:
            distance = ((ball.x_cur - center[0]) ** 2 + (ball.y_cur - center[1]) ** 2) ** 0.5
            if distance > radius - ball.radius:
                n = ((ball.x_cur - center[0]) / distance, (ball.y_cur - center[1]) / distance)
                ball.x_cur = center[0] + n[0] * (radius - ball.radius)
                ball.y_cur = center[1] + n[1] * (radius - ball.radius)

    def solve_collisions(self):
        for i, object1 in enumerate(self.listOfBalls):
            for j, object2 in enumerate(self.listOfBalls[:i]):
                if i == j:
                    continue

                diff_x = object1.x_cur - object2.x_cur
                diff_y = object1.y_cur - object2.y_cur

                distance = (diff_x ** 2 + diff_y ** 2) ** 0.5 + 0.00000001
                if distance < object1.radius + object2.radius:
                    normalized = (diff_x / distance, diff_y / distance)
                    delta = object1.radius + object2.radius - distance
                    object1.x_cur += 0.5 * delta * normalized[0]
                    object1.y_cur += 0.5 * delta * normalized[1]

                    object2.x_cur -= 0.5 * delta * normalized[0]
                    object2.y_cur -= 0.5 * delta * normalized[1]

    def get_rainbow(self, t):
        r = math.sin(t)
        g = math.sin(t + 0.33 * 2.0 * math.pi)
        b = math.sin(t + 0.66 * 2.0 * math.pi)
        return 255.0 * r * r, 255.0 * g * g, 255.0 * b * b

    def add_objects_to_grid(self):
        self.collisionGrid = [[[] for j in range(self.gridW)] for i in range(self.gridH)]

        for i in range(len(self.listOfBalls)):
            # try:
                newH = int(self.listOfBalls[i].y_cur // self.cellSize)
                newW = int(self.listOfBalls[i].x_cur // self.cellSize)
                self.collisionGrid[newH][newW].append(i)

    def find_collision_grid(self):
        for i in range(1, len(self.collisionGrid) - 1):
            for j in range(1, len(self.collisionGrid[0]) - 1):
                cell = self.collisionGrid[i][j]
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        otherCell = self.collisionGrid[i + di][j + dj]
                        self.check_cells_collisions(cell, otherCell)

    def check_cells_collisions(self, cell1, cell2):
        for i in cell1:
            for j in cell2:
                object1 = self.listOfBalls[i]
                object2 = self.listOfBalls[j]

                if object1 != object2:
                    diff_x = object1.x_cur - object2.x_cur
                    diff_y = object1.y_cur - object2.y_cur

                    distance = (diff_x ** 2 + diff_y ** 2) ** 0.5 + 0.00000001
                    if distance < object1.radius + object2.radius:
                        normalized = (diff_x / distance, diff_y / distance)
                        delta = object1.radius + object2.radius - distance
                        object1.x_cur += 0.5 * delta * normalized[0]
                        object1.y_cur += 0.5 * delta * normalized[1]

                        object2.x_cur -= 0.5 * delta * normalized[0]
                        object2.y_cur -= 0.5 * delta * normalized[1]


newGame = Main(1600, 900)
