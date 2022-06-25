if __name__ != '__main__':
    raise ImportError(f"Cannot import module '{__file__}'")

import argutil
import sys

if argutil.has_arg("help"):
    print("Load the simulation from a checkpoint")
    print("--cp [path]")
    print("Maximum number of generations between save intervals")
    print("--int [int]")
    sys.exit()

import neat
import pygame
import pickle

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

from natura import Creature, World, util, Genome, Simulator
from nndraw import NN
from camera import Camera
from random import randint, uniform, random
from math   import radians, sin, cos

SCREEN_WIDTH        = 1600
SCREEN_HEIGHT       = 1000
WORLD_WIDTH         = 1500
WORLD_HEIGHT        = 1500
FPS                 = 60

TEXT_FONT           = pygame.font.SysFont("comicsans", 15)
WORLD               = World(WORLD_WIDTH, WORLD_HEIGHT)
CAMERA              = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
IMAGE_FOOD          = pygame.image.load('./assets/food.png', 'food')

DRAW_NETWORK        = False
DRAW_STATS          = False
QUIT                = False
ONLY_SIMULATE       = False

COLOR_BACKGROUND    = (0, 0, 16)
COLOR_HIGHLIGHT     = (COLOR_BACKGROUND[0], COLOR_BACKGROUND[1], COLOR_BACKGROUND[2] * 4)
COLOR_WHITE         = (255, 255, 255)

# Statistics
GENERATION = 0
MAX_FITNESS = 0
MAX_FITNESS_ARR = [0]

def draw_text(txt: str, pos: tuple, color = COLOR_WHITE):
    CAMERA.screen.blit(TEXT_FONT.render(str(txt), True, COLOR_WHITE), pos)

def draw_properties(creature: Creature):
    width, height = (300, 100)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((100, 100, 100, 100))
    CAMERA.screen.blit(surf, (SCREEN_WIDTH - width, 0))

    def draw_txt(txt, i):
        text = TEXT_FONT.render(str(txt), True, COLOR_WHITE)
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width, 7.5 * 2 * i))

    def draw_v_txt(txt, i):
        text = TEXT_FONT.render(str(txt), True, COLOR_WHITE)
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width + 80, 7.5 * 2 * i))

    draw_txt("Fov", 0)
    draw_v_txt(creature.GENE_FOV, 0)
    draw_txt("Energy", 1)
    draw_v_txt(f"{util.percent(creature.energy, creature.GENE_ENERGY)}% / {creature.GENE_ENERGY}", 1)
    draw_txt("Health", 2)
    draw_v_txt(f"{util.percent(creature.health, creature.GENE_HEALTH)}% / {creature.GENE_HEALTH}", 2)
    draw_txt("Speed", 3)
    draw_v_txt(creature.GENE_SPEED, 3)
    draw_txt("View Range", 4)
    draw_v_txt(creature.GENE_VIEW_RANGE, 4)
    draw_txt("Hunger", 5)
    draw_v_txt(creature.GENE_HUNGER, 5)

def draw_stats(pop_count: int):
    surf = pygame.Surface((200, 85), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    CAMERA.screen.blit(surf, (0, 0))

    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Max Fitness: {MAX_FITNESS_ARR[len(MAX_FITNESS_ARR)-1]}", (0, 20))
    draw_text(f"Avr Fitness: {sum(MAX_FITNESS_ARR)/len(MAX_FITNESS_ARR)}", (0, 40))
    draw_text(f"Pop count: {pop_count}", (0, 60))

def draw_creature(c: Creature, highlight: bool = False):
    CAMERA.draw_circle(c.GENE_COLOR, c.pos, c.size_px)
    rad = radians(c.GENE_FOV/1.5)
    CAMERA.draw_circle((0,0,0), (
            c.pos[0] + cos(c.angle-rad) * c.size_px, 
            c.pos[1] + sin(c.angle-rad) * c.size_px), c.size_px / 4)
    CAMERA.draw_circle((0,0,0), (
            c.pos[0] + cos(c.angle+rad) * c.size_px, 
            c.pos[1] + sin(c.angle+rad) * c.size_px), c.size_px / 4)

    if highlight:
        CAMERA.draw_circle((200, 200, 200), c.pos, c.size_px+5, 1)

def draw_world():
    for i, food in enumerate(WORLD.food):
        CAMERA.draw_image(IMAGE_FOOD, (food.pos[0] - food.size / 2, food.pos[1] - food.size / 2), food.size * 2.5)

def draw_static():
    CAMERA.clear_screen()
    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Max Fitness: {MAX_FITNESS_ARR[len(MAX_FITNESS_ARR)-1]}", (0, 20))
    draw_text(f"Avr Fitness: {sum(MAX_FITNESS_ARR)/len(MAX_FITNESS_ARR)}", (0, 40))
    draw_text(f"Press 'Enter' to resume viewing the realtime simulation", (0, 80))
    pygame.display.update()

# could implement parallelism into this to speed it up, obviously not drawing anything, but like before!
# https://github.com/HenBOMB/Natura/commit/e10530add790470874891472f48d0c5bee916e23#diff-852f425cb274d4895ce21fa82f7075101cc8e8bcd94d000838c57fc5241afa5a

def tick(population: list):
    CAMERA.clear_screen()
    CAMERA.draw_rect(COLOR_BACKGROUND, (-WORLD_WIDTH, -WORLD_HEIGHT, WORLD_WIDTH*2, WORLD_HEIGHT*2))
    draw_world()
    for creature in population: draw_creature(creature)
    CAMERA.tick(FPS)
    return CAMERA.delta

simulator = Simulator(WORLD, tick)
simulator.load('./saves/gen-719')
simulator.start()