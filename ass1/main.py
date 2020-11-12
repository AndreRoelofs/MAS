import pygame
import configparser
import pygame_gui
import random
from pygame_gui.core import UIContainer
from pygame_gui.elements import \
    UIScrollingContainer, \
    UIVerticalScrollBar
from ass1.helpers import *
from ast import literal_eval
import numpy as np

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
preference_vector_input = None
save_preference_vector_button = None
response_label = None

preference_vector = []

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
    global preference_vector_input
    global save_preference_vector_button
    global response_label

    # init n voters ui
    gui.create_label(pygame, ui_manager, position=(int(left_offset*1.0), int(top_offset*2.2)), text='Number of voters',
                     size=(int(left_offset*4.0), int(top_offset*1.0)))
    number_votes_input = gui.create_input(pygame, ui_manager,
                                          size=(int(left_offset*3.0), int(top_offset*0.6)),
                                          position=(int(left_offset*5.5), int(top_offset*2.5)))
    number_votes_input.set_allowed_characters('numbers')
    number_votes_input.set_text_length_limit(2)
    randomize_n_voters_button = gui.create_button(pygame, ui_manager,
                                                  text='Randomize number of voters',
                                                  size=(int(left_offset*6.0), int(top_offset*1.0)),
                                                  position=(int(left_offset*9.0), int(top_offset*2.2)))

    # init n preferences ui
    gui.create_label(pygame, ui_manager, position=(int(left_offset*1.0), int(top_offset*3.7)),
                     text='Number of preferences',
                     size=(int(left_offset*4.0), int(top_offset*1.0)))
    number_preferences_input = gui.create_input(pygame, ui_manager, size=(int(left_offset*3.0), int(top_offset*0.6)),
                                                position=(int(left_offset*5.5), int(top_offset*4.0)))
    number_votes_input.set_allowed_characters('numbers')
    number_votes_input.set_text_length_limit(2)
    randomize_n_preferences_button = gui.create_button(pygame, ui_manager, text='Randomize number of preferences',
                                                       size=(int(left_offset*6.0), int(top_offset*1.0)),
                                                       position=(int(left_offset*9.0), int(top_offset*3.7)))

    # init vector initialization
    gui.create_label(pygame, ui_manager, position=(int(left_offset*1.0), int(top_offset*5.2)),
                     text='Preference vector (two dimensional python array [[]])',
                     size=(int(left_offset*14.0), int(top_offset*1.0)))
    preference_vector_input = gui.create_input(pygame, ui_manager, size=(int(left_offset*7.5), int(top_offset*0.6)),
                                                position=(int(left_offset*1.0), int(top_offset*6.7)))
    save_preference_vector_button = gui.create_button(pygame, ui_manager, text='Save preference vector',
                                                       size=(int(left_offset*6.0), int(top_offset*1.0)),
                                                       position=(int(left_offset*9.0), int(top_offset*6.5)))
    response_label = gui.create_text_display(pygame,
                                             ui_manager,
                                             position=(int(left_offset*1.0), int(top_offset*8)),
                                             size=(int(left_offset*14.0), int(top_offset*1.2)))



def init_runtime_ui():
    global generate_table_button
    gui.create_label(pygame, ui_manager,
                     position=(int(left_offset*1.0), int(top_offset*12.0)),
                     size=(int(left_offset*14.0), int(top_offset*1.0)),
                     text='Runtime')

    gui.create_dropdown_button(pygame, ui_manager,
                               opt_list=voting_schemes,
                               position=(int(left_offset*1.0), int(top_offset*13.5)),
                               size=(int(left_offset*6.0), int(top_offset*1.0))
                               )
    generate_table_button = gui.create_button(pygame, ui_manager,
                      text='Generate voters table',
                      position=(int(left_offset*9.0), int(top_offset*13.5)),
                      size=(int(left_offset*6.0), int(top_offset*1.0))
                      )


def create_table_ui():
    gui.create_label(
        pygame,
        ui_manager,
        position=(int(left_offset*15.5), int(top_offset*1.0)),
        size=(int(left_offset*3.0), int(top_offset*1.0)),
        text='Preference Vector',
    )

    gui.create_label(
        pygame,
        ui_manager,
        position=(int(left_offset*19.0), int(top_offset*1.0)),
        size=(int(left_offset*3.0), int(top_offset*1.0)),
        text='Voter Name',
    )

    gui.create_label(
        pygame,
        ui_manager,
        position=(int(left_offset*22.5), int(top_offset*1.0)),
        size=(int(left_offset*2.0), int(top_offset*1.0)),
        text='Pref...',
    )

    rect = pygame.Rect((int(left_offset*15.5), int(top_offset*2.5)), (int(left_offset*9.0), int(top_offset*12.0)))
    table_container = UIScrollingContainer(
        relative_rect=rect,
        manager=ui_manager,
    )
    return table_container


def create_table(table_container):
    container = table_container.get_container()
    container.clear()

    top_size = int(top_offset*0.6)
    left_size = int(left_offset*3.0)
    vertical_offset = top_offset
    horizontal_offset = int(left_offset*3.5)
    for i in range(n_voters):
        vector_input = gui.create_input(
            pygame,
            ui_manager,
            size=(left_size, top_size),
            container=table_container,
            position=(0, vertical_offset * i),
        )

        voter_name_label = gui.create_label(
            pygame,
            ui_manager,
            size=(left_size, top_size),
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
                size=(left_size, top_size),
                text=str(j + 1),
                container=table_container,
                position=(horizontal_offset * (j + 2), vertical_offset * i),
            )
            container.add_element(preference_label)


    table_container.set_scrollable_area_dimensions((1000, n_voters * vertical_offset))


def parse_vector(pref_vec):
    # Simple check whether it is a 2D array
    if pref_vec[:2] == '[[' and pref_vec[-2:] == ']]':
        # Use ast.literal_eval to convert the string to an actual array
        pv = np.array(literal_eval(pref_vec))

        # Check whether the votes match the amount of preferences
        if (pv.min() < 0) | (pv.max() > n_preferences):
            return None

        # Check whether the dimensions fit the amount of voters & preferences
        if pv.shape[0] == n_voters and pv.shape[1] == n_preferences:
            # Check for each voter whether he has voted correctly
            for c, voter in enumerate(pv):
                if len(voter) == len(set(voter)):
                    return pv
                else:
                    print("Voter {voter} has voted multiple times for a candidate".format(voter=c+1))
        return None


if __name__ == "__main__":
    init_settings()
    init_pygame()
    ui_manager = gui.init_ui(screen_size)
    gui.create_text_box(pygame, ui_manager, size=output_console_size, position=output_console_position)

    gui.create_label(pygame, ui_manager, position=(left_offset, int(top_offset*0.7)), size=(int(left_offset*14.0), int(top_offset*1.0)), text='Settings')

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
                    if event.ui_element == save_preference_vector_button:
                        preference_vector_in = preference_vector_input.get_text()
                        parsed_vector = parse_vector(preference_vector_in)
                        if parsed_vector is None:
                            response_label.set_text("Not a correct preference vector")
                        else:
                            response_label.set_text("Preference vector parsed!")



                # Input parsing
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == number_votes_input:
                        n_voters = int(event.text)
                    elif event.ui_element == number_preferences_input:
                        n_preferences = int(event.text)

        ui_manager.update(time_delta)

        screen.blit(background_surface, (0, 0))
        ui_manager.draw_ui(screen)

        pygame.display.update()
