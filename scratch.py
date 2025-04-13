import pygame
import random
import time
import sys

pygame.init()

# -----------------------------
# General settings
# -----------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Time Simulation")

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Fonts
font_large = pygame.font.SysFont(None, 48)
font_medium = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 28)

clock = pygame.time.Clock()

# States
STATE_MENU = 0
STATE_SIMULATION = 1
STATE_RESULT = 2

current_state = STATE_MENU

# -----------------------------
# Simulation variables
# -----------------------------
reaction_time = None
start_event_time = None
event_started = False  # indicates when the drifting starts
collision_happened = False

time_to_event = 0
start_test_time = 0

# Car sizes
user_car_width = 50
user_car_height = 80
opponent_car_width = 50
opponent_car_height = 80

# Car positions
user_car_x = 200
user_car_y = HEIGHT // 2 - user_car_height // 2

opponent_car_start_x = 600  # where the opponent starts
opponent_car_y = HEIGHT // 2 - opponent_car_height // 2
opponent_car_x = opponent_car_start_x

drift_speed = 5  # pixels per frame when drifting


# -----------------------------
# Helper functions
# -----------------------------
def draw_button(text, x, y, w, h, inactive_color, active_color, text_color=BLACK):
    """
    Draws a button with text and returns True if it's clicked.
    """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        color = active_color
    else:
        color = inactive_color

    pygame.draw.rect(screen, color, (x, y, w, h))

    txt_surf = font_medium.render(text, True, text_color)
    txt_rect = txt_surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(txt_surf, txt_rect)

    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        if click[0] == 1:  # left-click
            return True
    return False


def draw_text_center(text, font, color, x, y):
    """
    Draws text centered at (x, y).
    """
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)


def start_simulation():
    """
    Resets all needed variables for a new test and gets ready to run.
    """
    global reaction_time, start_event_time, event_started, collision_happened
    global time_to_event, start_test_time
    global opponent_car_x

    reaction_time = None
    start_event_time = None
    event_started = False
    collision_happened = False

    # Random time between 2 to 5 seconds before opponent starts drifting
    time_to_event = random.uniform(2, 5)
    start_test_time = time.time()

    # Reset opponent car position
    opponent_car_x = opponent_car_start_x


def check_collision():
    """
    Checks if the opponent car collides (overlaps) with the user car.
    Returns True if collided, False otherwise.
    """
    user_rect = pygame.Rect(user_car_x, user_car_y, user_car_width, user_car_height)
    opponent_rect = pygame.Rect(opponent_car_x, opponent_car_y, opponent_car_width, opponent_car_height)
    return user_rect.colliderect(opponent_rect)


# -----------------------------
# Main loop
# -----------------------------
running = True
while running:
    clock.tick(60)  # up to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # If we're in the simulation state, listen for SPACE
        if current_state == STATE_SIMULATION and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # if drifting already started and no collision yet
                if event_started and not collision_happened and reaction_time is None:
                    end_time = time.time()
                    reaction_time = end_time - start_event_time
                    current_state = STATE_RESULT

    # Clear screen
    screen.fill(WHITE)

    # -------------- MENU STATE --------------
    if current_state == STATE_MENU:
        draw_text_center("Reaction Time Simulation", font_large, BLACK, WIDTH // 2, HEIGHT // 2 - 50)

        # Start button
        if draw_button("Start Simulation", WIDTH // 2 - 100, HEIGHT // 2, 200, 50, GRAY, (150, 150, 150)):
            start_simulation()
            current_state = STATE_SIMULATION

        # Exit button
        if draw_button("Exit", WIDTH // 2 - 50, HEIGHT // 2 + 70, 100, 40, GRAY, (150, 150, 150)):
            running = False

    # -------------- SIMULATION STATE --------------
    elif current_state == STATE_SIMULATION:
        # Draw user car (green)
        user_car_rect = pygame.Rect(user_car_x, user_car_y, user_car_width, user_car_height)
        pygame.draw.rect(screen, GREEN, user_car_rect)

        # Draw opponent car (red)
        opponent_car_rect = pygame.Rect(opponent_car_x, opponent_car_y, opponent_car_width, opponent_car_height)
        pygame.draw.rect(screen, RED, opponent_car_rect)

        # Has the time for event arrived?
        current_time = time.time()
        elapsed = current_time - start_test_time

        # If we haven't started drifting yet, check if it's time
        if not event_started and elapsed >= time_to_event:
            event_started = True
            start_event_time = time.time()

        # If drifting has started, move the opponent car toward the user car each frame
        if event_started and not collision_happened:
            # Move left until it collides or user reacts
            if opponent_car_x > user_car_x + user_car_width:
                opponent_car_x -= drift_speed  # drifting speed
            else:
                # If the opponent has reached or overlapped user's area, it's a collision
                collision_happened = check_collision()
                if collision_happened and reaction_time is None:
                    # We record reaction_time as None => user didn't respond in time
                    # We can switch to result state with a special message
                    current_state = STATE_RESULT

        # Instructions
        hint_text = font_small.render("Press SPACE as soon as you see the opponent car drifting toward you!", True,
                                      BLACK)
        screen.blit(hint_text, (20, 20))

    # -------------- RESULT STATE --------------
    elif current_state == STATE_RESULT:
        if collision_happened and reaction_time is None:
            # Means user didn't press space in time
            draw_text_center("Collision happened! You did not react in time.", font_medium, RED, WIDTH // 2,
                             HEIGHT // 2 - 40)
        else:
            # User pressed space in time -> show reaction time
            if reaction_time is not None:
                msg = f"Your reaction time: {reaction_time:.3f} seconds"
                draw_text_center(msg, font_medium, BLACK, WIDTH // 2, HEIGHT // 2 - 40)
            else:
                # theoretically shouldn't happen, but just in case
                draw_text_center("No valid reaction time recorded.", font_medium, RED, WIDTH // 2, HEIGHT // 2 - 40)

        # Button to start a new test
        if draw_button("New Test", WIDTH // 2 - 80, HEIGHT // 2 + 10, 160, 50, GRAY, (150, 150, 150)):
            start_simulation()
            current_state = STATE_SIMULATION

        # Exit button
        if draw_button("Exit", WIDTH // 2 - 50, HEIGHT // 2 + 70, 100, 40, GRAY, (150, 150, 150)):
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
