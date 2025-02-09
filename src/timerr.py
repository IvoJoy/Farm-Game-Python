'''the module for having timers'''
import pygame
from typing import Callable, Optional

class Timer:
    '''creating timer'''
    def __init__(self, duration: int, func: Optional[Callable[[], None]] = None) -> None:
        self.duration: int = duration
        self.func: Optional[Callable[[], None]] = func
        self.start_time: int = 0
        self.active: bool = False

    def activate(self) -> None:
        '''activating timer'''
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactive(self) -> None:
        '''deactivating timer'''
        self.active = False
        self.start_time = 0

    def update(self) -> None:
        '''updating'''
        current_time: int = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactive()
