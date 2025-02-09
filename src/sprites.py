'''the module for different objects in game'''
import os
from random import randint, choice
import pygame
from pygame.surface import Surface
from pygame.sprite import Group
from src.settings import LAYERS, APPLE_POS
from typing import Callable

class Generic(pygame.sprite.Sprite):
    '''the generic'''
    def __init__(self, pos: tuple[int, int], surf: Surface, groups: list[Group], z: int = LAYERS['main']):
        super().__init__(*groups)
        self.image: Surface = surf
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        self.z: int = z
        self.hitbox: pygame.Rect = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Interaction(Generic):
    '''one for interactions'''
    def __init__(self, pos: tuple[int, int], size: tuple[int, int], groups: Group, name: str):
        surf: Surface = pygame.Surface(size)
        super().__init__(pos, surf, [groups])
        self.name: str = name

class Water(Generic):
    '''one for the water'''
    def __init__(self, pos: tuple[int, int], frames: list[Surface], groups: Group):
        self.frames: list[Surface] = frames
        self.frame_index: float = 0
        super().__init__(pos=pos, surf=self.frames[int(self.frame_index)], groups=[groups], z=LAYERS['water'])

    def animate(self, dt: float) -> None:
        '''pseudo animating water'''
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt: float) -> None:
        '''updating'''
        self.animate(dt)

class Wildflower(Generic):
    '''one for the flowers around'''
    def __init__(self, pos: tuple[int, int], surf: Surface, groups: list[Group]):
        super().__init__(pos, surf, groups)
        self.hitbox: pygame.Rect = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Particle(Generic):
    '''a particle effect'''
    def __init__(self, pos: tuple[int, int], surf: Surface, groups: Group, z: int, duration: int = 200):
        super().__init__(pos, surf, [groups], z)
        self.start_time: int = pygame.time.get_ticks()
        self.duration: int = duration

        mask_surf: pygame.Mask = pygame.mask.from_surface(self.image)
        new_surf: Surface = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, dt: float) -> None:
        '''updating'''
        current_time: int = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.kill()

class Tree(Generic):
    '''one for the trees'''
    def __init__(self, pos: tuple[int, int], surf: Surface, groups: list[Group], name: str, player_add: Callable):
        super().__init__(pos, surf, groups)
        self.all_sprites: Group = groups[0]

        # tree attributes
        self.health: int = 5
        self.is_alive: bool = True
        stump_path: str = os.getcwd() + f'/graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf: Surface = pygame.image.load(stump_path).convert_alpha()

        # apples
        self.apple_surf: Surface = pygame.image.load(os.getcwd() + '/graphics/fruit/apple.png').convert_alpha()
        self.apple_pos: list[tuple[int, int]] = APPLE_POS[name]
        self.apple_sprites: Group = pygame.sprite.Group()
        self.create_fruit()

        self.player_add: Callable = player_add
        self.axe_sound: pygame.mixer.Sound = pygame.mixer.Sound(os.getcwd() + '/audio/axe.mp3')

    def damage(self) -> None:
        '''hitting a tree with an axe'''
        self.health -= 1
        self.axe_sound.play()
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(random_apple.rect.topleft, random_apple.image, self.all_sprites, LAYERS['fruit'])
            self.player_add('apple')
            random_apple.kill()

    def check_death(self) -> None: 
        '''is it?'''
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.all_sprites, LAYERS['fruit'], 500)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.is_alive = False
            self.player_add('wood')

    def update(self, dt: float) -> None:
        '''updating'''
        if self.is_alive:
            self.check_death()

    def create_fruit(self) -> None:
        '''spawning apples'''
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x, y = pos[0] + self.rect.left, pos[1] + self.rect.top
                Generic(
                    pos=(x, y),
                    surf=self.apple_surf,
                    groups=[self.apple_sprites, self.all_sprites],
                    z=LAYERS['fruit']
                )
