import numpy as np
import random
import time
from copy import copy


class Situation:
    def __init__(self, preference_matrix):
        self.voter_num = len(preference_matrix)
        self.candidate_num = len(preference_matrix[0])
        self.preference_matrix = preference_matrix

        self.candidates = None
        self.agenda = None
        self.round_winner = None
        self.voting_strategy = ''
        self.voters = None
        self.voting_scheme = ''
        self.candidates_outcome = None
        self.strategic_voting_options = None
        self.overall_happiness = 0.0


        self.reset_situation()

    def calculate_outcome(self, voting_scheme, agenda=None):
        self.voting_scheme = voting_scheme

        if voting_scheme == 'Round voting':
            self.round_winner = self.candidates[0]
            for i in range(1, len(agenda)):
                participants = [self.round_winner, self.candidates[i]]
                for voter in self.voters:
                    voter.vote_round(voting_scheme, participants)
                if self.round_winner.score < self.candidates[i].score:
                    self.round_winner.score = 0
                    self.round_winner = self.candidates[i]
                self.round_winner.score = 0
                self.candidates[i].score = 0
        else:
            for voter in self.voters:
                voter.vote(voting_scheme, self.voting_strategy == 'Bullet voting')
            self.candidates_outcome = sorted(self.candidates, key=lambda c: c.score, reverse=True)

        for voter in self.voters:
            voter.calculate_happiness(self.candidates_outcome)

        self.calculate_overall_happiness()

    def create_stategic_option(self, voter):
        return [
            voter.id,
            [c.id for c in voter.vote_order],
            self.candidates_outcome[0].id,
            self.overall_happiness,
            'test z'
        ]

    def apply_compromising(self):
        for i in range(self.voter_num):
            voter = self.voters[i]
            for k in range(1, self.candidate_num):
                for l in range(k, 0, -1):
                    preference_vector = voter.get_preference_vector()
                    preference_vector.insert(k, preference_vector.pop(k - l))

                    voter.set_vote_order(preference_vector)

                    self.calculate_outcome(voting_for_one)

                    self.strategic_voting_options.append(self.create_stategic_option(voter))

                voter.set_vote_order(voter.get_preference_vector())

    def apply_burying(self):
        for i in range(self.voter_num):
            voter = self.voters[i]
            for k in range(0, self.candidate_num):
                for l in range(k + 1, self.candidate_num):
                    preference_vector = voter.get_preference_vector()
                    preference_vector.insert(k, preference_vector.pop(k - l))

                    voter.set_vote_order(preference_vector)

                    self.calculate_outcome(voting_for_one)

                    self.strategic_voting_options.append(self.create_stategic_option(voter))

                voter.set_vote_order(voter.get_preference_vector())

    def apply_voting_strategy(self, voting_strategy):
        self.reset_situation()
        self.strategic_voting_options = []
        self.voting_strategy = voting_strategy

        if voting_strategy == 'Compromising':
            self.apply_compromising()
            self.reset_situation()
        if voting_strategy == 'Burying':
            self.apply_burying()
            self.reset_situation()
        if voting_strategy == 'Bullet voting':
            self.calculate_outcome(self.voting_scheme)



    def set_preference_matrix(self, preference_matrix):
        self.preference_matrix = preference_matrix

    def reset_situation(self):
        self.overall_happiness = 0.0
        self.candidates = self.create_candidates(self.candidate_num)
        self.voters = self.create_voters(self.voter_num, self.candidates)
        self.candidates_outcome = None
        self.assign_preferences(self.preference_matrix)

    def calculate_overall_happiness(self):
        self.overall_happiness = 0.0
        for voter in self.voters:
            self.overall_happiness += voter.happiness

    def create_voters(self, voter_num, candidates):
        return [Voter(
            voter_id=i,
            candidates=candidates,
        ) for i in range(voter_num)]

    def create_candidates(self, candidate_num):
        return [Candidate(
            candidate_id=i,
        ) for i in range(candidate_num)]

    def assign_preferences(self, preference_matrix):
        for i in range(len(preference_matrix)):
            voter = self.voters[i]
            preference_vector = preference_matrix[i]
            voter.set_preference(preference_vector)

    def print_output(self):
        for voter in self.voters:
            voter.print_output()
            print("\n")
        print("Candidate {} won with a score of {}".format(self.candidates_outcome[0].id,
                                                           self.candidates_outcome[0].score))
        print("Overall voter happiness is {}".format(self.overall_happiness))

    def print_strategic_voting_options(self):
        print("Applying strategy: {}".format(self.voting_strategy))
        for option in self.strategic_voting_options:
            v_id, v, O, H, z = option
            print("v_id: {}, v: {}, O^~: {}, H^~: {}, z: {}".format(v_id, v, O, H, z))


