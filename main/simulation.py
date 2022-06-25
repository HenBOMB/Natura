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
DRAW_SIMULATION     = True
DRAGGING            = False

COLOR_BACKGROUND    = (0, 0, 16)
COLOR_HIGHLIGHT     = (COLOR_BACKGROUND[0], COLOR_BACKGROUND[1], COLOR_BACKGROUND[2] * 4)
COLOR_WHITE         = (255, 255, 255)

CLICKED_CREATURE    = 0
GENERATION          = 0
MAX_FITNESS         = 0
AVR_FITNESS         = []

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
    l = len(AVR_FITNESS)
    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Max Fitness: {MAX_FITNESS}", (0, 20))
    draw_text(f"Avr Fitness: {sum(AVR_FITNESS)/l if l != 0 else 0}", (0, 40))
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
    l = len(AVR_FITNESS)
    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Max Fitness: {MAX_FITNESS}", (0, 20))
    draw_text(f"Avr Fitness: {(sum(AVR_FITNESS)/len(AVR_FITNESS) if l > 0 else 0)}", (0, 40))
    draw_text(f"Press 'Enter' to resume viewing the realtime simulation", (0, 80))
    pygame.display.update()

def end_gen(generation: int, best_genome: Genome):
    global GENERATION, MAX_FITNESS
    MAX_FITNESS = best_genome.fitness
    AVR_FITNESS.append(MAX_FITNESS)
    if len(AVR_FITNESS) == 5: AVR_FITNESS.pop(0)
    GENERATION  = generation
    if not DRAW_SIMULATION: draw_static()

def tick(population: list):
    global DRAW_NETWORK, DRAW_STATS, DRAW_SIMULATION, GENERATION, DRAGGING, CLICKED_CREATURE

    if not DRAW_SIMULATION: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.WINDOWMINIMIZED:
                print("WARNING! Simulation Paused due to pygame enabled and window minimized")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                DRAW_SIMULATION = not DRAW_SIMULATION
        return

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.WINDOWMINIMIZED:
            print("WARNING! Simulation Paused due to pygame enabled and window minimized")

        elif event.type == pygame.MOUSEWHEEL:
            CAMERA.zoom(-event.y)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            DRAGGING = True
            CAMERA.set_pos(pygame.mouse.get_pos())

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            DRAGGING = False
            creature: Creature

            for i, creature in enumerate(population):
                d = util.dist(CAMERA.fix_pos(creature.pos), pygame.mouse.get_pos())
                if d < CAMERA.fix_scale(creature.size_px*2):
                    CLICKED_CREATURE = i
                    break

        elif event.type == pygame.MOUSEMOTION and DRAGGING:
            if util.dist(CAMERA.cam_pos, pygame.mouse.get_pos()) > 5:
                CAMERA.pan_camera(pygame.mouse.get_pos())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                DRAW_NETWORK = not DRAW_NETWORK
            elif event.key == pygame.K_s:
                DRAW_STATS = not DRAW_STATS
            elif event.key == pygame.K_RETURN:
                DRAW_SIMULATION = not DRAW_SIMULATION
                draw_static()
                return
            elif event.key == pygame.K_f:
                try: CAMERA.set_global_pos(population[CLICKED_CREATURE].pos)
                except: pass

    pop_l = len(population)

    if CLICKED_CREATURE >= pop_l: 
        CLICKED_CREATURE = randint(0, pop_l-1)

    CAMERA.clear_screen()
    CAMERA.draw_rect(COLOR_BACKGROUND, (-WORLD_WIDTH, -WORLD_HEIGHT, WORLD_WIDTH*2, WORLD_HEIGHT*2))
    draw_world()

    for i, creature in enumerate(population):
        if i != CLICKED_CREATURE: 
            draw_creature(creature)
            continue

        draw_creature(creature, True)
        if DRAW_NETWORK:
            nndraw = NN(creature.config, creature.genome, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
            nndraw.update_inputs(["" for i in range(0, 15)])
            nndraw.update_outputs(["" for i in range(0, 5)])
            nndraw.draw(CAMERA.screen)
        if DRAW_STATS:
            draw_properties(creature)

    draw_stats(pop_l)
    CAMERA.tick(FPS)
    return CAMERA.delta

simulator = Simulator(WORLD, tick, end_gen)

cp = argutil.get_arg("cp", None)
if cp: simulator.load(cp)

simulator.start(argutil.get_arg("int", 30))

GENERATION = simulator.pop.generation