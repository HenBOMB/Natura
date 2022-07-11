from natura.food import Food
from random import randint, random

class World():
    def __init__(self, width, height, gravity = 9.81):
        self.food = []
        self.width = width
        self.height = height
        self.gravity = gravity

    def tick(self, limit = 1000, chance = .1):
        if len(self.food) >= limit: return
        if random() <= chance: self.spawn_food(1)

    def clear(self):
        self.food = []

    def spawn_food(self, count: int):
        for _ in range(count):
            self.food.append(Food((randint(-self.width+5, self.height-5), randint(-self.width+5, self.height-5))))
    
    def set_food(self, food: Food):
        self.food.append(food)