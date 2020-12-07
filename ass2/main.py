import pygame
import configparser
import pygame_gui
from ass1.helpers import *
from ast import literal_eval
import numpy as np
from numpy import random
import pandas as pd
import matplotlib.pyplot as plt
from ass2.auctioning import *

import ass2.gui as gui

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
bidding_strategy_dropdown = None
output_dropdown = None

bid_increase_factor_input = None
bid_decrease_factor_input = None
refund_penalty_factor_input = None
refund_penalty_factor_label = None
max_starting_price_input = None

execute_button = None
output_button = None
auction = None

# parameters
n_sellers = 2
n_buyers = 2
n_rounds = 2
current_auction_type = auction_pure
current_pricing_type = price_type_random
current_bidding_strategy = bidding_advanced
current_output = output_all
bid_increase_factor = 1.2
bid_decrease_factor = 0.9
refund_penalty_factor = 0.1
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
    number_sellers_input.set_text_length_limit(2)
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
    number_buyers_input.set_text_length_limit(2)
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
    number_rounds_input.set_text_length_limit(5)
    number_rounds_input.set_text(str(n_rounds))
    randomize_n_rounds_button = gui.create_button(pygame, ui_manager, text='Randomize',
                                                  size=(int(left_offset * 6.0), int(top_offset * 1.0)),
                                                  position=(int(left_offset * 9.0), int(top_offset * 5.2)))


def create_auction_settings_ui():
    global auctioning_type_dropdown
    global start_price_type_dropdown
    global bidding_strategy_dropdown
    global output_dropdown
    global current_pricing_type
    global current_auction_type
    global current_bidding_strategy
    global current_output

    gui.create_label(pygame, ui_manager,
                     position=(int(left_offset * 1.0), int(top_offset * 7.0)),
                     size=(int(left_offset * 14.0), int(top_offset * 1.0)),
                     text='Auction settings')

    # auctioning type
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 8.5)),
                     text='Auctioning type:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))
    auctioning_type_dropdown = gui.create_dropdown_button(pygame, ui_manager,
                                                          opt_list=auctioning_types,
                                                          position=(int(left_offset * 6.0), int(top_offset * 8.5)),
                                                          size=(int(left_offset * 9.0), int(top_offset * 1.0)))
    current_auction_type = auctioning_type_dropdown.selected_option

    # pricing type
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 10.0)),
                     text='Start price type:',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))
    start_price_type_dropdown = gui.create_dropdown_button(pygame, ui_manager,
                                                           opt_list=start_price_types,
                                                           position=(int(left_offset * 6.0), int(top_offset * 10.0)),
                                                           size=(int(left_offset * 9.0), int(top_offset * 1.0)))
    current_pricing_type = start_price_type_dropdown.selected_option

    # bidding strategy
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 11.5)),
                     text='Bidding strategy',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    bidding_strategy_dropdown = gui.create_dropdown_button(pygame, ui_manager,
                                                           opt_list=bidding_strategy_types,
                                                           position=(int(left_offset * 6.0), int(top_offset * 11.5)),
                                                           size=(int(left_offset * 9.0), int(top_offset * 1.0)))
    current_bidding_strategy = bidding_strategy_dropdown.selected_option

    # output
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 1.0), int(top_offset * 13.0)),
                     text='Output',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    output_dropdown = gui.create_dropdown_button(pygame, ui_manager,
                                                           opt_list=output_types,
                                                           position=(int(left_offset * 6.0), int(top_offset * 13.0)),
                                                           size=(int(left_offset * 9.0), int(top_offset * 1.0)))
    current_output = output_dropdown.selected_option

def create_runtime_buttons():
    global execute_button
    global output_button
    execute_button = gui.create_button(pygame, ui_manager, text='Execute',
                                       size=(int(left_offset * 4.0), int(top_offset * 1.0)),
                                       position=(int(left_offset * 1.0), int(top_offset * 15)))

    output_button = gui.create_button(pygame, ui_manager, text='Output',
                                       size=(int(left_offset * 4.0), int(top_offset * 1.0)),
                                       position=(int(left_offset * 11.0), int(top_offset * 15)))


def execute_auction():
    global auction
    auction = Auction(current_auction_type,
                      current_pricing_type,
                      current_bidding_strategy,
                      number_buyers=n_buyers,
                      number_sellers=n_sellers,
                      number_rounds=n_rounds,
                      bid_increase_factor=bid_increase_factor,
                      bid_decrease_factor=bid_decrease_factor,
                      penalty_factor=refund_penalty_factor,
                      max_starting_price=max_starting_price,
                      )

    for _ in range(n_rounds):
        auction.execute_next_round()
    history = auction.get_market_history()
    create_image(history, n_rounds, n_sellers)
    auction_string = auction.__str__()
    output_console.html_text = '<font face=Montserrat size=5 color=#000000>{}</font>'.format(
        auction_string.replace('\n', '<br><br>'))
    output_console.rebuild()
    output_console.full_redraw()

def execute_output():
    global auction
    if auction is not None:
        auction_string = auction.specific_str(current_output)
        output_console.html_text = '<font face=Montserrat size=5 color=#000000>{}</font>'.format(
            auction_string.replace('\n', '<br><br>'))
        output_console.rebuild()
        output_console.full_redraw()

def create_image(history, nr, ns):
    df = pd.DataFrame(history)
    df.columns = ["Round " + str(i) for i in range(nr)]
    df = df.transpose()
    df.columns = ["Seller " + str(i) for i in range(ns)]
    print(df.describe())  # seller statistics
    # print(df[:])
    ax = df.plot(kind="area", title="Stacked seller profits per round")
    ax.set_xlabel("Round number")
    ax.set_ylabel("Cumulative Seller Profits")
    image_path = "data/images/graph_output/graph.png"
    plt.savefig(image_path)

    graph_img = pygame.image.load(image_path).convert_alpha()
    image_rect = image_display.rect

    graph_img = pygame.transform.smoothscale(graph_img,
                                             image_rect.size)

    image_display.set_image(graph_img)
    image_display.visible = True

    print("done?")


