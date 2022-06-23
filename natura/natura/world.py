from natura.food import Food
from random import randint, random, seed

class World():
    def __init__(self, width, height, seed: float = random() * 100000):
        self.food = []
        self.seed = seed
        self.image_food = None
        self.width = width
        self.height = height

    def tick(self):
        chance = 0.1
        limit = 400

        if len(self.food) >= limit: return

        if random() <= chance:
            self.seed = randint(0, 1000000)
            self.spawn_food(1)

    def spawn_food(self, count: int):
        for i in range(count):
            s = i + (self.seed+1) * 461
            seed(s+100)
            x = randint(-self.width/2+5, self.height/2-5)
            seed(s+200)
            y = randint(-self.width/2+5, self.height/2-5)
            food = Food((x, y))
            food.energize(s+300)
            self.food.append(food)
    
    def set_food(self, food: Food):
        self.food.append(food)