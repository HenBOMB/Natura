import random

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
    def __init__(self, seed: float, SCREEN_WIDTH: int =WORLD_WIDTH, SCREEN_HEIGHT: int=WORLD_HEIGHT):
        self.food = []
        self.seed = seed
        self.click = (0, 0)
        self.offset_x = SCREEN_WIDTH / 2
        self.offset_y = SCREEN_HEIGHT / 2
        self.click_offset_x = 0
        self.click_offset_y = 0

        #draw only
        self.image_food = None

    def tick(self):
        chance = 0.1
        limit = 400

        if len(self.food) >= limit: return

        if random.random() <= chance:
            self.seed = random.randint(0, 1000000)
            self.spawn_food(1)

    def draw(self, SCREEN, pygame):
        if self.image_food == None:
            self.image_food = pygame.image.load('./assets/food.png', 'food')

        for i, food in enumerate(self.food):
            if food.energy == 0:
                self.food.pop(i)
                continue
            # pygame.draw.circle(SCREEN, food.color, (food.pos[0] + self.offset_x, food.pos[1] + self.offset_y), food.size)
            s = food.size * 2.5
            SCREEN.blit(
                pygame.transform.scale(self.image_food, (s, s)), 
                (food.pos[0] + self.offset_x - s/2, food.pos[1] + self.offset_y - s/2)
            )

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

    def set_click(self, pos: tuple):
        self.click = pos
        self.click_offset_x = self.offset_x
        self.click_offset_y = self.offset_y

    def pan_camera(self, pos: tuple):
        self.offset_x = self.click_offset_x + (pos[0] - self.click[0])
        self.offset_y = self.click_offset_y + (pos[1] - self.click[1])