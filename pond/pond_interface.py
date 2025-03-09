import pygame
import paho.mqtt.client as mqtt
import time
from fish import *

# Pygame setup
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1200, 800))  # Screen size
pygame.display.set_caption("Parallel Pond")

# MQTT Configuration
BROKER = "40.90.169.126"
PORT = 1883
USERNAME = "dc24"
PASSWORD = "kmitl-dc24"
TOPIC = "P2P(Parallel2Parallel)"

# Create MQTT Client
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:  # Press 'T' to send fish data
                message = f"Fish spawned at {time.time()}"
                client.publish(TOPIC, message)
                print(f"Sent message: {message}")

    screen.fill((0, 100, 200))  # Blue background
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client.disconnect()
