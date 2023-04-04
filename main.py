import math
import time

import pygame
import pygame.gfxdraw

from threading import Thread
import webbrowser

from multiprocessing import Process, cpu_count

class Ball:

    def __init__(self, x, y, radius, color):
        self.velX = 0
        self.velY = 0

        self.x_cur = x
        self.y_cur = y

        self.x_old = x
        self.y_old = y

        self.radius = radius

        self.accX = 0
        self.accY = 1000

        self.color = color


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
        self.listOfPreviousBalls = []

        Thread(target=self.import_pos).start()

        # Thread(target=self.create_balls).start()
        # self.create_balls()
        substeps = 4
        self.running = True

        self.cellSize = 40

        self.gridW, self.gridH = int(self.width//self.cellSize) + 1, int(self.height//self.cellSize) + 1
        # self.collisionGrid = [[[] for j in range(self.gridW)] for i in range(self.gridH)]
        self.collisionGrid = [[[] for j in range(self.gridW)] for i in range(self.gridH)]

        self.background = pygame.image.load("Rick Astley Image.jpg")
        self.background = pygame.transform.scale(self.background, (self.width, self.height)).convert_alpha()

        self.ballCount = 0
        self.canCreateBall = True
        self.lastTimeOfBallSpawn = time.time()
        self.ballTimeDelay = 0.02


        self.startGameTime = time.time()


        while self.running:
            physics_time = pygame.time.get_ticks()

            if self.ballCount < 1000:
                self.create_ball(self.ballCount)
                self.lastTimeOfBallSpawn = time.time()
                self.canCreateBall = False


            elif time.time() - self.lastTimeOfBallSpawn > self.ballTimeDelay:
                self.canCreateBall = True



            for i in range(substeps):
                self.apply_gravity()
                self.add_objects_to_grid()
                self.find_collision_grid()
                # self.solve_collisions()
                self.apply_constraints()
                self.update_positions((1/60) / substeps)

            physics_time = pygame.time.get_ticks() - physics_time

            render_time = pygame.time.get_ticks()
            self.screen.fill((0, 0, 0))
            pygame.draw.circle(self.screen, (100, 100, 100), (self.width/2, self.height/2), 400)

            for ball, ballMeta in zip(self.listOfBalls, self.listOfPreviousBalls):
                pygame.gfxdraw.filled_circle(self.screen, int(ball.x_cur), int(ball.y_cur), int(ball.radius),
                                             ballMeta.color)
                pygame.gfxdraw.aacircle(self.screen, int(ball.x_cur), int(ball.y_cur), int(ball.radius), (0, 0, 0))


            # for ball in self.listOfPreviousBalls:
            #     pygame.gfxdraw.aacircle(self.screen, int(ball.x_cur), int(ball.y_cur), int(ball.radius), ball.color)
            # # self.screen.blit(self.background, (0, 0))




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

            if time.time() - self.startGameTime > 40:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

        self.check_balls()
        webbrowser.open_new("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley")
        pygame.quit()
    #
    # def create_balls(self):
    #     for i in range(500):
    #         randRadius = 7 + (i % 18)
    #         # randColor = self.get_rainbow(time.time())
    #         self.listOfBalls.append(Ball(self.width/2 + 200, self.height/2 - 100, randRadius))
    #         time.sleep(0.01)

    def create_ball(self, i):
            # randRadius = 7 + (i % 18)
            radius = 12
            randColor = self.get_rainbow(i)
            x = self.width/2 + 400 * math.cos(i/20)
            y = self.height/2 + 400 * math.sin(i/20)
            self.listOfBalls.append(Ball(x, y, radius, randColor))
            self.ballCount += 1


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



    def check_balls(self):
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        with open("info_about_balls.txt", "w") as f:
            for ball in self.listOfBalls:
                ball.color = self.screen.get_at((int(ball.x_cur), int(ball.y_cur)))
                f.write(f"{ball.x_cur} {ball.y_cur} {ball.radius} {ball.color[0]} {ball.color[1]} {ball.color[2]}\n")
        pygame.image.save(self.screen, "screenshot.jpg")
        print("Saving finished")

    def import_pos(self):
        with open("info_about_balls.txt", "r") as f:
            for line in f.readlines():
                x, y, radius, r, g, b = line.split()
                self.listOfPreviousBalls.append(Ball(float(x), float(y), float(radius), (float(r), float(g), float(b))))



newGame = Main(1600, 900)
