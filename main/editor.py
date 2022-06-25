if __name__ != '__main__':
    raise ImportError(f"Cannot import module '{__file__}'")

import sys
import pygame

pygame.init()
pygame.font.init()
pygame.display.set_caption("Natura - Life Evolution")

import nndraw
from natura import util
from camera import Camera

SCREEN_WIDTH        = 900
SCREEN_HEIGHT       = 900

TEXT_FONT           = pygame.font.SysFont("comicsans", 15)
CAMERA              = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

COLOR_BACKGROUND    = (0, 0, 16)

input_labels = [
    "Health", 
    "Hunger", 
    "Speed", 
    "Creature angle", 
    "Creature dist", 
    "Creature R--", 
    "Creature -G-", 
    "Creature --B", 
    "Creature count", 
    "Food angle", 
    "Food dist", 
    "Food R--", 
    "Food -G-", 
    "Food --B", 
    "Food count", 
]

output_labels = [
    "Forward", 
    "Back", 
    "Right", 
    "Left", 
    "Look for food / Eat", 
]

inputs = [-i for i in range(1, len(input_labels) + 1)]
hidden = []
outputs = [-i for i in range(1, len(output_labels) + 1)]

connections = []
nodes = []
nodeIdList = []
clicked_node = None
dragging = 0

TOOLBAR_HEIGHT = 100
NEW_HEIGHT = (SCREEN_HEIGHT-TOOLBAR_HEIGHT)

# get the arr with the highest count and use that as a measurement
NODE_RADIUS = NEW_HEIGHT/len(inputs) if len(inputs) > len(outputs) else NEW_HEIGHT/len(outputs) if len(inputs) > len(hidden) else NEW_HEIGHT/len(hidden) if len(hidden) > len(outputs) else NEW_HEIGHT/len(outputs)

for i in range(1, len(inputs)+1):
    nodes.append(nndraw.Node(inputs[i-1], 
        SCREEN_WIDTH/5, 
        NEW_HEIGHT/2+(i-len(inputs)/2)*NODE_RADIUS-NODE_RADIUS/2, 
        0, 
        [nndraw.INPUT_COLOR_1, nndraw.INPUT_COLOR_2], 
        "",
        input_labels[i-1]
    ))
    nodeIdList.append(inputs[i-1])

for i in range(1, len(hidden)+1):
    nodes.append(nndraw.Node(hidden[i-1], 
        SCREEN_WIDTH/2, 
        NEW_HEIGHT/2+(i-len(hidden)/2)*NODE_RADIUS-NODE_RADIUS/2,  
        1, 
        [nndraw.HIDDEN_COLOR_1, nndraw.HIDDEN_COLOR_2], 
    ))
    nodeIdList.append(hidden[i-1])

for i in range(1, len(outputs)+1):
    nodes.append(nndraw.Node(outputs[i-1], 
        SCREEN_WIDTH/1.2, 
        NEW_HEIGHT/2+(i-len(outputs)/2)*NODE_RADIUS-NODE_RADIUS/2,  
        2, 
        [nndraw.OUTPUT_COLOR_1, nndraw.OUTPUT_COLOR_2], 
        "",
        output_labels[i-1]
    ))
    nodeIdList.append(outputs[i-1])

for i, c in enumerate(connections):
    input, output = c
    connections[i] = nndraw.Connection(nodes[nodeIdList.index(input)], nodes[nodeIdList.index(output)], 1)

def get_clicked_node():
    d = NODE_RADIUS / 1.5
    for node in nodes:
        _d = util.dist((node.x, node.y), pygame.mouse.get_pos())
        if _d < d:
            d = _d
            return node
    return None

while True:
    CAMERA.clear_screen((200, 200, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEMOTION and dragging == 0:
            if clicked_node:
                clicked_node.x, clicked_node.y = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            node = nndraw.Node(len(nodeIdList) + 1, 
                pygame.mouse.get_pos()[0], 
                pygame.mouse.get_pos()[1], 
                1, 
                [nndraw.HIDDEN_COLOR_1, nndraw.HIDDEN_COLOR_2], 
            )
            nodes.append(node)
            nodeIdList.append(node.id)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button != 5:
            clicked_node = get_clicked_node()
            dragging = event.button - 1 if clicked_node else 0

        elif event.type == pygame.MOUSEBUTTONUP and event.button != 5:
            dragging = 9
            if event.button == 3:
                node = get_clicked_node()
                if node and clicked_node and node.type != clicked_node.type:
                    connections.append(nndraw.Connection(clicked_node, node, 1))
            clicked_node = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                pass
            elif event.key == pygame.K_s:
                pass
            elif event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_f:
                pass

    surf = pygame.Surface((SCREEN_WIDTH, TOOLBAR_HEIGHT), pygame.SRCALPHA)
    surf.fill((100, 100, 100, 100))
    CAMERA.screen.blit(surf, (0, NEW_HEIGHT))

    if dragging == 2:
        pygame.draw.line(CAMERA.screen, (50, 50, 50), (clicked_node.x, clicked_node.y), pygame.mouse.get_pos(), 1)

    for c in connections: c.drawConnection(CAMERA.screen)
    for n in nodes: n.draw_node(CAMERA.screen)

    if clicked_node:
        pygame.draw.circle(CAMERA.screen, clicked_node.color[0], (clicked_node.x, clicked_node.y), nndraw.NODE_RADIUS+5, 5, False, True, True, False)
        pygame.draw.circle(CAMERA.screen, clicked_node.color[1], (clicked_node.x, clicked_node.y), nndraw.NODE_RADIUS+5, 5, True, False, False, True)
    
    pygame.display.flip()