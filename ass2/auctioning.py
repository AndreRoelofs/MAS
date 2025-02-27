from numpy import random
import numpy as np
from copy import copy
import matplotlib.pyplot as plt
import pandas as pd

auction_pure = "Pure"
auction_leveled = "Leveled"

auctioning_types = [
    auction_pure,
    auction_leveled
]

price_type_random = "Random"
price_type_own_good = "Own good"
price_type_common_good = "Common good"

start_price_types = [
    price_type_random,
    price_type_own_good,
    price_type_common_good,
]

bidding_standard = "Standard"
bidding_advanced = "Advanced"

bidding_strategy_types = [
    bidding_standard,
    bidding_advanced,
]

bidding_factor_random = "Random"
bidding_factor_constant = "Constant"

bidding_factor_types = [
    bidding_factor_random,
    bidding_factor_constant
]

output_all = "All"
output_buyer_statistics = "Buyer Statistics"
output_seller_statistics = "Seller Statistics"
output_market_prices = "Market Prices"
output_starting_prices = "Starting Prices"
output_buyer_profits = "Buyer Profits"
output_seller_profits = "Seller Profits"

output_types = [
    output_all,
    output_buyer_statistics,
    output_seller_statistics,
    output_market_prices,
    output_starting_prices,
    output_buyer_profits,
    output_seller_profits,
]


