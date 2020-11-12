import pygame
import configparser
import pygame_gui
import random
from pygame_gui.core import UIContainer
from pygame_gui.elements import \
    UIScrollingContainer, \
    UIVerticalScrollBar
from ass1.helpers import *

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
randomize_n_voters_button = None
randomize_n_preferences_button = None
generate_table_button = None
number_votes_input = None
number_preferences_input = None
n_voters = -1
n_preferences = -1

voting_schemes = [
    'Voting for one',
    'Voting for two',
    'Veto voting',
    'Borda voting',
]


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

    #offsets
    top_offset = int(int(default_config['ScreenHeight'])/18)
    left_offset = int(int(default_config['ScreenWidth'])/32)

    #output console dimension
    output_console_size = (int(int(default_config['ScreenWidth'])/5),int(default_config['ScreenHeight'])-top_offset)
    output_console_position = (int(int(default_config['ScreenWidth'])-int(default_config['ScreenWidth'])/5)-left_offset, top_offset)


def init_pygame():
    global screen
    global screen_size
    global clock
    global background_surface

    pygame.init()
    pygame.display.set_caption("Voting scheme")
    screen = pygame.display.set_mode(screen_size)

    background_surface = pygame.Surface(screen_size)
    background_surface.fill(pygame.Color(SPACE_GREY))

    clock = pygame.time.Clock()


def init_settings_ui():
    global randomize_n_voters_button
    global number_votes_input
    global randomize_n_preferences_button
    global number_preferences_input

    # init n voters ui
    gui.create_label(pygame, ui_manager, position=(left_offset, int(top_offset*2.2)), text='Number of voters',
                     size=(200, 50))
    number_votes_input = gui.create_input(pygame, ui_manager,
                                          size=(150, int(top_offset*0.6)),
                                          position=(left_offset + 225, int(top_offset*2.5)))
    number_votes_input.set_allowed_characters('numbers')
    number_votes_input.set_text_length_limit(2)
    randomize_n_voters_button = gui.create_button(pygame, ui_manager,
                                                  text='Randomize number of voters',
                                                  size=(300, int(top_offset*1.0)),
                                                  position=(left_offset + 400, int(top_offset*2.2)))

    # init n preferences ui
    gui.create_label(pygame, ui_manager, position=(left_offset, int(top_offset*3.7)),
                     text='Number of preferences',
                     size=(200, 50))
    number_preferences_input = gui.create_input(pygame, ui_manager, size=(150, int(top_offset*0.6)),
                                                position=(left_offset + 225, int(top_offset*4.0)))
    number_votes_input.set_allowed_characters('numbers')
    number_votes_input.set_text_length_limit(2)
    randomize_n_preferences_button = gui.create_button(pygame, ui_manager, text='Randomize number of preferences',
                                                       size=(300, int(top_offset*1.0)),
                                                       position=(left_offset + 400, int(top_offset*3.7)))

    # init vector initialization
    gui.create_label(pygame, ui_manager, position=(left_offset, int(top_offset*5.2)),
                     text='Preference vector (two dimensional python array [[]])',
                     size=(700, 50))
    preference_vector_input = gui.create_input(pygame, ui_manager, size=(375, int(top_offset*0.6)),
                                                position=(left_offset, int(top_offset*6.7)))
    save_preference_vector_button = gui.create_button(pygame, ui_manager, text='Save preference vector',
                                                       size=(300, int(top_offset*1.0)),
                                                       position=(left_offset + 400, int(top_offset*6.5)))



def init_runtime_ui():
    global generate_table_button
    gui.create_label(pygame, ui_manager,
                     position=(left_offset, int(top_offset*12.0)),
                     size=(700, 50),
                     text='Runtime')

    gui.create_dropdown_button(pygame, ui_manager,
                               opt_list=voting_schemes,
                               position=(left_offset, int(top_offset*13.5)),
                               size=(300, int(top_offset*1.0))
                               )
    generate_table_button = gui.create_button(pygame, ui_manager,
                      text='Generate voters table',
                      position=(left_offset + 400, int(top_offset*13.5)),
                      size=(300, int(top_offset*1.0))
                      )


def create_table_ui():
    gui.create_label(
        pygame,
        ui_manager,
        position=(725 + left_offset, top_offset),
        size=(150, 50),
        text='Preference Vector',
    )

    gui.create_label(
        pygame,
        ui_manager,
        position=(725 + left_offset + 150 + 25, top_offset),
        size=(150, 50),
        text='Voter Name',
    )

    gui.create_label(
        pygame,
        ui_manager,
        position=(725 + left_offset + 300 + 50, top_offset),
        size=(100, 50),
        text='Pref...',
    )

    rect = pygame.Rect((725 + left_offset, int(top_offset*2.5)), (450, int(top_offset*12.0)))
    table_container = UIScrollingContainer(
        relative_rect=rect,
        manager=ui_manager,
    )
    return table_container


def create_table(table_container):
    container = table_container.get_container()
    container.clear()

    vertical_offset = 50
    horizontal_offset = 175
    for i in range(n_voters):
        vector_input = gui.create_input(
            pygame,
            ui_manager,
            size=(150, 30),
            container=table_container,
            position=(0, vertical_offset * i),
        )

        voter_name_label = gui.create_label(
            pygame,
            ui_manager,
            size=(150, 30),
            text='Voter ' + str(i + 1),
            container=table_container,
            position=(horizontal_offset, vertical_offset * i),
        )

        container.add_element(vector_input)
        container.add_element(voter_name_label)

        for j in range(n_preferences):
            preference_label = gui.create_label(
                pygame,
                ui_manager,
                size=(150, 30),
                text=str(j + 1),
                container=table_container,
                position=(horizontal_offset * (j + 2), vertical_offset * i),
            )
            container.add_element(preference_label)


    table_container.set_scrollable_area_dimensions((1000, n_voters * vertical_offset))


if __name__ == "__main__":
    init_settings()
    init_pygame()
    ui_manager = gui.init_ui(screen_size)
    gui.create_text_box(pygame, ui_manager, size=output_console_size, position=output_console_position)

    gui.create_label(pygame, ui_manager, position=(left_offset, int(top_offset*0.7)), size=(700, int(top_offset*1.0)), text='Settings')

    init_settings_ui()

    # create buttons for choosing algorithms and running the code
    init_runtime_ui()

    table_container = create_table_ui()
    running = True

    while running:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui_manager.process_events(event)

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == randomize_n_voters_button:
                        n_voters = random.randint(0, 99)
                        number_votes_input.set_text(str(n_voters))
                    if event.ui_element == randomize_n_preferences_button:
                        n_preferences = random.randint(0, 99)
                        number_preferences_input.set_text(str(n_preferences))
                    if event.ui_element == generate_table_button:
                        if n_voters == -1:
                            n_voters = 10
                            number_votes_input.set_text('10')
                            print('Setting number of voters to a default value of 10')
                        if n_preferences == -1:
                            n_preferences = 3
                            number_preferences_input.set_text('3')
                            print('Setting number of preferences to a default value of 3')
                        create_table(table_container)

        ui_manager.update(time_delta)

        screen.blit(background_surface, (0, 0))
        ui_manager.draw_ui(screen)

        pygame.display.update()
