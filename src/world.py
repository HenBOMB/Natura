import random
from camera import Camera

from food import *

WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000

GRAVITY = 9.81

# 1 pixel = 0.01 meters
# 100 pixels = 1 meter
def pixel_to_meter(pixels):
    return pixels / 100

def meter_to_pixel(meter):
    return meter * 100

class World():
    def __init__(self, seed: float):
        self.food = []
        self.seed = seed
        self.image_food = None

    def tick(self):
        chance = 0.1
        limit = 400

        if len(self.food) >= limit: return

        if random.random() <= chance:
            self.seed = random.randint(0, 1000000)
            self.spawn_food(1)

    def draw(self, camera: Camera):
        for i, food in enumerate(self.food):
            if food.energy == 0:
                self.food.pop(i)
                continue

            camera.draw_image(self.image_food, (food.pos[0] - food.size / 2, food.pos[1] - food.size / 2), food.size * 2.5)

    def spawn_food(self, count: int):
        for i in range(count):
            seed = i + (self.seed+1) * 461
            random.seed(seed+100)
            x = random.randint(-WORLD_HEIGHT/2+5, WORLD_HEIGHT/2-5)
            random.seed(seed+200)
            y = random.randint(-WORLD_HEIGHT/2+5, WORLD_HEIGHT/2-5)
            food = Food((x, y))
            food.energize(seed+300)
            self.food.append(food)
    
    def set_food(self, food: Food):
        self.food.append(food)