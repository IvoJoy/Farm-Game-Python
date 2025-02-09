'''the module for the sky and rain'''
import os
from random import randint, choice
import pygame
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH, LAYERS
from src.support import import_folder
from src.sprites import Generic, Surface
from src.level import CameraGroup


class Sky:
    ''' class sky'''
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.end_color = (38, 101, 189)

    def display(self, dt: float) -> None:
        '''displaying'''
        for index, value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] -= int(2 * dt)
        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

class Drop(Generic):
    ''' rain drops'''
    # self, pos: tuple[int, int], surf: Surface, groups: list[Group], z: int
    def __init__(self, surf: Surface, pos: tuple[int, int], moving: bool, groups: list[pygame.sprite.Group], z: int) -> None:
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt: float) -> None:
        '''updating'''
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

class Rain:
    ''' rain class'''
    def __init__(self, all_sprites: CameraGroup) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(os.getcwd() + '/graphics/rain/drops')
        self.rain_floor = import_folder(os.getcwd() + '/graphics/rain/floor')
        self.floor_w, self.floor_h = pygame.image.load(os.getcwd() + '/graphics/world/ground.png').get_size()

    def create_floor(self) -> None:
        '''creating floor'''
        Drop(choice(self.rain_floor), (randint(0, self.floor_w), randint(0, self.floor_h)), False, [self.all_sprites], LAYERS['rain floor'])

    def create_drops(self) -> None:
        '''creating rain drops'''
        Drop(choice(self.rain_drops), (randint(0, self.floor_w), randint(0, self.floor_h)), True, [self.all_sprites], LAYERS['rain drops'])

    def update(self) -> None: 
        '''updating'''
        self.create_floor()
        self.create_drops()
