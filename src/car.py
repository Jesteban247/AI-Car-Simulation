import math
import pygame
from collections import defaultdict

# Constants
CAR_SIZE_X = 0
CAR_SIZE_Y = 0
BORDER_COLOR = (255, 255, 255, 255)  # Assuming border color is white
AVOIDANCE_RADIUS = 50  # Radius within which avoidance behavior is triggered
SECTOR_SIZE = 100  # Size of each sector for sector-based avoidance

class Car:
    def __init__(self, sizex, sizey, startx, starty):
        global CAR_SIZE_X, CAR_SIZE_Y
        CAR_SIZE_X = sizex
        CAR_SIZE_Y = sizey

        self.sprite = pygame.image.load('images/car.png').convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        self.position = [startx, starty]
        self.angle = 0
        self.speed = 0
        self.speed_set = False

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]

        self.radars = []
        self.drawing_radars = []

        self.alive = True
        self.distance = 0
        self.time = 0

        self.crash_points = defaultdict(int)  # Dictionary to store crash points with weights

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)
        self.draw_radar(screen)
        self.draw_bounding_box(screen)

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (255, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (255, 255, 0), position, 5)

    def draw_bounding_box(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (*self.position, CAR_SIZE_X, CAR_SIZE_Y), 2)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                self.record_crash_point()
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length += 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, game_map, width, height):
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        self.avoid_crash_points()

        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 0)
        self.position[0] = min(self.position[0], width - CAR_SIZE_X)

        self.distance += self.speed
        self.time += 1

        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 0)
        self.position[1] = min(self.position[1], height - CAR_SIZE_Y)

        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
                    self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
                     self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
                       self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
                        self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(game_map)
        self.radars.clear()

        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        return self.alive

    def get_reward(self):
        reward = self.distance / (CAR_SIZE_X / 2)
        if not self.is_alive():
            reward -= 1000
        return reward

    def rotate_center(self, image, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(topleft=self.position).center)
        return rotated_image, new_rect.topleft

    def record_crash_point(self):
        """Record the crash point and angle if the car crashes, with a weight."""
        if not self.is_alive():
            crash_point = (self.center[0], self.center[1], self.angle)
            self.crash_points[crash_point] += 1  # Increment weight for this crash point

    def avoid_crash_points(self):
        """Adjust the car's direction if it's near a previous crash point with significant weight."""
        for crash_point, weight in self.crash_points.items():
            point_x, point_y, point_angle = crash_point
            dist = math.sqrt((self.center[0] - point_x) ** 2 + (self.center[1] - point_y) ** 2)
            if dist < AVOIDANCE_RADIUS:
                avoidance_factor = min(weight, 10)  # Limit the influence of the weight
                if point_angle < self.angle:
                    self.angle += 5 * avoidance_factor  # Adjust more based on weight
                else:
                    self.angle -= 5 * avoidance_factor
                break  # Adjust only once for the nearest significant crash point