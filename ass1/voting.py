import numpy as np
import random
import time
import copy

class Situation:
    def __init__(self,voter_num,candidate_num):
        self.voter_num = voter_num
        self.candidate_num = candidate_num
        self.candidates = Candidates(self.candidate_num)
        self.voters = [Voter(self.candidates.num) for i in range(self.voter_num)]
    def print(self):
        print("the situation now is \n")
        self.candidates.print()
        for voter in self.voters:
            voter.print()

class Voter:
    def __init__(self,candidates_num,preference=None,vote_order=None):
        self.candidates_num = candidates_num
        self.preference = preference
        self.vote_order = vote_order
        if self.preference is None:
            self.set_preference()
            self.set_voting_strategy()

    def set_preference(self):
        self.preference = [i for i in range(self.candidates_num)]
        random.shuffle(self.preference)

    def set_voting_strategy(self):
        self.vote_order = copy.copy(self.preference) #voting order is the same as preference

    def print(self):
        print("Voter: candidates_num {}\npreference {}\nvote_order {}\n".format(
        self.candidates_num,self.preference,self.vote_order))

class Candidates:
    def __init__(self,num):
        self.num = num
        self.ids = [i for i in range(self.num)]
        self.outcome = [0 for i in range(self.num)]

    def print(self):
        print("Candidates: num {}\nids {}\noutcome {}\n".format(
        self.num,self.ids,self.outcome))

if __name__ == "__main__":
    c = Candidates(4)
    c.print()
    v = Voter(c.num)
    v.print()
    s = Situation(2,4)
    s.print()
