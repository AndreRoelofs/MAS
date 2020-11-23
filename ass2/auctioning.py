from numpy import random
import numpy as np
from copy import copy

auction_pure = "Pure"
auction_leveled = "Leveled"

price_type_random = "Random"
price_type_own_good = "Own good"
price_type_common_good = "Common good"

auctioning_types = [
    auction_pure,
    auction_leveled
]

start_price_types = [
    price_type_random,
    price_type_own_good,
    price_type_common_good,
]


class Auction:
    n_sellers = None
    n_buyers = None
    n_rounds = None

    current_round_number = None

    sellers = None
    buyers = None
    rounds = None

    def __init__(self,
                 auction_type,
                 start_price_type,
                 number_sellers=2,
                 number_buyers=3,
                 number_rounds=2,
                 penalty_factor=0.1,
                 max_starting_price=100):
        self.n_sellers = number_sellers
        self.n_buyers = number_buyers
        self.n_rounds = number_rounds

        self.auction_type = auction_type
        self.start_price_type = start_price_type
        self.max_starting_price = max_starting_price

        self.current_round_number = 0
        self.penalty_factor = penalty_factor

        self.initialize_sellers()
        self.initialize_buyers()
        self.initialize_rounds()

    def initialize_sellers(self):
        self.sellers = []
        for i in range(self.n_sellers):
            self.sellers.append(Seller(
                id=i,
                n_items=self.n_rounds,
                start_price_type=self.start_price_type,
                max_starting_price=self.max_starting_price))

    def initialize_buyers(self):
        self.buyers = []
        for i in range(self.n_buyers):
            self.buyers.append(Buyer(
                id=i,
                number_sellers=self.n_sellers
            ))

    def initialize_rounds(self):
        self.rounds = []
        for i in range(self.n_rounds):
            self.rounds.append(Round(id=i, buyers=self.buyers))

    def execute_next_round(self):
        current_round = self.rounds[self.current_round_number]
        winners = []
        # add items to the round
        for seller in self.sellers:
            current_round.available_items.append(seller.get_random_item())

        # reset buyer current profits
        for buyer in self.buyers:
            buyer.reset_current_profits()

        # place bids on items
        for item in current_round.available_items:
            item.reset_current_bids()
            for buyer in current_round.available_buyers:
                item.add_bid(buyer)
            # compute market price of the item
            item.calculate_market_price()

            # determine the winner
            winner_id, winner_payout = item.get_winner_id_and_payout()
            winner = self.buyers[winner_id]

            # calculate seller profit
            item.seller.profit += winner_payout - item.starting_price

            # calculate buyer profit
            winner.increase_profit(item, winner_payout)

            # decide which one to decommit
            if self.auction_type == auction_leveled and winner in winners:

                worst_buy = winner.get_least_profitable_buy()
                fee = self.penalty_factor * worst_buy['winner_payout']

                item.seller.profit += fee
                winner.profit -= fee

            winners.append(winner)

            if self.auction_type == auction_pure:
                # remove winning buyer from the available buyers
                current_round.available_buyers.pop(current_round.available_buyers.index(winner))

            # remove sold item from seller's stock
            item.seller.remove_item_from_stock(item)

        for seller in self.sellers:
            print("Seller: {} earned a profit of {} after round {}"
                  .format(seller.id, np.around(seller.profit, 2), self.current_round_number))

        print("")

        for buyer in self.buyers:
            print("Buyer: {} earned a profit of {} after round {}"
                  .format(buyer.id, np.around(buyer.profit, 2), self.current_round_number))

        print("")

        print("TODO: Item market price development across rounds")

        print("_______________________________________________\n")

        self.current_round_number += 1


class Round:
    id = None
    available_items = None
    available_buyers = None

    def __init__(self, id, buyers):
        self.id = id
        self.available_items = []
        self.available_buyers = copy(buyers)

    def add_item(self, item):
        self.available_items.append(item)

    def set_available_buyers(self, buyers):
        self.available_buyers = buyers


class Seller:
    id = None
    items_stock = None
    items_sold = None
    profit = 0.0

    def __init__(self, id, n_items, start_price_type, max_starting_price):
        self.id = id
        self.items_stock = []
        self.items_sold = []

        self.initialize_items(n_items, start_price_type, max_starting_price)

    def initialize_items(self, n_items, start_price_type, max_starting_price):
        for i in range(n_items):
            item = Item(seller=self)
            if start_price_type == price_type_random:
                item.set_starting_price(random.randint(0, max_starting_price))
            self.items_stock.append(item)

    def get_random_item(self):
        return random.choice(self.items_stock)

    def remove_item_from_stock(self, item):
        self.items_stock.pop(self.items_stock.index(item))
        self.items_sold.append(item)


class Buyer:
    id = None
    profit = 0.0
    current_profits = None
    bidding_factors = None

    def __init__(self, id, number_sellers):
        self.id = id
        self.items_bought = []
        self.current_profits = []

        self.initialize_bidding_factors(number_sellers)

    def reset_current_profits(self):
        self.current_profits = []

    def initialize_bidding_factors(self, number_sellers):
        self.bidding_factors = []
        for i in range(number_sellers):
            self.bidding_factors.append(random.uniform(1.0, 5.0))

    def calculate_bid(self, item):
        seller_id = item.seller.id
        bidding_factor = self.bidding_factors[seller_id]

        return bidding_factor * item.starting_price

    def increase_profit(self, item, winner_payout):
        profit = item.get_market_price() - winner_payout
        self.current_profits.append({
            'item': item,
            'market_price': item.get_market_price(),
            'winner_payout': winner_payout,
            'profit': profit
        })
        self.profit += profit

    def get_least_profitable_buy(self):
        return sorted(self.current_profits, key=lambda x: x['profit'])[0]



class Item:
    starting_price = None
    market_price = None  # price per round
    current_bids = None  # tuples of buyer_id and bid
    seller = None
    buyer = None

    def __init__(self, seller):
        self.seller = seller
        self.market_price = []
        self.current_bids = []

    def set_starting_price(self, price):
        self.starting_price = price

    def reset_current_bids(self):
        self.current_bids = []

    def add_bid(self, buyer):
        self.current_bids.append([buyer.id, buyer.calculate_bid(self)])

    def calculate_market_price(self):
        self.current_bids = np.array(self.current_bids)
        self.market_price.append(np.average(self.current_bids[:, 1]))

    def get_winner_id_and_payout(self, round_number=None):
        current_market_price = self.get_market_price(round_number)
        eligible_buyers = self.current_bids[self.current_bids[:, 1] <= current_market_price]
        eligible_buyers = eligible_buyers[eligible_buyers[:, 1].argsort()[::-1]]

        winner_id = eligible_buyers[0][0]

        if eligible_buyers.shape[0] > 1:
            winner_payout = eligible_buyers[1][1]
        else:
            winner_payout = eligible_buyers[0][1]

        return int(winner_id), winner_payout

    def get_market_price(self, round_number=None):
        if round_number is None:
            return self.market_price[-1]
        else:
            return self.market_price[round_number]


if __name__ == "__main__":
    n_sellers = 5
    n_buyers = 10
    n_rounds = 1

    # auction = Auction(auction_pure, price_type_random)
    auction = Auction(auction_leveled, price_type_random)
    auction.execute_next_round()
    auction.execute_next_round()
