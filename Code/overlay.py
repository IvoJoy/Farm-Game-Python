'''the module for overlay'''
import os
import pygame
from settings import OVERLAY_POSITIONS

class Overlay:
    '''Overlay class'''
    def __init__(self, player):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # imports
        overlay_path = os.getcwd() + '/graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):
        '''Display overlay'''
        # tools
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        # seeds
        seeds_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seeds_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seeds_surf, seed_rect)