class Auction:
    n_sellers = None
    n_buyers = None
    n_rounds = None

    current_round_number = None

    sellers = None
    buyers = None
    rounds = None

    starting_prices = None
    market_history = None
    buyer_history = None
    seller_history = None
    market_price_analytics = None
    seller_statistics = None
    buyer_statistics = None

    def __init__(self,
                 auction_type,
                 start_price_type,
                 bidding_strategy,
                 bidding_factor_type,
                 number_sellers=2,
                 number_buyers=3,
                 number_rounds=2,
                 penalty_factor=0.1,
                 bid_increase_factor=1.2,
                 bid_decrease_factor=0.9,
                 price_increase_factor=1.2,
                 price_decrease_factor=0.9,
                 bidding_factor_value=5.0,
                 max_starting_price=100, ):
        self.n_sellers = number_sellers
        self.n_buyers = number_buyers
        self.n_rounds = number_rounds
        self.overbidders = 0
        self.underbidders = 0

        self.auction_type = auction_type
        self.start_price_type = start_price_type
        self.bidding_strategy = bidding_strategy
        self.bidding_factor_type = bidding_factor_type
        self.max_starting_price = max_starting_price

        self.current_round_number = 0
        self.penalty_factor = penalty_factor
        self.bid_increase_factor = bid_increase_factor
        self.bid_decrease_factor = bid_decrease_factor
        self.price_increase_factor = price_increase_factor
        self.price_decrease_factor = price_decrease_factor
        self.bidding_factor_value = bidding_factor_value

        self.initialize_sellers()
        self.initialize_buyers()
        self.initialize_rounds()

        self.starting_prices = np.zeros(number_sellers)
        self.market_history = np.zeros((number_sellers, number_rounds))
        self.previous_starting_price = np.zeros(number_sellers)
        self.common_profit_factor = np.zeros(number_sellers)
        self.buyer_history = np.zeros((number_buyers, number_rounds))
        self.seller_history = np.zeros((number_sellers, number_rounds))
        self.market_price_analytics = ""


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
                number_sellers=self.n_sellers,
                bidding_strategy=self.bidding_strategy,
                sampling=self.bidding_factor_type,
                value=self.bidding_factor_value
            ))

    def initialize_rounds(self):
        self.rounds = []
        for i in range(self.n_rounds):
            self.rounds.append(Round(id=i, buyers=self.buyers))

    def execute_next_round(self):
        current_round = self.rounds[self.current_round_number]
        winners = []
        item_tracker = 0
        # add items to the round
        for seller in self.sellers:
            current_round.available_items.append(seller.get_random_item(self.previous_starting_price[seller.id], self.common_profit_factor[seller.id], self.max_starting_price, self.start_price_type, self.price_decrease_factor, self.price_increase_factor, self.overbidders, self.underbidders, current_round.id))

        # reset buyer current profits
        for buyer in self.buyers:
            buyer.reset_current_profits()

        # place bids on items
        for item in current_round.available_items:
            if current_round.id == 0:
                self.starting_prices[item_tracker] = item.starting_price
                item_tracker += 1
            if len(current_round.available_buyers) == 0:
                continue
            item.reset_current_bids()
            for buyer in current_round.available_buyers:
                item.add_bid(buyer)
            # compute market price of the item & add to the history for statistical purposes
            item.calculate_market_price()
            self.market_history[item.seller.id][current_round.id] = item.get_market_price()

            self.previous_starting_price[item.seller.id] = item.starting_price
            self.common_profit_factor[item.seller.id] = (item.market_price[0] - item.starting_price)/item.starting_price

            # determine the winner
            winner_id, winner_payout = item.get_winner_id_and_payout()

            if winner_id is not None:
                winner = self.buyers[winner_id]

                # calculate seller profit
                seller_profit = winner_payout - item.starting_price
                item.seller.profit += seller_profit

                # calculate buyer profit
                buyer_profit = winner.increase_profit(item, winner_payout)

                # decide which one to decommit
                if self.auction_type == auction_leveled and winner in winners:
                    worst_buy = winner.get_least_profitable_buy()
                    fee = self.penalty_factor * worst_buy['winner_payout']

                    if buyer_profit - fee > worst_buy['profit']:
                        worst_buy['item'].seller.profit += fee
                        worst_buy['item'].seller.profit -= worst_buy['winner_payout'] - worst_buy['starting_price']

                        winner.profit -= fee
                        winner.profit -= worst_buy['profit']
                        winner.remove_worst_buy()
                    else:
                        fee = self.penalty_factor * winner_payout
                        item.seller.profit += fee
                        item.seller.profit -= seller_profit

                        winner.profit -= fee
                        winner.profit -= buyer_profit

                winners.append(winner)

                if self.auction_type == auction_pure:
                    # remove winning buyer from the available buyers
                    current_round.available_buyers.pop(current_round.available_buyers.index(winner))

            # remove sold item from seller's stock
            item.seller.remove_item_from_stock(item)

            if self.bidding_strategy == bidding_advanced and "winner" in locals():
                self.change_bidding_factors(winner, item)

        for seller in self.sellers:
            print("Seller: {} earned a profit of {} after round {}"
                  .format(seller.id, np.around(seller.profit, 2), self.current_round_number))
            if current_round.id == 0:
                self.seller_history[seller.id][current_round.id] = seller.profit
            else:
                self.seller_history[seller.id][current_round.id] = seller.profit - np.sum(self.seller_history[seller.id][:-1])

        print("")

        for buyer in self.buyers:
            print("Buyer: {} earned a profit of {} after round {}"
                  .format(buyer.id, np.around(buyer.profit, 2), self.current_round_number))
            if current_round.id == 0:
                self.buyer_history[buyer.id][current_round.id] = buyer.profit
            else:
                self.buyer_history[buyer.id][current_round.id] = buyer.profit - np.sum(self.buyer_history[buyer.id][:-1])

        print("")

        if current_round.id > 0:
            for seller in self.sellers:
                first_market_price = self.market_history[seller.id][0]
                previous_market_price = self.market_history[seller.id][
                    current_round.id - 1 if current_round.id > 0 else 0]
                current_market_price = self.market_history[seller.id][current_round.id]
                if first_market_price != 0:
                    start_to_round_change = round((current_market_price / first_market_price) * 100, 2)
                else:
                    start_to_round_change = 0.00
                one_step_change = round(current_market_price - previous_market_price, 2)

                print("Market price for seller {s} changed by {mp}"
                      .format(s=seller.id, mp=one_step_change))

                if current_round.id > 0:
                    print("Market price for seller {s} now is {mp}% of first round\n"
                          .format(s=seller.id, mp=start_to_round_change))
                    self.market_price_analytics += "Round {r}: Seller {s} profit changed by {mp}%\n" \
                        .format(r=current_round.id, s=seller.id, mp=start_to_round_change)

        print("_______________________________________________\n")

        self.current_round_number += 1

    def change_bidding_factors(self, winner, item):
        seller = item.seller
        overbidders_ids = item.get_overbidders_ids()
        underbidders_ids = item.get_underbidders_ids()
        self.overbidders = len(overbidders_ids)
        self.underbidders = len(underbidders_ids)

        for id in overbidders_ids:
            buyer = self.buyers[int(id)]
            buyer.change_bidding_by_factor(seller, self.bid_decrease_factor)

        for id in underbidders_ids:
            buyer = self.buyers[int(id)]
            if buyer is winner:
                buyer.change_bidding_by_factor(seller, self.bid_decrease_factor)
            else:
                buyer.change_bidding_by_factor(seller, self.bid_increase_factor)

    def get_market_history(self):
        return self.market_history

    def __str__(self):
        item_starting_price_string = ""
        buyer_history_string = ""
        seller_history_string = ""
        df_sellers = pd.DataFrame(self.market_history)
        df_sellers.columns = ["Round " + str(i) for i in range(len(self.rounds))]
        df_sellers = df_sellers.transpose()
        df_sellers.columns = ["Seller " + str(i) for i in range(len(self.sellers))]
        self.seller_statistics = ""
        df_buyers = pd.DataFrame(self.buyer_history)
        df_buyers.columns = ["Round " + str(i) for i in range(len(self.rounds))]
        df_buyers = df_buyers.transpose()
        df_buyers.columns = ["Buyer " + str(i) for i in range(len(self.buyers))]
        self.buyer_statistics = ""
        temp = len(self.starting_prices)
        for i in range(temp):
            if(temp < 100):
                item_starting_price_string += "Item {} Starting Price:\n<i>{}</i>\n".format(i, np.around(
                    self.starting_prices[i], 2))
        temp = len(self.buyer_history)
        rounds = len(self.buyer_history[0])
        for i in range(temp):
            for j in range(rounds):
                if(rounds < 100 or j%10==0):
                    buyer_history_string += "Buyer {} Profit:\nRound {}: <i>{}</i>\n".format(i, j, np.around(
                        self.buyer_history[i][j], 2))
        temp = len(self.seller_history)
        rounds = len(self.seller_history[0])
        for i in range(temp):
            for j in range(rounds):
                if(rounds < 100 or j%10==0):
                    seller_history_string += "Seller {} Profit:\nRound {}: <i>{}</i>\n".format(i, j, np.around(
                     self.seller_history[i][j], 2))

        temp = len(self.sellers)
        for i in range(temp):
            values = df_sellers.iloc[:, i]
            values = [values.mean(), values.std(), values.min(), values.max()]
            self.seller_statistics += "Seller {}:\nMean profit: <i>{}</i>\nStandard deviation: <i>{}</i>\nMin profit: <i>{}</i>\nMax profit:  <i>{}</i>\n".format(
                i, np.around(values[0], 2), np.around(values[1], 2), np.around(values[2], 2), np.around(values[3], 2))

        temp = len(self.buyers)
        for i in range(temp):
            values = df_buyers.iloc[:, i]
            values = [values.mean(), values.std(), values.min(), values.max()]
            self.buyer_statistics += "Buyer {}:\nMean profit: <i>{}</i>\nStandard deviation: <i>{}</i>\nMin profit: <i>{}</i>\nMax profit:  <i>{}</i>\n".format(
                i, np.around(values[0], 2), np.around(values[1], 2), np.around(values[2], 2), np.around(values[3], 2))

        output = "<b>Starting prices:</b>\n{}\n<b>Buyer profits over rounds:</b>\n{}\n<b>Buyer statistics</b>:\n{}\n<b>Seller profits over rounds:</b>\n{}\n<b>Seller analytics:</b>\n{}\n<b>Seller statistics</b>:\n{}".format(
            item_starting_price_string, buyer_history_string, self.buyer_statistics, seller_history_string,
            self.market_price_analytics, self.seller_statistics)

        return output

    def specific_str(self, type):
        output = ""
        temp = 0
        rounds = 0
        if type == output_seller_statistics:
            df_sellers = pd.DataFrame(self.market_history)
            df_sellers.columns = ["Round " + str(i) for i in range(len(self.rounds))]
            df_sellers = df_sellers.transpose()
            df_sellers.columns = ["Seller " + str(i) for i in range(len(self.sellers))]
            self.seller_statistics = ""
            temp = len(self.sellers)
            for i in range(temp):
                values = df_sellers.iloc[:, i]
                values = [values.mean(), values.std(), values.min(), values.max()]
                self.seller_statistics += "Seller {}:\nMean profit: <i>{}</i>\nStandard deviation: <i>{}</i>\nMin profit: <i>{}</i>\nMax profit:  <i>{}</i>\n".format(
                    i, np.around(values[0], 2), np.around(values[1], 2), np.around(values[2], 2),
                    np.around(values[3], 2))
            output = "<b>Seller statistics:</b>\n{}".format(self.seller_statistics)

        if type == output_buyer_statistics:
            df_buyers = pd.DataFrame(self.buyer_history)
            df_buyers.columns = ["Round " + str(i) for i in range(len(self.rounds))]
            df_buyers = df_buyers.transpose()
            df_buyers.columns = ["Buyer " + str(i) for i in range(len(self.buyers))]
            self.buyer_statistics = ""
            temp = len(self.buyers)
            for i in range(temp):
                values = df_buyers.iloc[:, i]
                values = [values.mean(), values.std(), values.min(), values.max()]
                self.buyer_statistics += "Buyer {}:\nMean profit: <i>{}</i>\nStandard deviation: <i>{}</i>\nMin profit: <i>{}</i>\nMax profit:  <i>{}</i>\n".format(
                    i, np.around(values[0], 2), np.around(values[1], 2), np.around(values[2], 2),
                    np.around(values[3], 2))
            output = "<b>Buyer statistics:</b>\n{}".format(self.buyer_statistics)

        if type == output_market_prices:
            output = "<b>Seller analytics:</b>\n{}".format(self.market_price_analytics)

        if type == output_starting_prices:
            output = ""
            temp = len(self.starting_prices)
            for i in range(temp):
                output += "Item {} Starting Price:\n<i>{}</i>\n".format(i, np.around(
                    self.starting_prices[i], 2))

        if type == output_buyer_profits:
            output = "<b>Buyer profits:</b>\n"
            temp = len(self.buyer_history)
            rounds = len(self.buyer_history[0])
            for i in range(temp):
                for j in range(rounds):
                    if(rounds < 100 or j%10==0):
                        output += "Buyer {} Profit:\nRound {}: <i>{}</i>\n".format(i, j, np.around(
                            self.buyer_history[i][j], 2))

        if type == output_seller_profits:
            output = "<b>Seller profits:</b>\n"
            temp = len(self.seller_history)
            rounds = len(self.seller_history[0])
            for i in range(temp):
                for j in range(rounds):
                    if(rounds < 100 or j%10==0):
                        output += "Seller {} Profit:\nRound {}: <i>{}</i>\n".format(i, j, np.around(
                            self.seller_history[i][j], 2))

        if type == output_all:
            output = self.__str__()

        return output


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
            item.set_starting_price(random.randint(0, max_starting_price))
            self.items_stock.append(item)

    def get_random_item(self, previous_start_price, common_profit_factor, max_starting_price, seller_strategy, price_decrease, price_increase, overbidders, underbidders, round):
        # create new item
        # calculate price based on strategy
        item = random.choice(self.items_stock)

        if True:
            return item

        if previous_start_price == 0:
            return item

        start_price = previous_start_price

        if common_profit_factor < 1:
            start_price *= common_profit_factor

        if seller_strategy == price_type_own_good:
            start_price *= price_increase if overbidders > underbidders else 1
        if seller_strategy == price_type_common_good:
            start_price *= price_increase * (overbidders-underbidders) if overbidders > underbidders else price_decrease*(underbidders - overbidders) if overbidders < underbidders else 1
        item.starting_price = min(start_price, max_starting_price)
        return item

    def remove_item_from_stock(self, item):
        self.items_stock.pop(self.items_stock.index(item))
        self.items_sold.append(item)



