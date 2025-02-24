import pygame
import paho.mqtt.client as mqtt
import time
import json
import os
import matplotlib.pyplot as plt
from PIL import Image
from fish import Fish
from utils import *
import random
import math

# Observability Metrics
message_count = 0
valid_message_count = 0
invalid_message_count = 0
fish_types = {}
received_messages = []
message_logs = []  # For storing logs over time
last_update_time = time.time()


def log_observability():
    global message_logs
    print("\n--- Observability Data ---")
    print(f"Total Messages: {message_count}")
    print(f"Valid Messages: {valid_message_count}")
    print(f"Invalid Messages: {invalid_message_count} (Bad Situation if High)")
    print(f"Total Fish in Pond: {len(fish_animations)}")
    print(f"Fish Types in Pond: {fish_types}")
    print("-------------------------\n")
    
    # Store logs
    message_logs.append({
        "time": time.time(),
        "total_messages": message_count,
        "valid_messages": valid_message_count,
        "invalid_messages": invalid_message_count,
        "total_fish": len(fish_animations)
    })

def generate_chart():
    if not message_logs:
        return
    
    times = [log["time"] for log in message_logs]
    total_messages = [log["total_messages"] for log in message_logs]
    valid_messages = [log["valid_messages"] for log in message_logs]
    invalid_messages = [log["invalid_messages"] for log in message_logs]
    total_fish = [log["total_fish"] for log in message_logs]
    
    plt.figure(figsize=(10, 5))
    plt.plot(times, total_messages, label="Total Messages", marker="o")
    plt.plot(times, valid_messages, label="Valid Messages", marker="s")
    plt.plot(times, invalid_messages, label="Invalid Messages", marker="x")
    plt.plot(times, total_fish, label="Total Fish", marker="d")
    
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.legend()
    plt.title("Observability Metrics Over Time")
    plt.grid()
    plt.show()

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
    global message_count, valid_message_count, invalid_message_count
    message_count += 1
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Message received on topic {msg.topic}: {payload}")
        if msg.topic == "user/Parallel":
            if payload['group_name'] == "DC_Universe":
                DC_FRAME = load_gif_frames("./lib/assets/DC_Universe.gif")
                DC_POSITION = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
                fish_animations.append(Fish(DC_FRAME, DC_POSITION, payload['name'], payload['lifetime']))
            elif payload['group_name'] == "NetLink":
                NETLINK_FRAME = load_gif_frames("./lib/assets/NetLink.gif")
                NETLINK_POSITION = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
                fish_animations.append(Fish(NETLINK_FRAME, NETLINK_POSITION, payload['name'], payload['lifetime']))
            elif payload['group_name'] == "Parallel":
                PARALLEL_FRAME = load_gif_frames("./lib/assets/Parallel.gif")
                PARALLEL_POSITION = generate_random_position(pond_center, pond_radius, fish_frames[0].get_rect())
                fish_animations.append(Fish(PARALLEL_FRAME, PARALLEL_POSITION, payload['name'], payload['lifetime']))
        if ("type" in payload and payload["type"] == "hello") or ("group_name" in payload and "name" in payload):
            valid_message_count += 1
            fish_type = payload["group_name"]
            fish_types[fish_type] = fish_types.get(fish_type, 0) + 1
            received_messages.append(payload)
            if len(received_messages) > 10:
                received_messages.pop(0)
        else:
            raise ValueError("Invalid message format")
    except Exception:
        invalid_message_count += 1
        print("[ERROR] Invalid message received!")
        print("Message:", msg.payload)

    log_observability()


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

# Pond parameters
fish_animations = []
last_update_time = time.time()
fish_frames = load_gif_frames("./lib/assets/Parallel.gif")

# Pygame setup
screen_width, screen_height = 1200, 800
pygame.font.init()
font = pygame.font.Font(None, 36)
text_color = (255, 255, 255)  # White text
bg_color = (26, 148, 49)  # Green background
button_color = (0, 128, 0)  # Green button
button_text_color = (255, 255, 255)  # White text for the button
circle_color = (173, 216, 230)  # Blue circle

# Calculate center of the screen for the pond
pond_center = (screen_width // 2, screen_height // 2)  # Center of screen (600, 400)
pond_radius = 200