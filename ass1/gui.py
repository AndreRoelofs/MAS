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
    ui_manager.preload_fonts([{'name': 'Montserrat', 'html_size': 4.5, 'style': 'bold'},
                              {'name': 'Montserrat', 'html_size': 4.5, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 2, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 2, 'style': 'italic'},
                              {'name': 'Montserrat', 'html_size': 6, 'style': 'bold'},
                              {'name': 'Montserrat', 'html_size': 6, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 6, 'style': 'bold_italic'},
                              {'name': 'Montserrat', 'html_size': 4, 'style': 'bold'},
                              {'name': 'Montserrat', 'html_size': 4, 'style': 'regular'},
                              {'name': 'Montserrat', 'html_size': 4, 'style': 'italic'},
                              {'name': 'Montserrat', 'point_size': 18, 'style': 'bold_italic'},
                              {'name': 'Montserrat', 'point_size': 18, 'style': 'regular'},
                              {'name': 'Montserrat', 'point_size': 18, 'style': 'bold'},
                              ])

    return ui_manager


def create_text_box(pygame, ui_manager, size=(250, 200), position=(520, 10), font_size=5):
    return UITextBox('<font face=Montserrat size=' + str(font_size) + ' color=#000000><b>Hey, What the heck!</b>'
                                                                      '<br><br>'
                                                                      'This is some <a href="test">text</a> in a different box,'
                                                                      ' hooray for variety - '
                                                                      'if you want then you should put a ring upon it. '
                                                                      '<body bgcolor=#990000>What if we do a really long word?</body> '
                                                                      '<b><i>derp FALALALALALALALXALALALXALALALALAAPaaaaarp gosh'
                                                                      '</b></i></font>',
                     pygame.Rect(position, size),
                     manager=ui_manager,
                     object_id="#text_box_2")


def create_button(pygame, ui_manager, text='', position=(30, 20), size=(100, 20)):
    button_layout_rect = pygame.Rect(position, size)

    return UIButton(relative_rect=button_layout_rect,
                    text=text,
                    manager=ui_manager)


def create_label(pygame, ui_manager, text='', position=(30, 20), size=(100, 20)):
    label_layout_rect = pygame.Rect(position, size)
    return UILabel(relative_rect=label_layout_rect,
                   text=text,
                   manager=ui_manager)


def create_input(pygame, ui_manager, position=(30, 20), size=(100, 20)):
    input_layout_rect = pygame.Rect(position, size)

    return UITextEntryLine(
        relative_rect=input_layout_rect,
        manager=ui_manager)


def create_dropdown_button(pygame, ui_manager, opt_list=['No options'], first_option_index=0, position=(30, 20),
                           size=(100, 20)):
    dropdown_layout_rect = pygame.Rect(position, size)

    return UIDropDownMenu(
        options_list=opt_list,
        starting_option=opt_list[first_option_index],
        relative_rect=dropdown_layout_rect,
        manager=ui_manager
    )