class Buyer:
    id = None
    profit = 0.0
    current_profits = None
    bidding_factors = None
    bidding_strategy = None

    def __init__(self, id, number_sellers, bidding_strategy, sampling, value):
        self.id = id
        self.items_bought = []
        self.current_profits = []
        self.bidding_strategy = bidding_strategy

        self.initialize_bidding_factors(number_sellers, sampling, value)

    def reset_current_profits(self):
        self.current_profits = []

    def initialize_bidding_factors(self, number_sellers, sampling, value):
        self.bidding_factors = []
        if sampling == bidding_factor_random:
            for i in range(number_sellers):
                self.bidding_factors.append(random.uniform(1.0, value))
        if sampling == bidding_factor_constant:
            for i in range(number_sellers):
                self.bidding_factors.append(value)

    def calculate_bid(self, item):
        seller_id = item.seller.id
        bidding_factor = self.bidding_factors[seller_id]
        bid = bidding_factor * item.starting_price

        return bid

    def increase_profit(self, item, winner_payout):
        profit = item.get_market_price() - winner_payout
        self.current_profits.append({
            'item': item,
            'market_price': item.get_market_price(),
            'winner_payout': winner_payout,
            'profit': profit,
            'starting_price': item.starting_price
        })
        self.profit += profit
        return profit

    def get_least_profitable_buy(self):
        worst_buy = sorted(self.current_profits, key=lambda x: x['profit'])[0]
        return worst_buy

    def remove_worst_buy(self):
        worst_buy = sorted(self.current_profits, key=lambda x: x['profit'])[0]
        self.current_profits.remove(worst_buy)


    def change_bidding_by_factor(self, seller, factor):
        self.bidding_factors[seller.id] = max(self.bidding_factors[seller.id] * factor, 1)