def set_n_random(id, upper):
    global n_buyers, n_sellers, n_rounds
    if id == "buyers":
        n_buyers = random.randint(1, upper)
        number_buyers_input.set_text(str(n_buyers))
    if id == "sellers":
        n_sellers = random.randint(1, upper)
        number_sellers_input.set_text(str(n_sellers))
    if id == "rounds":
        n_rounds = random.randint(1, upper)
        number_rounds_input.set_text(str(n_rounds))


def create_parameters_ui():
    global bid_increase_factor_input
    global bid_decrease_factor_input
    global refund_penalty_factor_input
    global max_starting_price_input
    global refund_penalty_factor_label

    gui.create_label(pygame, ui_manager, position=(left_offset * 15.5, int(top_offset * 0.7)),
                     size=(int(left_offset * 8.5), int(top_offset * 1.0)), text='Parameters')

    # bid increase
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 15.5), int(top_offset * 2.2)),
                     text='Bid Increase Factor',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    bid_increase_factor_input = gui.create_input(pygame, ui_manager,
                                                 size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                                 position=(int(left_offset * 20.5), int(top_offset * 2.5)))
    bid_increase_factor_input.set_text_length_limit(5)
    bid_increase_factor_input.set_text(str(bid_increase_factor))

    # bid decrease
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 15.5), int(top_offset * 3.7)),
                     text='Bid Decrease Factor',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    bid_decrease_factor_input = gui.create_input(pygame, ui_manager,
                                                 size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                                 position=(int(left_offset * 20.5), int(top_offset * 4.0)))
    bid_decrease_factor_input.set_text_length_limit(5)
    bid_decrease_factor_input.set_text(str(bid_decrease_factor))

    # refund penalty factor
    gui.create_label(pygame, ui_manager, position=(int(left_offset * 15.5), int(top_offset * 5.2)),
                     text='Max Starting Price',
                     size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    max_starting_price_input = gui.create_input(pygame, ui_manager,
                                                size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                                position=(int(left_offset * 20.5), int(top_offset * 5.5)))
    max_starting_price_input.set_text_length_limit(5)
    max_starting_price_input.set_allowed_characters('numbers')
    max_starting_price_input.set_text(str(max_starting_price))

    # max starting price
    refund_penalty_factor_label = gui.create_label(pygame, ui_manager,
                                                   position=(int(left_offset * 15.5), int(top_offset * 6.7)),
                                                   text='Refund Penalty Factor',
                                                   size=(int(left_offset * 4.0), int(top_offset * 1.0)))

    refund_penalty_factor_input = gui.create_input(pygame, ui_manager,
                                                   size=(int(left_offset * 3.0), int(top_offset * 0.6)),
                                                   position=(int(left_offset * 20.5), int(top_offset * 7.0)))
    refund_penalty_factor_input.set_text_length_limit(5)
    refund_penalty_factor_input.set_text(str(refund_penalty_factor))

    if auctioning_type_dropdown.selected_option != auction_leveled:
        refund_penalty_factor_label.visible = False
        refund_penalty_factor_input.visible = False


if __name__ == "__main__":
    init_settings()
    init_pygame()
    ui_manager = gui.init_ui(screen_size)
    output_console = gui.create_text_box(pygame, ui_manager, size=output_console_size, position=output_console_position)

    create_starting_conditions_ui()

    create_auction_settings_ui()

    create_runtime_buttons()

    create_parameters_ui()

    image_display = gui.create_image_display(pygame, ui_manager,
                                             image_path="data/images/graph_output/graph_56.png",
                                             size=(int(left_offset * 9.3), int(top_offset * 5.0)),
                                             position=(int(left_offset * 21.5), int(top_offset * 17.5)))

    running = True

    while running:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui_manager.process_events(event)

            if event.type == pygame.USEREVENT:
                test = 0
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == execute_button:
                        n_sellers = int(number_sellers_input.get_text())
                        n_buyers = int(number_buyers_input.get_text())
                        n_rounds = int(number_rounds_input.get_text())

                        bid_increase_factor = float(bid_increase_factor_input.get_text())
                        bid_decrease_factor = float(bid_decrease_factor_input.get_text())
                        refund_penalty_factor = float(refund_penalty_factor_input.get_text())
                        max_starting_price = int(max_starting_price_input.get_text())

                        execute_auction()
                    if event.ui_element == output_button:
                        execute_output()
                    if event.ui_element == randomize_n_buyers_button:
                        set_n_random("buyers", upper=20)
                    if event.ui_element == randomize_n_sellers_button:
                        set_n_random("sellers", upper=20)
                    if event.ui_element == randomize_n_rounds_button:
                        set_n_random("rounds", upper=999)


                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == auctioning_type_dropdown:
                        current_auction_type = auctioning_type_dropdown.selected_option
                        refund_penalty_factor_label.visible = (current_auction_type == auction_leveled)
                        refund_penalty_factor_input.visible = (current_auction_type == auction_leveled)
                    if event.ui_element == start_price_type_dropdown:
                        current_pricing_type = start_price_type_dropdown.selected_option
                    if event.ui_element == bidding_strategy_dropdown:
                        current_bidding_strategy = bidding_strategy_dropdown.selected_option

                # Input parsing
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    test = 0

        ui_manager.update(time_delta)

        screen.blit(background_surface, (0, 0))
        ui_manager.draw_ui(screen)

        pygame.display.update()
