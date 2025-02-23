import time
import pygame
import psycopg2
import json
from PIL import Image
import base64

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "127.0.0.1",  # Try this instead of "localhost"
    "port": 5432
}

def update_all_fish_in_db(fish_animations):
    """ Update all fish in the database """
    for fish in fish_animations:
        fish.save_to_db()

def get_fish_from_db():
    """ Load all fish from the database """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM fish;")
        fish_ids = cur.fetchall()
        
        fish_animations = []
        for fish_id in fish_ids:
            fish = Fish.load_from_db(fish_id)
            if fish:
                fish_animations.append(fish)
        
        cur.close()
        conn.close()
        return fish_animations
    except Exception as e:
        print(f"Error getting fish from database: {e}")
    return []

class Fish:
    def __init__(self, frames, position, id=None, lifetime=20):
        self.id = id
        self.name = f"Parallel_{time.time()}" if not id else id
        self.frames = frames
        self.position = position
        self.current_frame_index = 0
        self.last_frame_time = time.time()
        self.remainingLifetime = lifetime

    def update(self):
        current_time = time.time()
        if current_time - self.last_frame_time > 0.5:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.remainingLifetime -= (current_time - self.last_frame_time)
            self.last_frame_time = current_time
            print(f"{self.name}'s remaining lifetime : {self.remainingLifetime}")
            return self.remainingLifetime > 0
        return True

    def draw(self, surface):
        surface.blit(self.frames[self.current_frame_index], self.position)

    def save_to_db(self):
        """ Save the fish instance to PostgreSQL """
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            frames_data = json.dumps([base64.b64encode(pygame.image.tostring(frame, 'RGBA')).decode('utf-8') for frame in self.frames])

            cur.execute("""
                INSERT INTO fish (name, position_x, position_y, remaining_lifetime, frames) 
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """, (self.name, self.position[0], self.position[1], self.remainingLifetime, frames_data))

            self.id = cur.fetchone()[0]
            conn.commit()
            print(f"Fish {self.name} saved to database with id {self.id}")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error saving fish to database: {e}")


    @classmethod
    def load_from_db(cls, fish_id):
        """ Load a fish instance from PostgreSQL """
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            cur.execute("SELECT name, position_x, position_y, remaining_lifetime, frames FROM fish WHERE id = %s;", (fish_id,))
            result = cur.fetchone()
            
            if result:
                name, x, y, lifetime, frames_data = result
                frames = [pygame.image.fromstring(bytes(frame), (64, 64), 'RGBA') for frame in json.loads(frames_data)]
                fish = cls(frames, (x, y), id=name, lifetime=lifetime)
                return fish
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error loading fish from database: {e}")
        return None
