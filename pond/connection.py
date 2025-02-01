import pygame
import paho.mqtt.client as mqtt
import time
import json
import random
import math
import os
from PIL import Image
from fish import Fish
#pip install pillow

# MQTT server details
BROKER = "40.90.169.126"
PORT = 1883
USERNAME = "dc24"
PASSWORD = "kmitl-dc24"
TOPIC = "fishhaven/stream"

# Define topic for each users

# topic for sending to DC_UNIVERSE group
DC_UNIVERSE = "user/DC_Universe"


# Define the "hello" message
HELLO_MESSAGE = {
    "type": "hello",
    "sender": "Parallel",
    "timestamp": int(time.time()),
    "data": {}
}

SEND_MESSAGE = {
    "type": "message",
    "sender": "User",
    "timestamp": int(time.time()),
    "data": {
        "text": "Hello from Pygame button!"
    }
}

# Pygame setup
pygame.init()
screen_width, screen_height = 1200, 800
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))  # Larger screen size (1200x800)
pygame.display.set_caption("MQTT Message Pond with GIF")
font = pygame.font.Font(None, 36)
text_color = (255, 255, 255)  # White text
bg_color = (26, 148, 49)  # Green background
button_color = (0, 128, 0)  # Green button
button_text_color = (255, 255, 255)  # White text for the button
circle_color = (173, 216, 230)  # Blue circle

# To hold the GIF frames and current animations
fish_animations = []
last_update_time = time.time()

# To hold the latest received messages
received_messages = []

# Load and resize GIF frames
def load_gif_frames(gif_path):
    frames = []
    try:
        gif = Image.open(gif_path)
        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame_image = gif.convert("RGBA")
            frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
            frame_surface = pygame.transform.scale(frame_surface, (50, 50))
            frames.append(frame_surface)
        return frames
    except Exception as e:
        print(f"Unable to load GIF frames: {e}")
        return []

fish_frames = load_gif_frames("./lib/assets/Parallel.gif")
# fish_frames = load_gif_frames("./lib/assets/DC_UNIVERSE.gif")

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        # Publish the "hello" message
        client.publish(TOPIC, json.dumps(HELLO_MESSAGE))
        print("Published message:", HELLO_MESSAGE)
    else:
        print("Failed to connect, return code %d\n", rc)

# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message received on topic {msg.topic}: {message}")
    if msg.topic == "user/DC_Universe":
        DC_FRAME = load_gif_frames("./lib/assets/DC_Universe.gif")
        DC_POSITION = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
        fish_animations.append(Fish(DC_FRAME, DC_POSITION, message.name))

    # Add received message to the list
    received_messages.append(message)
    if len(received_messages) > 10:  # Keep only the latest 10 messages
        received_messages.pop(0)

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

def send_fish_to_topicX(topicX, fishName, remainingLifetime):
    print("Sending message to topic:", topicX)
    message = { 
        "name": fishName,
        "group_name": "Parallel",
        "lifetime": remainingLifetime
    } 
    print(f"Sending message: {message}")
    client.publish(topicX, json.dumps(message))

# Generate a random position within the circle
def generate_random_position(center, radius, image_rect):
    # Random angle in radians
    angle = random.uniform(0, 2 * math.pi)
    # Random distance from the center within the radius of the circle
    distance = random.uniform(0, radius - image_rect.width / 2)
    # Convert polar coordinates to cartesian coordinates
    x = center[0] + distance * math.cos(angle)
    y = center[1] + distance * math.sin(angle)
    return x, y

# Main loop to keep the script running and display messages
running = True
fish_id = 0
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
                fish_animations.append(Fish(fish_frames, fish_position, fish_id))  # Add new fish to the list
                fish_id += 1  # Increment the fish ID
                
            # Check if the mouse click is inside the Send Message button area
            if button_rect_send.collidepoint(mouse_x, mouse_y) and fish_animations:
                send_fish_to_topicX(DC_UNIVERSE, f"Fish{fish_animations[0].name}", fish_animations[0].remainingLifetime)
                fish_animations.pop(0)  # Remove the first fish in the list

    # Fill the screen with the background color
    screen.fill(bg_color)

    # Calculate center of the screen for the pond
    pond_center = (screen_width // 2, screen_height // 2)  # Center of screen (600, 400)
    pond_radius = 200

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

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 frames per second
    clock.tick(60)

