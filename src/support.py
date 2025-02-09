'''the module for 2 functions that help import pictures'''
from os import walk
import pygame
from typing import List, Dict

def import_folder(path: str) -> List[pygame.Surface]:
    '''importing a folder'''
    surface_list: List[pygame.Surface] = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf: pygame.Surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_folder_dict(path: str) -> Dict[str, pygame.Surface]:
    '''importing a folder directory'''
    surface_dict: Dict[str, pygame.Surface] = {}

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf: pygame.Surface = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf

    return surface_dict
