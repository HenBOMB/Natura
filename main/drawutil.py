import natura
import pygame

from natura.util import percent, round2, sub_vec
from natura.food import Food
from math import radians, sin, cos

IMAGE_FOOD  = pygame.image.load('./assets/plant.png', 'food')
IMAGE_EGG   = pygame.image.load('./assets/egg.png', 'food')

COLOR_WHITE = (255,255,255)

class DrawUtil(object):
    def __init__(self, camera, world):
        self.camera = camera
        self.w = world

    def creature(self, c: natura.Creature):
        if c.is_baby():
            self.camera.draw_image(IMAGE_EGG, sub_vec(c.pos, (c.size/2, c.size/2)), c.size*2)
        else:
            r = c.size
            self.camera.draw_circle(c.GENE_COLOR, c.pos, r)
            rad = radians(c.GENE_FOV/1.5)

            self.camera.draw_circle((0,0,0), (
                    c.pos[0] + cos(c.angle-rad) * r, 
                    c.pos[1] + sin(c.angle-rad) * r), r / 4)

            self.camera.draw_circle((0,0,0), (
                    c.pos[0] + cos(c.angle+rad) * r, 
                    c.pos[1] + sin(c.angle+rad) * r), r / 4)

    def creature_highlight(self, c: natura.Creature):
        if c.is_baby():
            self.camera.draw_circle((200, 200, 200), c.pos, c.size+1, 1)
        else:
            self.camera.draw_circle((200, 200, 200), c.pos, c.size+5, 1)

    def creature_properties(self, creature: natura.Creature):
        font = pygame.font.SysFont("comicsans", 15)

        d = {}
        d["Health"]     = f"{percent(creature.health, creature.max_health)}% - {int(creature.health)} / {int(creature.max_health)}"
        d["Energy"]     = f"{percent(creature.energy, creature.max_energy)}% - {round2(creature.energy)} / {round2(creature.max_energy)}"
        d["Speed"]      = f"{percent(creature.speed, creature.max_speed)}% - {round2(creature.speed)} {round2(creature.GENE_SPEED)}"
        d["Hunger"]     = round2(creature.GENE_HUNGER)
        d["Size"]       = f"{round2(creature.size)} - {round2(creature.min_size)} / {round2(creature.max_size)} meters"
        d["Fov"]        = creature.GENE_FOV
        d["View Range"] = creature.GENE_VIEW_RANGE
        d["Age"]        = f"{percent(creature.maturity, creature.GEN_MATURITY_LENGTH)} - {round2(creature.GEN_MATURITY_LENGTH)}"
        m = creature.GEN_MATURITY_LENGTH * creature.GEN_BABY_MATURITY_LENGTH
        d["Baby Age"]   = f"{percent(min(creature.maturity, m), m)} - {round2(m)}"
        d["Focus"]      = f"{round2(percent(creature.focus, 1))}"
        d["Cons."]      = f"{creature.consumption} e/s"

        spacing = 15
        width, height = (500, len(d)*spacing+spacing/2)
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((100, 100, 100, 100))
        self.camera.screen.blit(surf, (self.camera.screen_width - width, 0))

        def draw_txt(txt, i):
            text = font.render(str(txt), True, COLOR_WHITE)
            self.camera.screen.blit(text, (self.camera.screen_width - width, spacing * i))

        def draw_v_txt(txt, i):
            text = font.render(str(txt), True, (COLOR_WHITE))
            self.camera.screen.blit(text, (self.camera.screen_width - width + 80, spacing * i))
        
        for i, k in enumerate(d):
            draw_txt(k, i)
            draw_v_txt(d[k], i)

    def world(self):
        food: Food
        for food in self.w.food:
            self.camera.draw_circle(food.color, (food.pos[0] - food.radius / 2, food.pos[1] - food.radius / 2), food.radius)
            # self.camera.draw_image(IMAGE_FOOD, (food.pos[0] - r / 2, food.pos[1] - r / 2), r * 2)

    def text(self, txt: str, pos: tuple, color = COLOR_WHITE, font = None):
        font = font or pygame.font.SysFont("comicsans", 15)
        self.camera.screen.blit(font.render(str(txt), True, color), pos)