class Voter:
    def __init__(self,
                 voter_id,
                 candidates,
                 ):
        self.id = voter_id
        self.preferences = candidates
        self.vote_order = candidates
        self.happiness = 0.0

    def set_preference(self, preference_vector):
        new_preferences = []

        for idx in preference_vector:
            candidate = self.preferences[idx]
            new_preferences.append(candidate)

        self.preferences = new_preferences
        self.vote_order = copy(self.preferences)

    def get_preference_vector(self):
        return np.arange(0, len(self.preferences), 1).tolist()

    def calculate_happiness(self, candidates_outcome):
        total_distance = 0
        reversed_outcome = list(reversed(candidates_outcome))
        k = 1
        for candidate in list(reversed(self.preferences)):
            j = reversed_outcome.index(candidate) + 1
            total_distance += (k - j) * j
            k += 1
        self.happiness = 1 / (1 + abs(total_distance))

    def set_vote_order(self, preference_vector):
        new_vote_order = []

        for idx in preference_vector:
            candidate = self.preferences[idx]
            new_vote_order.append(candidate)

        self.vote_order = new_vote_order

    def vote(self, voting_scheme, bullet_voting=False):
        if voting_scheme == "Voting for one":
            self.vote_order[0].score += 1
        if voting_scheme == "Voting for two":
            self.vote_order[0].score += 1
            if bullet_voting:
                return
            self.vote_order[1].score += 1
        if voting_scheme == 'Veto voting':
            for i in range(len(self.vote_order) - 1):
                self.vote_order[i].score += 1
                if bullet_voting:
                    return
        if voting_scheme == 'Borda voting':
            candidate_num = len(self.vote_order)
            for i in range(len(self.vote_order)):
                self.vote_order[i].score += candidate_num-1-i
                if bullet_voting:
                    return

    def vote_round(self, voting_scheme, round_participants):
        if voting_scheme == "Voting for one":
            for candidate in self.vote_order:
                if candidate in round_participants:
                    candidate.score += 1
                    return

    def print_output(self):
        print("Voter: ", self.id)
        print("True preference: ", [c.id for c in self.preferences])
        print("Adjusted preference: ", [c.id for c in self.vote_order])
        # print("Vote: ", self.vote)
        print("Happiness: ", self.happiness)


class Candidate:
    def __init__(self,
                 candidate_id,
                 ):
        self.id = candidate_id
        self.score = 0


if __name__ == "__main__":
    voting_schemes = [
        'Voting for one',
        'Voting for two',
        'Veto voting',
        'Borda voting',
        'Round voting',
    ]

    voting_strategies = [
        'Compromising',
        'Burying',
        'Push over',
        'Bullet voting',
    ]

    voting_for_one, voting_for_two, veto_voting, borda_voting, _ = voting_schemes
    compromising, burying, _, bullet_voting = voting_strategies

    preference_matrix = [
        [0, 1, 2],
        [1, 2, 0],
    ]

    agenda = [2, 1, 0]
    s = Situation(preference_matrix=preference_matrix)

    s.calculate_outcome(borda_voting, agenda)
    s.print_output()
    #
    # s.voting_scheme = bullet_voting
    # s.calculate_outcome(borda_voting)
    # s.print_output()
    #
    # s.apply_voting_strategy(compromising)
    # s.print_strategic_voting_options()
    #
    # s.apply_voting_strategy(burying)
    # s.print_strategic_voting_options()
    #


    # s.calculate_outcome(voting_for_one)
    # s.print_output()

    # The voter now compromises
    # original: voter 1 wants A > B
    # changed:  voter 1 wants B > A (Compromise)

    # we need to return
    # [v, O^~, H^~, z]
    # v = [B, A]
    # O^~ = B
    # H^~ = w/e
    # z = w/e

    # for each voter
    # for each voting strategy
    # if voting strategy changes outcome: record
    #
