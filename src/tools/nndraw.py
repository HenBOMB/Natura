import pygame

NODE_RADIUS     =   20
NODE_SPACING    =   5
LAYER_SPACING   =   15
INPUT_NEURONS   =   7
OUTPUT_NEURONS  =   6
CONN_WIDTH      =   1

WHITE           =   (255, 255, 255)
GRAY            =   (200, 200, 200)
BLACK           =   (0, 0, 0)

INPUT_COLOR_1 = (100, 175, 50)
INPUT_COLOR_2 = (73, 135, 30)

OUTPUT_COLOR_1 = (100, 175, 50)
OUTPUT_COLOR_2 = (70, 135, 30)

HIDDEN_COLOR_1 = (100, 175, 237)
HIDDEN_COLOR_2 = (80, 160, 235)

HIDDEN_COLOR_3 = (200, 60, 60)
HIDDEN_COLOR_4 = (135, 40, 40)

NODE_FONT = pygame.font.SysFont("comicsans", 9)

class NN:

    def __init__(self, config, genome, pos, SCREEN_HEIGHT):
        self.nodes = []
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.genome = genome
        self.pos = (int(pos[0]+NODE_RADIUS), int(pos[1]))
        input_names = range(INPUT_NEURONS)
        output_names = range(OUTPUT_NEURONS)
        middle_nodes = [n for n in genome.nodes.keys()]
        nodeIdList = []

        #nodes
        h = (INPUT_NEURONS-1)*(NODE_RADIUS*2 + NODE_SPACING)

        for i, input in enumerate(config.genome_config.input_keys):
            n = Node(
                input, 
                pos[0], 
                pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), 
                0, 
                [INPUT_COLOR_1, INPUT_COLOR_2], 
                input_names[i], 
                i)
            self.nodes.append(n)
            nodeIdList.append(input)

        h = (OUTPUT_NEURONS-1)*(NODE_RADIUS*2 + NODE_SPACING)
        for i,out in enumerate(config.genome_config.output_keys):
            n = Node(
                out+INPUT_NEURONS, 
                self.pos[0] + 2*(LAYER_SPACING*1.5+2*NODE_RADIUS), 
                self.pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), 
                2, 
                [OUTPUT_COLOR_1, OUTPUT_COLOR_2], 
                output_names[i], 
                i)

            self.nodes.append(n)
            middle_nodes.remove(out)
            nodeIdList.append(out)

        h = (len(middle_nodes)-1)*(NODE_RADIUS*2 + NODE_SPACING)
        for i, m in enumerate(middle_nodes):
            n = Node(
                m, 
                self.pos[0] + (LAYER_SPACING+2*NODE_RADIUS), 
                self.pos[1] + int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), 
                1, 
                [HIDDEN_COLOR_1, HIDDEN_COLOR_2])

            self.nodes.append(n)
            nodeIdList.append(m)

        self.connections = []
        self.offset_end = 0
        for c in genome.connections.values():
            if c.enabled:
                input, output = c.key
                # if input > INPUT_NEURONS and output > INPUT_NEURONS:
                #     self.nodes[nodeIdList.index(input)].x += LAYER_SPACING * 2
                #     self.offset_end += LAYER_SPACING
                #     self.nodes[nodeIdList.index(input)].color = [HIDDEN_COLOR_3, HIDDEN_COLOR_4]

                # if input > OUTPUT_NEURONS:
                #     self.nodes[nodeIdList.index(input)].connection_count += 1
                #     self.nodes[nodeIdList.index(input)].x += NODE_RADIUS
                    
                # if output > OUTPUT_NEURONS:
                #     self.nodes[nodeIdList.index(output)].connection_count += 1
                #     self.nodes[nodeIdList.index(output)].x += NODE_RADIUS

                self.connections.append(Connection(self.nodes[nodeIdList.index(input)],self.nodes[nodeIdList.index(output)], c.weight))

        for i in range(len(self.nodes)):
            if self.nodes[i].type == 2 and self.nodes[i].connection_count > 0:
                self.nodes[i].x += self.offset_end

        # self.new_nodes = []

        # for i, node in enumerate(config.genome_config.input_keys):
        #     self.new_nodes.append([])

    def update_inputs(self, input_names):
        for i, l in enumerate(input_names):
            self.nodes[i].label = l
    
    def update_outputs(self, output_names):
        for i, l in enumerate(output_names):
            self.nodes[i+INPUT_NEURONS].label = l

    def draw(self, screen):
        pygame.draw.rect(screen, (250, 244, 225), (0, 0, 3*(LAYER_SPACING*2+2*NODE_RADIUS) + NODE_RADIUS + self.offset_end, self.SCREEN_HEIGHT))

        for c in self.connections:
            c.drawConnection(screen)
        for node in self.nodes:
            node.draw_node(screen)

class Node:
    def __init__(self, id, x, y, type, color, label = "", index=0):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.color = color
        self.label = label
        self.index = index
        self.connection_count = 0

    def draw_node(self, SCREEN):

        pygame.draw.circle(SCREEN, self.color[0], (self.x,self.y), NODE_RADIUS, 0, False, True, True, False)
        pygame.draw.circle(SCREEN, self.color[1], (self.x,self.y), NODE_RADIUS, 0, True, False, False, True)
        #draw labels
        if self.type != 1:
            text = NODE_FONT.render(self.label, 1, BLACK)
            SCREEN.blit(text, (
                # self.x + (self.type-1) * ((text.get_width() if not self.type else 0) + NODE_RADIUS + 5), 
                self.x - text.get_width()/2, 
                self.y - text.get_height()/2))

class Connection:
    def __init__(self, input, output, wt):
        self.input = input
        self.output = output
        self.wt = wt

    def drawConnection(self, SCREEN):
        color = (100, 100, 100) if self.wt >= 0 else (50, 50, 50)
        width = int(abs(self.wt * CONN_WIDTH))
        if width == 0: width = 1
        
        pygame.draw.line(
            SCREEN, 
            color,
            (self.input.x, self.input.y), 
            (self.output.x, self.output.y), 
            width)