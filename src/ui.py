"""
This code defines a function to draw the user interface (UI) for a car simulation game using Pygame. The UI displays the generation number, the number of alive cars, and the global elapsed time.
"""

import pygame

MAP_WIDTH = 800
HEIGHT = 600
UI_WIDTH = 200
TOTAL_WIDTH = MAP_WIDTH + UI_WIDTH


def draw_ui(screen, generation, alive, global_elapsed_time):
    font = pygame.font.SysFont("Arial", 30)

    gen_text = font.render(f"Gen: {generation}", True, (0, 0, 0))
    screen.blit(gen_text, (MAP_WIDTH + 20, 50))

    alive_text = font.render(f"Alive: {alive}", True, (0, 0, 0))
    screen.blit(alive_text, (MAP_WIDTH + 20, 100))

    time_text = font.render(f"Time: {int(global_elapsed_time)}s", True,
                            (0, 0, 0))
    screen.blit(time_text, (MAP_WIDTH + 20, 150))
    