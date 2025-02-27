'''the module for the player character'''
import os
import pygame
from src.settings import LAYERS, PLAYER_TOOL_OFFSET
from src.support import import_folder
from src.timerr import Timer
from typing import Dict, List, Callable
from src.soil import SoilLayer

class Player(pygame.sprite.Sprite):
    ''' Player class '''
    def __init__(self, pos: tuple[int, int], group: pygame.sprite.Group, collision_sprites: pygame.sprite.Group, 
                 tree_sprites: pygame.sprite.Group, interaction: pygame.sprite.Group, soil_layer: SoilLayer, 
                 toggle_shop: Callable[[], None]) -> None:
        super().__init__(group)

        self.import_assets()
        self.status: str = 'down_idle'
        self.frame_index: float = 0

        self.image: pygame.Surface = self.animations[self.status][self.frame_index]
        self.rect: pygame.Rect = self.image.get_rect(center=pos)
        self.z: int = LAYERS['main']

        self.direction: pygame.math.Vector2 = pygame.math.Vector2()
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(self.rect.center)
        self.speed: int = 300

        # coll
        self.collision_sprites: pygame.sprite.Group = collision_sprites
        self.hitbox: pygame.Rect = self.rect.copy().inflate((-126, -70))

        # timers
        self.timers: Dict[str, Timer] = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }

        # tools
        self.tools: List[str] = ['hoe', 'axe', 'water']
        self.tool_index: int = 0
        self.selected_tool: str = self.tools[self.tool_index]

        # seeds
        self.seeds: List[str] = ['corn', 'tomato']
        self.seed_index: int = 0
        self.selected_seed: str = self.seeds[self.seed_index]

        # inventory
        self.item_inventory: Dict[str, int] = {
            'wood': 10,
            'apple': 10,
            'corn': 10,
            'tomato': 10
        }
        self.seed_inventory: Dict[str, int] = {
            'corn': 5,
            'tomato': 5
        }
        self.money: int = 200

        # interaction
        self.tree_sprites: pygame.sprite.Group = tree_sprites
        self.interaction: pygame.sprite.Group = interaction
        self.sleep: bool = False
        self.soil_layer: SoilLayer = soil_layer
        self.toggle_shop: Callable[[], None] = toggle_shop

        # sound
        self.watering: pygame.mixer.Sound = pygame.mixer.Sound(os.getcwd() + '/audio/water.mp3')
        self.watering.set_volume(0.1)


    def use_tool(self) -> None:
        ''' using the tools '''
        self.get_target_pos()
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.watering.play()

    def get_target_pos(self) -> None:
        ''' getting target position'''
        self.target_pos: pygame.math.Vector2 = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]


    def use_seed(self) -> None:
        ''' using seeds '''
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def import_assets(self) -> None:
        '''importing assets'''
        self.animations: Dict[str, List[pygame.Surface]] = {'up': [], 'down': [], 'left': [], 'right': [],
                                                            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                                                            'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                                                            'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                                                            'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}
        for animation in self.animations.keys():
            # had a problem extracting the directory, so had to use os.getcwd()
            full_path: str = os.getcwd() + '/graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)
            
    def animate(self, dt: float) -> None:
        '''animating'''
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self) -> None:
        '''taking input from the keyboard'''
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active and not self.sleep:
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # tool use
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # changing tools
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]

            # seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # changing seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]

            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    else:
                        self.status = 'left_idle'
                        self.sleep = True

    def get_status(self) -> None:
        '''status of character'''
        # idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        # tools use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self) -> None:
        '''updating timers'''
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction: str) -> None:
        '''collision with objects'''
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt: float) -> None:
        '''moving the character'''
        # normalizing vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        #horizontal
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        #vertical
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt: float) -> None:
        '''updating'''
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
