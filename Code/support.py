'''the module for 2 functions that help import pictures'''
from os import walk
import pygame

def import_folder(path):
    '''importing a folder'''
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)


    return surface_list

def import_folder_dict(path):
    '''importing a folder directory'''
    surface_dict = {}
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf

    return surface_dict
