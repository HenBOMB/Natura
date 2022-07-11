import pygame
from math import ceil
from natura.util import clamp, lerp

class Camera():
    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, fps: int = 60):
        self.cam_pos = (0, 0)
        self.offset_x = SCREEN_WIDTH / 2
        self.offset_y = SCREEN_HEIGHT / 2
        self.zoom_scale = .5
        self.click_offset_x = 0
        self.click_offset_y = 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.delta = 1. / float(fps)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
    
    def tick(self, fps: int):
        if self.clock.get_fps() != 0: self.delta = 1. / self.clock.get_fps()
        pygame.display.update()
        self.clock.tick(fps)
    
    def pan_camera(self, pos: tuple):
        # v = clamp(self.zoom_scale, .4, 2)
        v = lerp(.01, .4, self.zoom_scale)

        # v = v if v < 1 else lerp(2, 7, (v-.9))
        self.offset_x = (self.click_offset_x + (pos[0] - self.cam_pos[0]) * v)
        self.offset_y = (self.click_offset_y + (pos[1] - self.cam_pos[1]) * v)

    def set_global_pos(self, pos: tuple):
        self.offset_x, self.offset_y = (self.screen_width / 2 - pos[0], self.screen_height / 2 - pos[1])

    def zoom(self, dir: int):
        self.zoom_scale = clamp(dir * .1 + self.zoom_scale, 0, 1)

    def set_pos(self, pos: tuple):
        self.cam_pos = pos
        self.click_offset_x = self.offset_x
        self.click_offset_y = self.offset_y

    def fix_pos(self, pos: tuple, offset: float = 0):
        magnitude = lerp(50, 0, self.zoom_scale)

        pos = (
            pos[0] + self.offset_x + offset, 
            pos[1] + self.offset_y + offset)
        return (
            pos[0] + pos[0] * magnitude - self.screen_width / 2 * magnitude, 
            pos[1] + pos[1] * magnitude - self.screen_height / 2 * magnitude)

    def fix_scale(self, scale: float):
        magnitude = lerp(50, 0, self.zoom_scale)

        return scale * (magnitude+1)

    def clear_screen(self, color: tuple = (0, 0, 0)):
        self.screen.fill(color)

    def draw_image(self, image: pygame.Surface, pos: tuple, scale: float = None, color_overlay: tuple = None):
        if scale:
            scale = self.fix_scale(scale)
            self.screen.blit(pygame.transform.scale(image, (scale, scale)), self.fix_pos(pos))
        else:
            self.screen.blit(image, self.fix_pos(pos))
            
    def draw_rect(self, color: tuple, rect: tuple, width: int = 0):
        x, y = self.fix_pos((rect[0], rect[1]))
        pygame.draw.rect(self.screen, color, (x, y, self.fix_scale(rect[2]), self.fix_scale(rect[3])), width)

    def draw_circle(self, color: tuple, pos: tuple, radius: float, width: int = 0):
            pygame.draw.circle(self.screen, color, self.fix_pos(pos), self.fix_scale(radius), int(ceil(self.fix_scale(width))) if width != 0 else 0)
