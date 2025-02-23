import pygame
import paho.mqtt.client as mqtt
import time
import json
import os
from PIL import Image
from fish import Fish
from utils import *
#pip install pillow

# Pygame setup
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))  # Larger screen size (1200x800)
pygame.display.set_caption("Parallel Pond")

# Create an MQTT client instance
client = mqtt.Client()

# Set username and password for the connection
client.username_pw_set(USERNAME, PASSWORD)

# Assign event callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(BROKER, PORT, 60)

# Start the network loop
client.loop_start()

# Subscribe to the same topic to receive messages
client.subscribe(TOPIC)
client.subscribe("user/Parallel")


# Main loop to keep the script running and display messages
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle button click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check if the mouse click is inside the Spawn Picture button area
            if button_rect_spawn.collidepoint(mouse_x, mouse_y):
                # Spawn a new fish (GIF) at a random position in the pond
                fish_position = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
                fish_animations.append(Fish(fish_frames, fish_position))  # Add new fish to the list
                
            # Check if the mouse click is inside the Send Message button area
            if button_rect_send.collidepoint(mouse_x, mouse_y) and fish_animations:
                send_fish_to_topicX(client, DC_UNIVERSE, f"Fish{fish_animations[0].name}", fish_animations[0].remainingLifetime)
                fish_animations.pop(0)  # Remove the first fish in the list

    # Fill the screen with the background color
    screen.fill(bg_color)

    # Draw the blue circle in the center (pond)
    pygame.draw.circle(screen, circle_color, pond_center, pond_radius)

    # Update and draw the fish (GIFs) inside the pond
    for fish in fish_animations:
        if not fish.update():
            print("removed fish", fish.name)
            fish_animations.remove(fish)  # Remove the fish if its lifetime is over
        fish.draw(screen)

    # Draw the "Spawn Picture" button on the left
    button_rect_spawn = pygame.Rect(10, 550, 200, 50)  # Bottom-left corner (10, 550)
    pygame.draw.rect(screen, button_color, button_rect_spawn)
    button_text_spawn = font.render("Spawn Fish", True, button_text_color)
    screen.blit(button_text_spawn, (button_rect_spawn.x + 10, button_rect_spawn.y + 10))  # Center the text

    # Draw the "Send Message" button on the right
    button_rect_send = pygame.Rect(990, 550, 200, 50)  # Bottom-right corner (990, 550)
    pygame.draw.rect(screen, button_color, button_rect_send)
    button_text_send = font.render("Send Fish", True, button_text_color)
    screen.blit(button_text_send, (button_rect_send.x + 10, button_rect_send.y + 10))  # Center the text

    # Display the amount of fish
    fish_amount = len(fish_animations)
    fish_amount_text = font.render(f"Fish Amount: {fish_amount}", True, text_color)
    screen.blit(fish_amount_text, (10, 10))  # Display at the top-left corner

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 frames per second
    clock.tick(60)

