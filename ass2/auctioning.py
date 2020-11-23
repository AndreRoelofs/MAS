from numpy import random

auctioning_types = [
    "Pure",
    "Leveled"
]

start_price_type = [
    "Random",
    "Own good",
    "Common good",
]

class Round:
    available_items = None
    available_buyers = None

    def __init__(self):
        test = 0

class Seller:
    id = None
    items_to_sell = None
    items_sold = None

    def __init__(self):
        test = 0

class Buyer:
    id = None
    items_bought = None  # 2D array, seller x items

    def __init__(self):
        test = 0


class Item:
    starting_price = None
    market_price = None  # price per round
    seller = None
    buyer = None

    def __init__(self):
        test = 0


