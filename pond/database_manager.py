import time
import pygame
from PIL import Image

import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import time

import os

# Database configuration using environment variables
DB_CONFIG = {
    'dbname': os.environ.get('POSTGRES_DB', 'pond_db'),
    'user': os.environ.get('POSTGRES_USER', 'user'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'password'),
    'host': os.environ.get('POSTGRES_HOST', 'postgres'),  # Changed from localhost to postgres service name
    'port': '5432'
}
class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fish (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    x_position FLOAT NOT NULL,
                    y_position FLOAT NOT NULL,
                    creation_time TIMESTAMP NOT NULL,
                    lifetime INTEGER NOT NULL,
                    current_frame_index INTEGER DEFAULT 0
                )
            """)
            self.conn.commit()

    def add_fish(self, fish):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO fish (name, x_position, y_position, creation_time, lifetime, current_frame_index)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                fish.name,
                fish.position[0],
                fish.position[1],
                datetime.fromtimestamp(time.time()),
                fish.remainingLifetime,
                fish.current_frame_index
            ))
            fish_id = cur.fetchone()[0]
            self.conn.commit()
            return fish_id

    def remove_fish(self, fish_name):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM fish WHERE name = %s", (fish_name,))
            self.conn.commit()

    def get_all_fish(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM fish")
            return cur.fetchall()

    def update_fish_position(self, fish_name, x, y):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE fish 
                SET x_position = %s, y_position = %s 
                WHERE name = %s
            """, (x, y, fish_name))
            self.conn.commit()

    def update_fish_frame(self, fish_name, frame_index):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE fish 
                SET current_frame_index = %s 
                WHERE name = %s
            """, (frame_index, fish_name))
            self.conn.commit()

    def close(self):
        self.conn.close()

class Fish:
    def __init__(self, frames, position, db_manager, id=None, lifetime=20):
        self.frames = frames
        self.position = position
        self.current_frame_index = 0
        self.last_frame_time = time.time()
        self.remainingLifetime = lifetime
        self.db_manager = db_manager
        
        if not id:
            self.name = "Parallel_" + str(time.time())
        else:
            self.name = id
            
        # Store the fish in the database
        self.db_id = self.db_manager.add_fish(self)

    def update(self):
        current_time = time.time()
        if current_time - self.last_frame_time > 0.1:  # Animation speed
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.last_frame_time = current_time
            self.db_manager.update_fish_frame(self.name, self.current_frame_index)
            
            # Update lifetime
            self.remainingLifetime -= 0.1
            if self.remainingLifetime <= 0:
                self.db_manager.remove_fish(self.name)
                return False
        return True

    def draw(self, screen):
        current_frame = self.frames[self.current_frame_index]
        screen.blit(current_frame, self.position)

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
