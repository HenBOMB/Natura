# import random

class Genes():
    MAX_ENERGY = "energy"
    MAX_HEALTH = "health"
    MAX_SPEED = "speed"
    MAX_SEE_RANGE = "see_range"
    COLOR = "color"
    FOV = "fov"

    def __init__(self, seed: float):
        self.table = {}
        self.table[Genes.MAX_SEE_RANGE] = 5
        self.table[Genes.MAX_ENERGY] = 25
        self.table[Genes.MAX_HEALTH] = 100
        self.table[Genes.MAX_SPEED] = 1
        self.table[Genes.FOV] = 45
        self.table[Genes.COLOR] = (100, 100, 255)
    
    def get(self, key: str) -> float: 
        return self.table[key]

    def set(self, key: str, value):
        self.table[key] = value