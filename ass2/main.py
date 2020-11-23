import pygame
import configparser
import pygame_gui
from ass1.helpers import *
from ast import literal_eval
import numpy as np
from numpy import random
from ass2.auctioning import auctioning_types, start_price_types

import ass1.gui as gui

config = None
screen_size = None
screen = None
clock = None
ui_manager = None
background_surface = None
top_offset = None
left_offset = None
output_console_size = None
output_console_position = None
FPS = None
output_console = None

# ui
number_sellers_input = None
randomize_n_sellers_button = None

number_buyers_input = None
randomize_n_buyers_button = None

number_rounds_input = None
randomize_n_rounds_button = None

auctioning_type_dropdown = None
start_price_type_dropdown = None


# parameters
n_sellers = 2
n_buyers = 2
n_rounds = 2
max_starting_price = 1000


def init_settings():
    global config
    global screen_size
    global FPS
    global top_offset
    global left_offset
    global output_console_size
    global output_console_position

    config = configparser.ConfigParser()
    config.read_file(open('./config.ini'))

    default_config = config['DEFAULT']

    screen_size = (int(default_config['ScreenWidth']),
                   int(default_config['ScreenHeight']))
    FPS = int(default_config['FPS'])

    # offsets
    top_offset = int(int(default_config['ScreenHeight']) / 18)
    left_offset = int(int(default_config['ScreenWidth']) / 32)

    # output console dimension
    output_console_size = (
    int(int(default_config['ScreenWidth']) / 5), int(default_config['ScreenHeight']) - top_offset)
    output_console_position = (
    int(int(default_config['ScreenWidth']) - int(default_config['ScreenWidth']) / 5) - left_offset, top_offset)


def init_pygame():
    global screen
    global screen_size
    global clock
    global background_surface

    pygame.init()
    pygame.display.set_caption("Auctioning")
    screen = pygame.display.set_mode(screen_size)

    background_surface = pygame.Surface(screen_size)
    background_surface.fill(pygame.Color(SPACE_GREY))

    clock = pygame.time.Clock()


def create_starting_conditions_ui():
    global n_sellers
    global n_buyers

    global number_buyers_input
    global number_sellers_input
    global number_rounds_input

    global randomize_n_buyers_button
    global randomize_n_sellers_button
    global randomize_n_rounds_button

    gui.create_label(pygame, ui_manager, position=(left_offset, int(top_offset * 0.7)),
                     size=(int(left_offset * 14.0), int(top_offset * 1.0)), text='Starting conditions')


    # init n sellers ui
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 2.2)),
                     text='Sellers number K:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    number_sellers_input = gui.create_input(pygame, ui_manager,
                                          size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                          position=(int(left_offset * 5.5), int(top_offset * 2.5)))
    number_sellers_input.set_allowed_characters('numbers')
    number_sellers_input.set_text_length_limit(3)
    number_sellers_input.set_text(str(n_buyers))
    randomize_n_sellers_button = gui.create_button(pygame, ui_manager,
                                                  text='Randomize',
                                                  size=(int(left_offset * 6.0), int(top_offset * 1.0)),
                                                  position=(int(left_offset * 9.0), int(top_offset * 2.2)))

    # init n buyers ui
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 3.7)),
                     text='Buyers number N:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))
    number_buyers_input = gui.create_input(pygame, ui_manager,
                                                size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                                position=(int(left_offset * 5.5), int(top_offset * 4.0)))
    number_buyers_input.set_allowed_characters('numbers')
    number_buyers_input.set_text_length_limit(3)
    number_buyers_input.set_text(str(n_buyers))
    randomize_n_buyers_button = gui.create_button(pygame, ui_manager, text='Randomize',
                                                       size=(int(left_offset * 6.0), int(top_offset * 1.0)),
                                                       position=(int(left_offset * 9.0), int(top_offset * 3.7)))

    # init n rounds ui
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 5.2)),
                     text='Rounds number R:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))
    number_rounds_input = gui.create_input(pygame, ui_manager,
                                           size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                           position=(int(left_offset * 5.5), int(top_offset * 5.5)))
    number_rounds_input.set_allowed_characters('numbers')
    number_rounds_input.set_text_length_limit(3)
    number_rounds_input.set_text(str(n_rounds))
    randomize_n_rounds_button = gui.create_button(pygame, ui_manager, text='Randomize',
                                                  size=(int(left_offset * 6.0), int(top_offset * 1.0)),
                                                  position=(int(left_offset * 9.0), int(top_offset * 5.2)))


def create_auction_settings_ui():
    global auctioning_type_dropdown
    global start_price_type_dropdown

    gui.create_label(pygame, ui_manager,
                     position=(int(left_offset * 1.0), int(top_offset * 7.0)),
                     size=(int(left_offset * 14.0), int(top_offset * 1.0)),
                     text='Auction settings')


    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 8.5)),
                     text='Auctioning type:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))


    auctioning_type_dropdown = gui.create_dropdown_button(pygame, ui_manager,
                                                         opt_list=auctioning_types,
                                                         position=(int(left_offset * 6.0), int(top_offset * 8.5)),
                                                         size=(int(left_offset * 9.0), int(top_offset * 1.0)))

    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 10.0)),
                     text='Start price type:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    start_price_type_dropdown = gui.create_dropdown_button(pygame, ui_manager,
                                                           opt_list=start_price_types,
                                                           position=(int(left_offset * 6.0), int(top_offset * 10.0)),
                                                           size=(int(left_offset * 9.0), int(top_offset * 1.0)))








if __name__ == "__main__":
    init_settings()
    init_pygame()
    ui_manager = gui.init_ui(screen_size)
    output_console = gui.create_text_box(pygame, ui_manager, size=output_console_size, position=output_console_position)

    create_starting_conditions_ui()

    create_auction_settings_ui()


    running = True

    while running:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui_manager.process_events(event)

            if event.type == pygame.USEREVENT:
                test = 0

                # Input parsing
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    test = 0

        ui_manager.update(time_delta)

        screen.blit(background_surface, (0, 0))
        ui_manager.draw_ui(screen)

        pygame.display.update()
