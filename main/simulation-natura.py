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

import pygame
import neat

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

from natura import Creature, World, util, Genome, NaturaSimulator
from natura.food import Food
from natura.util import round2, percent, pixel_to_meter
from nndraw import NN
from camera import Camera
from random import randint
from math import radians, sin, cos

SCREEN_WIDTH        = 1600
SCREEN_HEIGHT       = 1000
WORLD_WIDTH         = 1500
WORLD_HEIGHT        = 1500
FPS                 = 30

TEXT_FONT           = pygame.font.SysFont("comicsans", 15)
WORLD               = World(WORLD_WIDTH, WORLD_HEIGHT)
CAMERA              = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
IMAGE_FOOD          = pygame.image.load('./assets/food.png', 'food')

DRAW_NETWORK        = False
DRAW_STATS          = False
DRAW_PROPERTIES     = True
DRAW_SIMULATION     = True
DRAGGING            = False
FOLLOW_CREATURE     = False

COLOR_BACKGROUND    = (0, 0, 16)
COLOR_HIGHLIGHT     = (COLOR_BACKGROUND[0], COLOR_BACKGROUND[1], COLOR_BACKGROUND[2] * 4)
COLOR_WHITE         = (255, 255, 255)

CLICKED_CREATURE    = 0
GENERATION          = 0

def draw_text(txt: str, pos: tuple, color = COLOR_WHITE):
    CAMERA.screen.blit(TEXT_FONT.render(str(txt), True, COLOR_WHITE), pos)

def draw_properties(creature: Creature):
    d = {}
    d["Health"]     = f"{percent(creature.health, creature.max_health)}% / {int(creature.max_health)}"
    d["Energy"]     = f"{percent(creature.energy, creature.max_energy)}% / {round2(creature.max_energy)}"
    d["Speed"]      = f"{percent(creature.speed, creature.max_speed)}% / {round2(creature.GENE_SPEED)}"
    d["Hunger"]     = round2(creature.GENE_HUNGER)
    d["Size"]       = f"{round2(pixel_to_meter(creature.size_px))} / {round2(creature.max_size)}"
    d["Fov"]        = creature.GENE_FOV
    d["View Range"] = creature.GENE_VIEW_RANGE

    spacing = 15
    width, height = (300, len(d)*spacing+spacing/2)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((100, 100, 100, 100))
    CAMERA.screen.blit(surf, (SCREEN_WIDTH - width, 0))

    def draw_txt(txt, i):
        text = TEXT_FONT.render(str(txt), True, COLOR_WHITE)
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width, spacing * i))

    def draw_v_txt(txt, i):
        text = TEXT_FONT.render(str(txt), True, COLOR_WHITE)
        CAMERA.screen.blit(text, (SCREEN_WIDTH - width + 80, spacing * i))
    
    for i, k in enumerate(d):
        draw_txt(k, i)
        draw_v_txt(d[k], i)

def draw_stats(pop_count: int):
    surf = pygame.Surface((200, 85), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    CAMERA.screen.blit(surf, (0, 0))
    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Pop count: {pop_count}", (0, 20))

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
    food: Food
    for food in WORLD.food:
        r = util.meter_to_pixel(food.radius)
        CAMERA.draw_image(IMAGE_FOOD, (food.pos[0] - r / 2, food.pos[1] - r / 2), r)

def draw_static():
    CAMERA.clear_screen()
    draw_text(f"Generation: {GENERATION}", (0, 0))
    draw_text(f"Press 'Enter' to resume viewing the realtime simulation", (0, 20))
    pygame.display.update()

def end_gen(generation: int):
    global GENERATION
    GENERATION  = generation
    if not DRAW_SIMULATION: draw_static()

def tick(population: list):
    global DRAW_NETWORK, DRAW_STATS, DRAW_SIMULATION, GENERATION, DRAGGING, CLICKED_CREATURE, FOLLOW_CREATURE, DRAW_PROPERTIES

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
            elif event.key == pygame.K_t:
                FOLLOW_CREATURE = not FOLLOW_CREATURE

    pop_l = len(population)

    if CLICKED_CREATURE >= pop_l and pop_l != 0: 
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
        if DRAW_PROPERTIES:
            draw_properties(creature)

    if FOLLOW_CREATURE:
        try: CAMERA.set_global_pos(population[CLICKED_CREATURE].pos)
        except: pass

    draw_stats(pop_l)
    CAMERA.tick(FPS)
    return CAMERA.delta

simulator = NaturaSimulator(WORLD)
cp = argutil.get_arg("cp", None)
if cp:
    simulator.load(cp)
else:
    config = neat.Config(
        Genome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        "./neat-config"
    )
    simulator.init(config)
    simulator.spawn_species("uwu", (0, 0), WORLD_WIDTH/2, 1, (255, 255, 100))

GENERATION = simulator.generation

simulator.run(
    tick_function=tick, 
    end_gen_function=end_gen, 
    save_interval=argutil.get_arg("int", 10),
    save_path="./saves/natura-cp-")