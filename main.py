"""
NEAT-based Car Simulation Project

This project uses the NEAT (NeuroEvolution of Augmenting Topologies) algorithm to evolve neural networks that control cars in a simulation. The cars navigate a track and are evaluated based on their performance, with rewards for moving forward and avoiding crashes. The simulation includes a preview phase where the user can select different maps and start the simulation.

Modules:
- pygame: Used for rendering the simulation and handling user input.
- neat: Used for creating and evolving neural networks.
- src.car: Contains the Car class which defines the car's behavior and properties.
- src.ui: Contains the draw_ui function for rendering the user interface.
- src.utils: Contains utility functions for loading map information and scaling images.
"""

import sys
import time
import pygame
import neat
from src.car import Car
from src.ui import draw_ui
from src.utils import load_map_info, scale_image

# Constants for map dimensions and UI
MAP_WIDTH = 800
HEIGHT = 600
UI_WIDTH = 200
TOTAL_WIDTH = MAP_WIDTH + UI_WIDTH

# Global variables for car and map settings
CAR_SIZE_X = 0
CAR_SIZE_Y = 0
CAR_POS_X = 0
CAR_POS_Y = 0
MAP_NAME = ""

# Variables to track current generation and start time
current_generation = 0
global_start_time = time.time()


def run_simulation(genomes, config, screen, original_map):
    global current_generation, global_start_time, CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y, MAP_NAME
    nets = []
    cars = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        cars.append(Car(CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y))

    clock = pygame.time.Clock()
    current_generation += 1
    counter = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.size
                screen_width = max(screen_width, TOTAL_WIDTH)
                screen_height = max(screen_height, HEIGHT)
                screen = pygame.display.set_mode((screen_width, screen_height),
                                                 pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                return_button_rect = pygame.Rect(MAP_WIDTH + 50,
                                                 HEIGHT // 2 + 25, 100, 50)
                if return_button_rect.collidepoint(mouse_pos):
                    main()

        game_map = scale_image(original_map, MAP_WIDTH, HEIGHT)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10
            elif choice == 1:
                car.angle -= 10
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2
            else:
                car.speed += 2

        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map, MAP_WIDTH, HEIGHT)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:
            break

        screen.fill((255, 255, 255))
        screen.blit(game_map, (0, 0))

        pygame.draw.rect(screen, (200, 200, 200),
                         (MAP_WIDTH, 0, UI_WIDTH, HEIGHT))

        best_car_index = 0
        best_fitness = float('-inf')

        for i, car in enumerate(cars):
            if genomes[i][1].fitness > best_fitness:
                best_fitness = genomes[i][1].fitness
                best_car_index = i

        for i, car in enumerate(cars):
            if car.is_alive():
                rotated_sprite, new_position = car.rotate_center(
                    car.sprite, car.angle)
                screen.blit(rotated_sprite, new_position)

                if i == best_car_index:
                    for radar in car.radars:
                        position = radar[0]
                        pygame.draw.line(screen, (255, 255, 0), car.center,
                                         position, 1)
                        pygame.draw.circle(screen, (255, 255, 0), position, 5)
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (*car.position, CAR_SIZE_X, CAR_SIZE_Y),
                                     2)

        global_elapsed_time = time.time() - global_start_time
        draw_ui(screen, current_generation, still_alive, global_elapsed_time)

        return_button_rect = pygame.Rect(MAP_WIDTH + 50, HEIGHT // 2 + 25, 100,
                                         50)
        pygame.draw.rect(screen, (255, 0, 0), return_button_rect)
        font = pygame.font.SysFont("Arial", 30)
        return_text = font.render("Return", True, (0, 0, 0))
        return_text_rect = return_text.get_rect(
            center=return_button_rect.center)
        screen.blit(return_text, return_text_rect)

        pygame.display.flip()
        clock.tick(60)

    return 'continue'


def preview(screen, original_map, map_info):
    global global_start_time, CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y, MAP_NAME

    car = Car(CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y)
    current_map_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.size
                screen_width = max(screen_width, TOTAL_WIDTH)
                screen_height = max(screen_height, HEIGHT)
                screen = pygame.display.set_mode((screen_width, screen_height),
                                                 pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                next_button_rect = pygame.Rect(MAP_WIDTH + 50,
                                               HEIGHT // 2 - 75, 100, 50)
                play_button_rect = pygame.Rect(MAP_WIDTH + 50,
                                               HEIGHT // 2 - 25, 100, 50)
                if next_button_rect.collidepoint(mouse_pos):
                    current_map_index = (current_map_index + 1) % len(map_info)
                    MAP_NAME, CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y = map_info[
                        current_map_index]
                    original_map = pygame.image.load(MAP_NAME).convert()
                    car = Car(CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y)
                elif play_button_rect.collidepoint(mouse_pos):
                    global_start_time = time.time()
                    return 'play'

        game_map = scale_image(original_map, MAP_WIDTH, HEIGHT)

        screen.fill((255, 255, 255))
        screen.blit(game_map, (0, 0))

        rotated_sprite, new_position = car.rotate_center(car.sprite, car.angle)
        screen.blit(rotated_sprite, new_position)

        pygame.draw.rect(screen, (200, 200, 200),
                         (MAP_WIDTH, 0, UI_WIDTH, HEIGHT))

        next_button_rect = pygame.Rect(MAP_WIDTH + 50, HEIGHT // 2 - 75, 100,
                                       50)
        pygame.draw.rect(screen, (0, 0, 255), next_button_rect)
        play_button_rect = pygame.Rect(MAP_WIDTH + 50, HEIGHT // 2 - 25, 100,
                                       50)
        pygame.draw.rect(screen, (0, 255, 0), play_button_rect)

        font = pygame.font.SysFont("Arial", 30)
        next_text = font.render("Next", True, (0, 0, 0))
        next_text_rect = next_text.get_rect(center=next_button_rect.center)
        screen.blit(next_text, next_text_rect)
        play_text = font.render("Play", True, (0, 0, 0))
        play_text_rect = play_text.get_rect(center=play_button_rect.center)
        screen.blit(play_text, play_text_rect)

        pygame.display.flip()


def main():
    global current_generation, global_start_time
    current_generation = 0

    global CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y, MAP_NAME
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT), pygame.RESIZABLE)

    map_info = load_map_info()
    if map_info:
        MAP_NAME, CAR_SIZE_X, CAR_SIZE_Y, CAR_POS_X, CAR_POS_Y = map_info[0]

    original_map = pygame.image.load(MAP_NAME).convert()

    while True:
        global_start_time = time.time()
        action = preview(screen, original_map, map_info)

        if action == 'play':
            original_map = pygame.image.load(MAP_NAME).convert()
            config_path = "files/neat_config.txt"
            config = neat.config.Config(neat.DefaultGenome,
                                        neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet,
                                        neat.DefaultStagnation, config_path)

            population = neat.Population(config)
            population.add_reporter(neat.StdOutReporter(True))
            stats = neat.StatisticsReporter()
            population.add_reporter(stats)

            while True:
                result = population.run(
                    lambda genomes, config: run_simulation(
                        genomes, config, screen, original_map), 1)
                if result == 'menu':
                    break


if __name__ == "__main__":
    main()
