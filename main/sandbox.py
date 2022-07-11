if __name__ != '__main__':
    raise ImportError(f"Cannot import module '{__file__}'")

import sys
import pygame
import natura
import neat
import drawutil

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

from camera import Camera

SCREEN_WIDTH    = 900
SCREEN_HEIGHT   = 900
TEXT_FONT       = pygame.font.SysFont("comicsans", 15)
CAMERA          = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
WORLD           = natura.World(SCREEN_WIDTH, SCREEN_HEIGHT)
POPULATION      = []
draw            = drawutil.DrawUtil(CAMERA, WORLD)

WORLD.spawn_food(250)

config = neat.Config(
    natura.Genome, neat.DefaultReproduction,
    neat.DefaultSpeciesSet, neat.DefaultStagnation,
    "./neat-config"
)

while True:
    CAMERA.clear_screen((200, 200, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
            genome = natura.Genome(0)
            c = natura.Creature(genome, config, (0, 0), WORLD, True)
            POPULATION.append(c)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pass

    draw.world()

    creature: natura.Creature
    for i, creature in enumerate(POPULATION):
        creature.tick(CAMERA.delta, POPULATION)
        
        if creature.dead: 
            POPULATION.pop(i)
            continue

        draw.creature(creature, False)
        draw.creature_properties(creature)

    CAMERA.tick(30)