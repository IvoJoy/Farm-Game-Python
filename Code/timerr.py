'''the module for having timers'''
import pygame

class Timer:
    '''creating timer'''
    def __init__(self, duration, func = None):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False

    def activate(self):
        '''activating timer'''
        self.active = True
        self.start_time = pygame.time.get_ticks()
    def deactive(self):
        '''deactivating timer'''
        self.active = False
        self.start_time = 0

    def update(self):
        '''updating'''
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactive()
