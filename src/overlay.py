'''the module for overlay'''
import os
import pygame
from src.settings import OVERLAY_POSITIONS
from src.player import Player

class Overlay:
    '''Overlay class'''
    def __init__(self, player: Player) -> None:
        # setup
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.player: Player = player

        # imports
        overlay_path: str = os.getcwd() + '/graphics/overlay/'
        self.tools_surf: dict[str, pygame.Surface] = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf: dict[str, pygame.Surface] = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self) -> None:
        '''Display overlay'''
        # tools
        tool_surf: pygame.Surface = self.tools_surf[self.player.selected_tool]
        tool_rect: pygame.Rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        # seeds
        seeds_surf: pygame.Surface = self.seeds_surf[self.player.selected_seed]
        seed_rect: pygame.Rect = seeds_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seeds_surf, seed_rect)
