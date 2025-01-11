import paho.mqtt.client as mqtt
import time
import json

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

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        # Publish the "hello" message
        client.publish(TOPIC, json.dumps(HELLO_MESSAGE))
        print("Published message:", HELLO_MESSAGE)
    else:
        print("Failed to connect, return code %d\n", rc)

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")

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

# Keep the script running to allow asynchronous operations
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting from broker...")
    client.loop_stop()
    client.disconnect()