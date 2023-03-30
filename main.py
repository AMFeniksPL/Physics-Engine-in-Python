import math
import random
import time
import numpy
import pygame
from numba.experimental import jitclass
from pygame.locals import *
from threading import Thread

class Ball:

    def __init__(self, x, y, radius, color, game):
        self.velocity = numpy.array((0, 0))

        self.pos_cur = numpy.array((x, y))

        self.pos_old = self.pos_cur.copy()

        self.color = color
        self.radius = radius

        self.screen = game.screen
        self.acceleration = numpy.array([0, 2000])


    def update_position(self, dt):
        self.velocity = self.pos_cur - self.pos_old
        self.pos_old = self.pos_cur.copy()

        self.pos_cur += self.velocity + (self.acceleration * dt * dt)

        self.acceleration = numpy.zeros(2)

    def accelerate(self, acc : numpy.array):
        self.acceleration += acc


    def update(self, dt):
        self.update_position(dt)



    def draw(self):
        pygame.draw.circle(self.screen, (0, 0, 0), tuple(self.pos_cur), self.radius)
        pygame.draw.circle(self.screen, self.color, tuple(self.pos_cur), self.radius - 1)

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
        substeps = 2
        running = True
        while running:

            for i in range(substeps):
                self.apply_gravity()
                self.update_positions(self.dt/2)
                self.solve_collisions()
                self.apply_constraints()


            self.screen.fill((0, 0, 0))
            pygame.draw.circle(self.screen, (100, 100, 100), (self.width/2, self.height/2), 400)
            for ball in self.listOfBalls:
                ball.draw()



            pygame.display.flip()
            clock.tick(60)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

    def create_balls(self):
        for i in range(300):
            randRadius = random.randint(10, 30)
            randColor = self.get_rainbow(time.time())
            self.listOfBalls.append(Ball(self.width/2 + 200, self.height/2 - 100, randRadius, randColor, self))
            time.sleep(0.05)


    def apply_gravity(self):
        for ball in self.listOfBalls:
            ball.accelerate(numpy.array([0, 2000]))


    def update_positions(self, dt):
        for ball in self.listOfBalls:
            ball.update_position(dt)


    def apply_constraints(self):
        center = numpy.array([self.width/2, self.height/2])
        radius = 400

        for ball in self.listOfBalls:
            distance = numpy.linalg.norm(ball.pos_cur - center)
            if distance > radius - ball.radius:
                n = (ball.pos_cur - center) / distance
                ball.pos_cur = center + n * (radius - ball.radius)


    def solve_collisions(self):
        for object1 in self.listOfBalls:
            for object2 in self.listOfBalls:
                if object1 == object2:
                    continue

                diff = object1.pos_cur - object2.pos_cur

                distance = numpy.linalg.norm(diff) + 0.0001
                if distance < object1.radius + object2.radius:
                    normalized = diff / distance
                    delta = object1.radius + object2.radius - distance

                    object1.pos_cur += 0.5 * delta * normalized
                    object2.pos_cur -= 0.5 * delta * normalized



    def get_rainbow(self, t):
        r = math.sin(t)
        g = math.sin(t + 0.33 * 2.0 * math.pi)
        b = math.sin(t + 0.66 * 2.0 * math.pi)
        return 255.0 * r * r, 255.0 * g * g, 255.0 * b * b

newGame = Main(1600, 900)
