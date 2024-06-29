import pygame

def load_map_info():
    """
    Load map information from a text file.

    Returns:
    List of tuples: Each tuple contains (map_name, size_x, size_y, pos_x, pos_y).
    """
    with open('files/info.txt', 'r') as f:
        lines = f.readlines()

    map_info = []
    for line in lines:
        map_name, size_x, size_y, pos_x, pos_y = line.strip().split(';')
        map_info.append((map_name, int(size_x), int(size_y), int(pos_x), int(pos_y)))

    return map_info

def scale_image(image, width, height):
    """
    Scale an image to the specified width and height.

    Args:
    image (Surface): The pygame Surface object representing the image.
    width (int): Desired width of the scaled image.
    height (int): Desired height of the scaled image.

    Returns:
    Surface: The scaled pygame Surface object.
    """
    return pygame.transform.scale(image, (width, height))

