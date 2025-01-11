import pygame
import paho.mqtt.client as mqtt
import time
import json
import random
import math
import os
from PIL import Image
#pip install pillow

# MQTT server details
BROKER = "40.90.169.126"
PORT = 1883
USERNAME = "dc24"
PASSWORD = "kmitl-dc24"
TOPIC = "fishhaven/stream"

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

# Load and resize GIF frames as individual images
def load_gif_frames():
    frames = []
    try:
        frames.append(pygame.image.load("./lib/assets/tile1.png"))
        frames.append(pygame.image.load("./lib/assets/tile2.png"))
        frames.append(pygame.image.load("./lib/assets/tile3.png"))
        frames.append(pygame.image.load("./lib/assets/tile4.png"))
        # Resize frames to 50x50
        frames = [pygame.transform.scale(frame, (50, 50)) for frame in frames]
        return frames
    except pygame.error as e:
        print(f"Unable to load images: {e}")
        return []

fish_frames = load_gif_frames()  # Load and resize the frames for the GIF

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

# Function to send a message when the button is pressed
def send_mqtt_message(gif_path):
    print("Sending message with GIF:", gif_path)
    message = {
        "type": "image_sequence",
        "sender": "User",
        "timestamp": int(time.time()),
        "data": {
            "gif_path": gif_path  # Send the path of the GIF file
        }
    }
    client.publish(TOPIC, json.dumps(message))

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

# Fish class to hold the fish GIF animation
class Fish:
    def __init__(self, frames, position):
        self.frames = frames
        self.position = position
        self.current_frame_index = 0
        self.last_frame_time = time.time()

    def update(self):
        current_time = time.time()
        # Update the fish animation (switch frames every 500ms)
        if current_time - self.last_frame_time > 0.5:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.last_frame_time = current_time

    def draw(self, surface):
        surface.blit(self.frames[self.current_frame_index], self.position)

    def save_as_gif(self, gif_name):
        # Create a list of images for the GIF
        pil_frames = []
        
        for frame in self.frames:
            # Convert each Pygame surface to a byte string in RGBA format
            frame_bytes = pygame.image.tostring(frame, 'RGBA')
            
            # Create a PIL Image from the byte string
            pil_image = Image.frombytes('RGBA', (frame.get_width(), frame.get_height()), frame_bytes)
            
            # Append the PIL Image to the frames list
            pil_frames.append(pil_image)
        
        # Save the frames as a GIF
        pil_frames[0].save(gif_name, save_all=True, append_images=pil_frames[1:], loop=0, duration=500)
        return gif_name


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
                # Remove one fish from the pond (decrement one element)
                fish_animations.pop(0)  # Remove the first fish in the list
                
                # Save the fish as a GIF and send the path of the GIF
                gif_path = fish_animations[0].save_as_gif("fish_animation.gif")
                send_mqtt_message(gif_path)

    # Fill the screen with the background color
    screen.fill(bg_color)

    # Calculate center of the screen for the pond
    pond_center = (screen_width // 2, screen_height // 2)  # Center of screen (600, 400)
    pond_radius = 200

    # Draw the blue circle in the center (pond)
    pygame.draw.circle(screen, circle_color, pond_center, pond_radius)

    # Update and draw the fish (GIFs) inside the pond
    for fish in fish_animations:
        fish.update()
        fish.draw(screen)

    # Draw the "Spawn Picture" button on the left
    button_rect_spawn = pygame.Rect(10, 550, 200, 50)  # Bottom-left corner (10, 550)
    pygame.draw.rect(screen, button_color, button_rect_spawn)
    button_text_spawn = font.render("Spawn Pictures", True, button_text_color)
    screen.blit(button_text_spawn, (button_rect_spawn.x + 10, button_rect_spawn.y + 10))  # Center the text

    # Draw the "Send Message" button on the right
    button_rect_send = pygame.Rect(990, 550, 200, 50)  # Bottom-right corner (990, 550)
    pygame.draw.rect(screen, button_color, button_rect_send)
    button_text_send = font.render("Send Message", True, button_text_color)
    screen.blit(button_text_send, (button_rect_send.x + 10, button_rect_send.y + 10))  # Center the text

    # Update the display
    pygame.display.flip()

   
