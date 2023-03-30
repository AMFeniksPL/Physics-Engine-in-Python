import random
import time

import pygame
from numba.experimental import jitclass
from pygame.locals import *
from threading import Thread





class Ball:

    def __init__(self, x, y, radius, game):
        self.velX = 0
        self.velY = 0

        self.x_cur = x
        self.y_cur = y

        self.x_old = x
        self.y_old = y


        self.radius = radius

        self.screen = game.screen
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



    def draw(self):
        pygame.draw.circle(self.screen, (0, 0, 0), (self.x_cur, self.y_cur), self.radius)
        pygame.draw.circle(self.screen, (255,255,255), (self.x_cur, self.y_cur), self.radius - 1)

class Main():


    def __init__(self, width, height):

        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))

        clock = pygame.time.Clock()

        self.listOfBalls = []

        Thread(target = self.create_balls).start()

        running = True
        while running:

            self.apply_gravity()
            self.update_positions()
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
        for i in range(205):
            # randX = random.randint(self.width/2 + 200, self.width/2 + 200)
            # randY = random.randint(self.height/2 - 100, self.height/2 + 100)

            randRadius = random.randint(10, 40)
            self.listOfBalls.append(Ball(self.width/2 + 200, self.height/2 - 100, randRadius, self))
            time.sleep(0.05)


    def apply_gravity(self):
        for ball in self.listOfBalls:
            ball.accelerate(0, 2000)


    def update_positions(self):
        for ball in self.listOfBalls:
            ball.update_position(1/60)


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
        for object1 in self.listOfBalls:
            for object2 in self.listOfBalls:
                if object1 == object2:
                    continue

                diff_x = object1.x_cur - object2.x_cur
                diff_y = object1.y_cur - object2.y_cur

                distance = (diff_x ** 2 + diff_y ** 2) ** 0.5 + 0.0001
                if distance < object1.radius + object2.radius:
                    normalized = (diff_x / distance, diff_y / distance)
                    delta = object1.radius + object2.radius - distance
                    object1.x_cur += 0.5 * delta * normalized[0]
                    object1.y_cur += 0.5 * delta * normalized[1]

                    object2.x_cur -= 0.5 * delta * normalized[0]
                    object2.y_cur -= 0.5 * delta * normalized[1]




newGame = Main(1600, 900)
