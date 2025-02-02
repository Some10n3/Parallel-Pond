import pygame
import time
from PIL import Image
import random
import math
import json


with open('MQTT.json', 'r') as config_file:
    config = json.load(config_file)

BROKER = config['BROKER']
PORT = config['PORT']
USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']
TOPIC = config['TOPIC']


# topic for sending to other group
DC_UNIVERSE = "user/DC_Universe"
NETLINK = "user/NetLink"

# To hold the latest received messages
received_messages = [] 

# Pygame setup
screen_width, screen_height = 1200, 800
pygame.font.init()
font = pygame.font.Font(None, 36)
text_color = (255, 255, 255)  # White text
bg_color = (26, 148, 49)  # Green background
button_color = (0, 128, 0)  # Green button
button_text_color = (255, 255, 255)  # White text for the button
circle_color = (173, 216, 230)  # Blue circle


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

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        HELLO_MESSAGE = {
            "type": "hello",
            "sender": "Parallel",
            "timestamp": int(time.time()),
            "data": {}
        }
        client.publish(TOPIC, json.dumps(HELLO_MESSAGE))
        print("Published message:", HELLO_MESSAGE)
    else:
        print("Failed to connect, return code %d\n", rc)

# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message received on topic {msg.topic}: {message}")
    if msg.topic == "user/Parallel":
        if message.group_name == "DC_Universe":
            DC_FRAME = load_gif_frames("./lib/assets/DC_Universe.gif")
            DC_POSITION = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
            fish_animations.append(Fish(DC_FRAME, DC_POSITION, message.name))
        elif message.group_name == "NetLink":
            NETLINK_FRAME = load_gif_frames("./lib/assets/NetLink.gif")
            NETLINK_POSITION = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
            fish_animations.append(Fish(NETLINK_FRAME, NETLINK_POSITION, message.name))

    # Add received message to the list
    received_messages.append(message)
    if len(received_messages) > 10:  # Keep only the latest 10 messages
        received_messages.pop(0)

def send_fish_to_topicX(client, topicX, fishName, remainingLifetime):
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