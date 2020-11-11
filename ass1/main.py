import pygame
import configparser

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core import IncrementalThreadedResourceLoader
from pygame_gui import UI_TEXT_BOX_LINK_CLICKED
from ass1.helpers import *

config = None
window_size = None
screen = None


def init_settings():
    global config
    global window_size

    config = configparser.ConfigParser()

    default_config = config['DEFAULT']

    window_size = (default_config['WindowWidth'],
                   default_config['WindowHeight'])


def init_pygame():
    global screen
    global window_size

    pygame.init()
    pygame.display.set_caption("Voting scheme")
    screen = pygame.display.set_mode(window_size)

    background_surface = pygame.Surface(window_size)
    background_surface.fill(pygame.Color("#000000"))


if __name__ == "__main__":
    init_settings()
    init_pygame()








loader = IncrementalThreadedResourceLoader()
clock = pygame.time.Clock()
ui_manager = UIManager(screen_size, 'data/themes/theme_1.json', resource_loader=loader)
ui_manager.add_font_paths("Montserrat",
                          "data/fonts/Montserrat-Regular.ttf",
                          "data/fonts/Montserrat-Bold.ttf",
                          "data/fonts/Montserrat-Italic.ttf",
                          "data/fonts/Montserrat-BoldItalic.ttf")

load_time_1 = clock.tick()
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
                          {'name': 'fira_code', 'html_size': 2, 'style': 'regular'},
                          {'name': 'fira_code', 'html_size': 2, 'style': 'bold'},
                          {'name': 'fira_code', 'html_size': 2, 'style': 'bold_italic'}
                          ])
loader.start()
finished_loading = False
while not finished_loading:
    finished_loading, progress = loader.update()
load_time_2 = clock.tick()
print('Font load time taken:', load_time_2 / 1000.0, 'seconds.')

time_1 = clock.tick()
# html_text_line = create_large_text_box()
time_2 = clock.tick()

htm_text_block_2 = UITextBox('<font face=fira_code size=2 color=#000000><b>Hey, What the heck!</b>'
                             '<br><br>'
                             'This is some <a href="test">text</a> in a different box,'
                             ' hooray for variety - '
                             'if you want then you should put a ring upon it. '
                             '<body bgcolor=#990000>What if we do a really long word?</body> '
                             '<b><i>derp FALALALALALALALXALALALXALALALALAAPaaaaarp gosh'
                             '</b></i></font>',
                             pygame.Rect((520, 10), (250, 200)),
                             manager=ui_manager,
                             object_id="#text_box_2")
htm_text_block_2.set_active_effect('typing_appear')
time_3 = clock.tick()

print('Time taken 1st window:', time_2 / 1000.0, 'seconds.')
print('Time taken 2nd window:', time_3 / 1000.0, 'seconds.')

ui_manager.print_unused_fonts()

running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                htm_text_block_2.set_active_effect('fade_out')
            if event.key == pygame.K_k:
                html_text_line.kill()
            if event.key == pygame.K_b:
                html_text_line = create_large_text_box()

        if event.type == pygame.USEREVENT:
            if event.user_type == UI_TEXT_BOX_LINK_CLICKED:
                if event.ui_element is htm_text_block_2:
                    if event.link_target == 'test':
                        print('clicked test link')
                else:
                    print('clicked link in text block 1')

        ui_manager.process_events(event)

    ui_manager.update(time_delta)

    screen.blit(background_surface, (0, 0))
    ui_manager.draw_ui(screen)

    pygame.display.update()
