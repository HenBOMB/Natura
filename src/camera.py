import pygame
from tools import clamp

class Camera():
    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, fps: int = 60):
        self.cam_pos = (0, 0)
        self.offset_x = SCREEN_WIDTH / 2
        self.offset_y = SCREEN_HEIGHT / 2
        self.zoom_scale = 1
        self.click_offset_x = 0
        self.click_offset_y = 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.delta = 1. / float(fps)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
    
    def tick(self):
        if self.clock.get_fps() != 0: self.delta = 1. / self.clock.get_fps()
        pygame.display.update()
        self.clock.tick(self.fps)
    
    def pan_camera(self, pos: tuple):
        v = clamp(self.zoom_scale, .4, 2)
        self.offset_x = (self.click_offset_x + (pos[0] - self.cam_pos[0]) * v)
        self.offset_y = (self.click_offset_y + (pos[1] - self.cam_pos[1]) * v)

    def zoom(self, dir: int):
        self.zoom_scale = clamp(dir * .1 + self.zoom_scale, 0, 1.9)

    def set_pos(self, pos: tuple):
        self.cam_pos = pos
        self.click_offset_x = self.offset_x
        self.click_offset_y = self.offset_y

    def fix_pos(self, pos: tuple, offset: float = 0):
        pos = (
            pos[0] + self.offset_x + offset, 
            pos[1] + self.offset_y + offset)
        return (
            pos[0] + pos[0] * (1-self.zoom_scale) - self.screen_width / 2 * (1-self.zoom_scale), 
            pos[1] + pos[1] * (1-self.zoom_scale) - self.screen_height / 2 * (1-self.zoom_scale))

    def fix_scale(self, scale: float):
        return scale * (2-self.zoom_scale)

    def clear_screen(self):
        self.screen.fill((0, 0, 0))

    def draw_image(self, image: pygame.Surface, pos: tuple, scale: float = None, color_overlay: tuple = None):
        if scale:
            scale = self.fix_scale(scale)
            self.screen.blit(pygame.transform.scale(image, (scale, scale)), self.fix_pos(pos))
        else:
            self.screen.blit(image, self.fix_pos(pos))
            
    def draw_rect(self, color: tuple, rect: tuple, width: int = 0):
        x, y = self.fix_pos((rect[0], rect[1]))
        pygame.draw.rect(self.screen, color, (x, y, self.fix_scale(rect[2]), self.fix_scale(rect[3])), width)

    def draw_circle(self, color: tuple, pos: tuple, radius: float):
            pygame.draw.circle(self.screen, color, self.fix_pos(pos), self.fix_scale(radius))