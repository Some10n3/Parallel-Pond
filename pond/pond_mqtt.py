import paho.mqtt.client as mqtt
import redis
import os

# MQTT Broker Configuration
BROKER = "40.90.169.126"
PORT = 1883
USERNAME = "dc24"
PASSWORD = "kmitl-dc24"
TOPIC = "fishhaven/stream"

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    message_data = msg.payload.decode()
    print(f"Received message: {message_data}")

    # Store message in Redis
    redis_client.lpush("pond_messages", message_data)

    # Publish message to Redis Pub/Sub channel
    redis_client.publish("pond_channel", message_data)

# Initialize MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)

# Start Listening
client.loop_forever()
