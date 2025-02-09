'''the module for the transition day/night'''
import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from typing import Callable
from src.player import Player

class Transition:
    '''transition class'''
    def __init__(self, reset: Callable[[], None], player: Player) -> None:
        # setup
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.reset: Callable[[], None] = reset
        self.player: Player = player

        # overlay image
        self.image: pygame.Surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color: int = 255
        self.speed: int = -2

    def play(self) -> None:
        '''the transition'''
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed = -2

        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