class Item:
    starting_price = None
    market_price = None  # price per round
    current_bids = None  # tuples of buyer_id and bid
    seller = None
    buyer = None

    def __init__(self, seller):
        self.seller = seller
        self.market_price = []
        self.market_history = []
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

    def get_winner_id_and_payout(self):
        current_market_price = self.get_market_price()
        eligible_buyers = self.current_bids[self.current_bids[:, 1] <= current_market_price]
        eligible_buyers = eligible_buyers[eligible_buyers[:, 1].argsort()[::-1]]

        if len(eligible_buyers) == 0:
            return None, None

        winner_id = eligible_buyers[0][0]

        if eligible_buyers.shape[0] > 1:
            winner_payout = eligible_buyers[1][1]
        else:
            winner_payout = (eligible_buyers[0][1] + self.starting_price) / 2

        return int(winner_id), winner_payout

    def get_overbidders_ids(self):
        current_market_price = self.get_market_price()
        return self.current_bids[self.current_bids[:, 1] >= current_market_price][:, 0]

    def get_underbidders_ids(self):
        current_market_price = self.get_market_price()
        return self.current_bids[self.current_bids[:, 1] < current_market_price][:, 0]

    def get_market_price(self, round_number=None):
        if round_number is None:
            return self.market_price[-1]
        else:
            return self.market_price[round_number]


if __name__ == "__main__":
    n_sellers = 6
    n_buyers = 5
    n_rounds = 10

    # auction = Auction(auction_pure, price_type_random)
    auction = Auction(auction_pure,
                      price_type_random,
                      bidding_advanced,
                      number_buyers=n_buyers,
                      number_sellers=n_sellers,
                      number_rounds=n_rounds)

    for _ in range(n_rounds):
        auction.execute_next_round()
    history = auction.get_market_history()
    for seller in auction.sellers:
        print('Seller ', seller.id, end=' || ')
        seller_history = history[seller.id]
        for i in range(n_rounds):
            print(round(seller_history[i]), end='\t| ')
        print()

    df = pd.DataFrame(history)
    df.columns = ["Round " + str(i) for i in range(n_rounds)]
    df = df.transpose()
    df.columns = ["Seller " + str(i) for i in range(n_sellers)]
    print(df.describe())  # seller statistics
    # print(df[:])
    ax = df.plot(kind="area", title="Stacked seller profits per round")
    ax.set_xlabel("Round number")
    ax.set_ylabel("Cumulative Seller Profits")
    plt.show()

    print(auction)
