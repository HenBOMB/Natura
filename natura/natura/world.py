from natura.food import Food
from random import randint, random

class World():
    def __init__(self, width, height):
        self.food = []
        self.image_food = None
        self.width = width
        self.height = height

    def tick(self):
        chance = 0.1
        limit = 300

        if len(self.food) >= limit: return

        if random() <= chance:
            self.spawn_food(1)

    def clear(self):
        self.food = []

    def spawn_food(self, count: int):
        for i in range(count):
            x = randint(-self.width+5, self.height-5)
            y = randint(-self.width+5, self.height-5)
            food = Food((x, y))
            food.energize()
            self.food.append(food)
    
    def set_food(self, food: Food):
        self.food.append(food)