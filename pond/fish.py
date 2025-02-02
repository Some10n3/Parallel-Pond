import time
import pygame
from PIL import Image

# Fish class to hold the fish GIF animation
class Fish:
    def __init__(self, frames, position, id=None):
        if not id:
            self.name = "Parallel_" + str(time.time())
        else:
            self.name = id
        self.frames = frames
        self.position = position
        self.current_frame_index = 0
        self.last_frame_time = time.time()
        self.remainingLifetime = 20

    def update(self):
        current_time = time.time()
        # print(self.remainingLifetime)
        # Update the fish animation (switch frames every 500ms)
        if current_time - self.last_frame_time > 0.5:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.remainingLifetime -= (current_time - self.last_frame_time)
            self.last_frame_time = current_time
            print(f"{self.name}'s remaining lifetime : {self.remainingLifetime}")
            return True
        if self.remainingLifetime <= 0:
            return False
        return True

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
