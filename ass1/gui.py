from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import *

from ass1.helpers import *


def init_ui(screen_size):
    ui_manager = UIManager(screen_size, 'data/themes/theme_1.json')
    ui_manager.add_font_paths("Montserrat",
                              "data/fonts/Montserrat-Regular.ttf",
                              "data/fonts/Montserrat-Bold.ttf",
                              "data/fonts/Montserrat-Italic.ttf",
                              "data/fonts/Montserrat-BoldItalic.ttf",
                              )
    font_size_multiplier = screen_size[0] + screen_size[1] / 2500
    ui_manager.preload_fonts([{'name': 'Montserrat', 'html_size': 4.5 * font_size_multiplier, 'style': 'bold'},
                              {'name': 'Montserrat', 'html_size': 4.5 * font_size_multiplier, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 2 * font_size_multiplier, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 2 * font_size_multiplier, 'style': 'italic'},
                              {'name': 'Montserrat', 'html_size': 6 * font_size_multiplier, 'style': 'bold'},
                              {'name': 'Montserrat', 'html_size': 6 * font_size_multiplier, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 6 * font_size_multiplier, 'style': 'bold_italic'},
                              {'name': 'Montserrat', 'html_size': 4 * font_size_multiplier, 'style': 'bold'},
                              {'name': 'Montserrat', 'html_size': 4 * font_size_multiplier, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 4 * font_size_multiplier, 'style': 'italic'},
                              {'name': 'Montserrat', 'point_size': 18, 'style': 'bold_italic'},
                              {'name': 'Montserrat', 'point_size': 18, 'style': 'regular'},
                              {'name': 'Montserrat', 'point_size': 18, 'style': 'bold'},
                              ])

    return ui_manager


def create_text_box(pygame, ui_manager, size=(250, 200), position=(520, 10), font_size=5):
    return UITextBox('<font face=Montserrat size=' + str(font_size) + ' color=#000000>Awaiting execution...</font>',
                     pygame.Rect(position, size),
                     manager=ui_manager,
                     object_id="#text_box_2")


def create_text_display(pygame, ui_manager, size=(250, 100), position=(520, 10), font_size=5):
    return UILabel(pygame.Rect(position, size),
                                   "",
                                   manager=ui_manager,
                                   object_id='#fps_counter')


def create_button(pygame, ui_manager, text='', position=(30, 20), size=(100, 20)):
    button_layout_rect = pygame.Rect(position, size)

    return UIButton(relative_rect=button_layout_rect,
                    text=text,
                    manager=ui_manager)


def create_label(pygame, ui_manager, text='', position=(30, 20), size=(100, 20), container=None):
    label_layout_rect = pygame.Rect(position, size)
    return UILabel(relative_rect=label_layout_rect,
                   text=text,
                   manager=ui_manager,
                   container=container
                   )


def create_input(pygame, ui_manager, position=(30, 20), size=(100, 20), container=None):
    input_layout_rect = pygame.Rect(position, size)

    return UITextEntryLine(
        relative_rect=input_layout_rect,
        manager=ui_manager,
        container=container
    )


def create_dropdown_button(pygame, ui_manager, opt_list=['No options'], first_option_index=0, position=(30, 20),
                           size=(100, 20)):
    dropdown_layout_rect = pygame.Rect(position, size)

    return UIDropDownMenu(
        options_list=opt_list,
        starting_option=opt_list[first_option_index],
        relative_rect=dropdown_layout_rect,
        manager=ui_manager
    )
