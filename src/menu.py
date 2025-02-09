'''the module for the buy/sell menu'''
import os
import pygame
from src.settings import PURCHASE_PRICES, SALE_PRICES, SCREEN_HEIGHT, SCREEN_WIDTH
from src.timerr import Timer
from typing import List, Callable
from src.player import Player

class Menu:
    '''menu class'''
    def __init__(self, player: 'Player', toggle_menu: Callable) -> None:
        self.player: 'Player' = player
        self.toggle_menu: Callable = toggle_menu
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.font: pygame.font.Font = pygame.font.Font(os.getcwd() + '/font/LycheeSoda.ttf', 30)

        # options
        self.width: int = 400
        self.space: int = 10
        self.padding: int = 8

        # entries
        self.options: List[str] = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border: int = len(self.player.item_inventory) - 1
        self.setup()

        # movement
        self.index: int = 0
        self.timer: Timer = Timer(200)


    def display_money(self) -> None:
        '''displaying the money'''
        text_surf: pygame.Surface = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect: pygame.Rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 3)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self) -> None:
        '''setting up'''
        self.text_surfs: List[pygame.Surface] = []
        self.total_height: int = 0
        for item in self.options:
            text_surf: pygame.Surface = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top: float = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect: pygame.Rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2,
                            self.menu_top, self.width, self.total_height)

        # buy/sell
        self.buy_text: pygame.Surface = self.font.render('Buy', False, 'Black')
        self.sell_text: pygame.Surface = self.font.render('Sell', False, 'Black')

    def input(self) -> None:
        '''getting input from keyboard'''
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()

                current_item: str = self.options[self.index]
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else:
                    seed_price: int = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= PURCHASE_PRICES[current_item]


        # clamping values
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index >= len(self.options):
            self.index = 0

    def show_entry(self, text_surf: pygame.Surface, amount: int, top: float, selected: bool) -> None:
        '''showing the menu'''
        # background
        bg_rect: pygame.Rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height()
                                          + self.padding * 2)
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 3)
        # text
        text_rect: pygame.Rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)
        # amount
        amount_surf: pygame.Surface = self.font.render(str(amount), False, 'Black')
        amount_rect: pygame.Rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
        # selected
        if selected:
            pygame.draw.rect(self.display_surface, 'Black', bg_rect, 3, 3)
            if self.index <= self.sell_border: # sell
                sell_rect: pygame.Rect = self.sell_text.get_rect(midleft = (self.main_rect.left + 150,
                                                            bg_rect.centery))
                self.display_surface.blit(self.sell_text, sell_rect)
            else: # buy
                buy_rect: pygame.Rect = self.buy_text.get_rect(midleft = (self.main_rect.left
                                                            + 150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, buy_rect)

    def update(self) -> None:
        '''updating'''
        self.input()
        self.display_money()
        for text_index,  text_surf in enumerate(self.text_surfs):
            top: float = self.main_rect.top + text_index * (text_surf.get_height() +
                                                    (self.padding * 2) + self.space)
            amount_list: List[int] = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount: int = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)
