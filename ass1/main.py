import pygame
import configparser

from ass1.helpers import *
import ass1.gui as gui

config = None
screen_size = None
screen = None
clock = None
ui_manager = None
background_surface = None
top_offset = 50
left_offset = 50
output_console_size = (300, 1100)
output_console_position = (1250, top_offset)
FPS = 60

voting_schemes = [
    'Voting for one',
    'Voting for two',
    'Veto voting',
    'Borda voting',
]


def init_settings():
    global config
    global screen_size

    config = configparser.ConfigParser()
    config.read_file(open('./config.ini'))

    default_config = config['DEFAULT']

    screen_size = (int(default_config['ScreenWidth']),
                   int(default_config['ScreenHeight']))


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


def init_n_voters_ui():
    gui.create_label(pygame, ui_manager, position=(left_offset, top_offset - 15 + 75), text='Number of voters',
                     size=(200, 50))
    number_votes_input = gui.create_input(pygame, ui_manager,
                                          size=(150, 30),
                                          position=(left_offset + 225, top_offset + 75))
    number_votes_input.set_allowed_characters('numbers')
    number_votes_input.set_text_length_limit(2)
    gui.create_button(pygame, ui_manager, text='Randomize number of voters', size=(300, 50),
                      position=(left_offset + 400, top_offset - 15 + 75))


def init_n_preferences_ui():
    offset = 75
    gui.create_label(pygame, ui_manager, position=(left_offset, top_offset - 15 + offset + 75),
                     text='Number of preferences',
                     size=(200, 50))
    number_votes_input = gui.create_input(pygame, ui_manager, size=(150, 30),
                                          position=(left_offset + 225, top_offset + offset + 75))
    number_votes_input.set_allowed_characters('numbers')
    number_votes_input.set_text_length_limit(2)
    gui.create_button(pygame, ui_manager, text='Randomize number of preferences', size=(300, 50),
                      position=(left_offset + 400, top_offset - 15 + offset + 75))


if __name__ == "__main__":
    init_settings()
    init_pygame()
    ui_manager = gui.init_ui(screen_size)
    gui.create_text_box(pygame, ui_manager, size=output_console_size, position=output_console_position)

    gui.create_label(pygame, ui_manager, position=(left_offset, top_offset - 15), size=(700, 50), text='Settings')

    # create number of voters ui
    init_n_voters_ui()

    # # create number of preferences ui
    init_n_preferences_ui()

    gui.create_label(pygame, ui_manager,
                     position=(left_offset, 300),
                     size=(700, 50),
                     text='Runtime')

    gui.create_dropdown_button(pygame, ui_manager,
                               opt_list=voting_schemes,
                               position=(left_offset, 375),
                               size=(300, 50)
                               )
    gui.create_button(pygame, ui_manager,
                      text='Generate voters table',
                      position=(left_offset + 400, 375),
                      size=(300, 50)
                      )

    running = True

    while running:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui_manager.process_events(event)

        ui_manager.update(time_delta)

        screen.blit(background_surface, (0, 0))
        ui_manager.draw_ui(screen)

        pygame.display.update()
