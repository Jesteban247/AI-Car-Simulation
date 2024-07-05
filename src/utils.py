"""
These functions are essential for loading map data and resizing images in a Pygame-based game or application.
"""

import pygame

def load_map_info():
    with open('files/info.txt', 'r') as f:
        lines = f.readlines()

    map_info = []
    for line in lines:
        map_name, size_x, size_y, pos_x, pos_y = line.strip().split(';')
        map_info.append((map_name, int(size_x), int(size_y), int(pos_x), int(pos_y)))

    return map_info

def scale_image(image, width, height):
    return pygame.transform.scale(image, (width, height))
