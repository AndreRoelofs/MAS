import numpy as np
import random
import time
import copy

class Situation:
    def __init__(self,voter_num,candidate_num,voting_scheme="Voting for one"):
        self.voter_num = voter_num
        self.candidate_num = candidate_num
        self.voting_scheme = voting_scheme
        self.candidates = Candidates(self.candidate_num)
        self.voters = [Voter(self.candidates.num,
        voting_scheme = self.voting_scheme) for i in range(self.voter_num)]
        self.situation = np.zeros((self.voter_num,self.candidate_num))
        for i in range(self.voter_num):
            self.situation[i] = self.voters[i].preference
        self.situation = self.situation.T
        self.GetOutcome()

    def GetOutcome(self):
        for voter in self.voters:
            self.candidates.outcome = np.sum([self.candidates.outcome,voter.vote],axis = 0)

    def Print(self):
        print("the situation now is \n{}\n".format(self.situation))
        self.candidates.Print()
        for voter in self.voters:
            voter.Print()

class Voter:
    def __init__(self,candidates_num,preference=None,
    vote_order=None,voting_scheme = "Voting for one"):
        self.candidates_num = candidates_num
        self.preference = preference
        self.vote_order = vote_order
        self.voting_scheme = voting_scheme
        self.vote = [0 for i in range(self.candidates_num)]
        if self.preference is None:
            self.SetPreference()
        if self.vote_order is None:
            self.SetVotingStrategy()
        self.GetVote()

    def SetPreference(self):
        self.preference = [i for i in range(self.candidates_num)]
        random.shuffle(self.preference)

    def SetVotingStrategy(self):
        self.vote_order = copy.copy(self.preference) #voting order is the same as preference

    def GetVote(self):
        if self.voting_scheme == "Voting for one":
            self.vote[self.vote_order[0]] = 1
        if self.voting_scheme == "Voting for two":
            self.vote[self.vote_order[0]] = 1
            self.vote[self.vote_order[1]] = 1
        if self.voting_scheme == "Veto voting":
            self.vote = [1 for i in range(self.candidates_num)]
            self.vote[self.vote_order[-1]] = 0
        if self.voting_scheme == "Borda voting":
            for i in range(self.candidates_num):
                self.vote[self.vote_order[i]] = self.candidates_num-1-i

    def Print(self):
        print("Voter: candidates_num {}\npreference {}\nvote_order {}\
        \nvoting_scheme {}\nvote {}\n".format(
        self.candidates_num,self.preference,self.vote_order,
        self.voting_scheme,self.vote))

class Candidates:
    def __init__(self,num):
        self.num = num
        self.ids = [i for i in range(self.num)]
        self.outcome = [0 for i in range(self.num)]

    def Print(self):
        print("Candidates: num {}\nids {}\noutcome {}\n".format(
        self.num,self.ids,self.outcome))

if __name__ == "__main__":
    voting_schemes = [
        'Voting for one',
        'Voting for two',
        'Veto voting',
        'Borda voting',
    ]
    s = Situation(1,4,voting_scheme='Borda voting')
    s.Print()
