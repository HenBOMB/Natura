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
import drawutil

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

from natura import Creature, World, util, NaturaNeatSimulator
from nndraw import NN
from camera import Camera
from random import randint

SCREEN_WIDTH        = 1600
SCREEN_HEIGHT       = 1000
WORLD_WIDTH         = 1500
WORLD_HEIGHT        = 1500
FPS                 = 30

TEXT_FONT           = pygame.font.SysFont("comicsans", 15)
WORLD               = World(WORLD_WIDTH, WORLD_HEIGHT)
CAMERA              = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
IMAGE_FOOD          = pygame.image.load('./assets/food.png', 'food')
IMAGE_EGG           = pygame.image.load('./assets/egg.png', 'food')

DRAW_NETWORK        = True
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
draw                = drawutil.DrawUtil(CAMERA, WORLD)

def draw_stats(pop_count: int):
    surf = pygame.Surface((200, 85), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    CAMERA.screen.blit(surf, (0, 0))
    draw.text(f"Generation: {GENERATION}", (0, 0))
    draw.text(f"Pop count: {pop_count}", (0, 20))

def draw_static():
    CAMERA.clear_screen()
    draw.text(f"Generation: {GENERATION}", (0, 0))
    draw.text(f"Press 'Enter' to resume viewing the realtime simulation", (0, 20))
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
    draw.world()

    for i, creature in enumerate(population):
        if i != CLICKED_CREATURE: 
            draw.creature(creature)
            continue

        draw.creature(creature, True)
        if DRAW_NETWORK:
            nndraw = NN(creature.config, creature.genome, (50, SCREEN_HEIGHT/2), SCREEN_HEIGHT)
            nndraw.update_inputs(["" for i in range(0, 15)])
            nndraw.update_outputs(["" for i in range(0, 5)])
            nndraw.draw(CAMERA.screen)
        if DRAW_PROPERTIES:
            draw.creature_properties(creature)

    if FOLLOW_CREATURE:
        try: CAMERA.set_global_pos(population[CLICKED_CREATURE].pos)
        except: pass

    draw_stats(pop_l)
    CAMERA.tick(FPS)
    return CAMERA.delta

simulator = NaturaNeatSimulator(WORLD)

# simulator = NaturaSimulator(WORLD)
cp = argutil.get_arg("cp", None)

if cp:
    # simulator.load(cp)
    simulator.load_checkpoint(cp)
# else:
#     config = neat.Config(
#         Genome, neat.DefaultReproduction,
#         neat.DefaultSpeciesSet, neat.DefaultStagnation,
#         "./neat-config"
#     )
#     simulator.init(config)
#     simulator.spawn_species("uwu", (0, 0), WORLD_WIDTH/2, 50, (255, 255, 100))

simulator.run(argutil.get_arg("int", 10), None, tick, end_gen)

GENERATION = simulator.pop.generation

# simulator.run(
#     tick_function=tick, 
#     end_gen_function=end_gen, 
#     save_interval=argutil.get_arg("int", 10),
#     save_path="./saves/natura-cp-")