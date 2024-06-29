import pygame

MAP_WIDTH = 800
HEIGHT = 600
UI_WIDTH = 200
TOTAL_WIDTH = MAP_WIDTH + UI_WIDTH

def draw_ui(screen, generation, alive, global_elapsed_time):
    # Font setup
    font = pygame.font.SysFont("Arial", 30)

    # Generation text
    gen_text = font.render(f"Gen: {generation}", True, (0, 0, 0))  # Render generation text
    screen.blit(gen_text, (MAP_WIDTH + 20, 50))  # Display at specified position

    # Alive cars text
    alive_text = font.render(f"Alive: {alive}", True, (0, 0, 0))  # Render alive cars text
    screen.blit(alive_text, (MAP_WIDTH + 20, 100))  # Display at specified position

    # Global elapsed time text
    time_text = font.render(f"Time: {int(global_elapsed_time)}s", True, (0, 0, 0))  # Render elapsed time text
    screen.blit(time_text, (MAP_WIDTH + 20, 150))  # Display at specified position
