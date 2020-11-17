import numpy as np
import random
import time
from copy import copy

voting_schemes = [
    'Voting for one',
    'Voting for two',
    'Veto voting',
    'Borda voting',
    'Round voting',
]

voting_strategies = [
    '',
    'Compromising',
    'Burying',
    'Push over',
    'Bullet voting',
]

voting_for_one, voting_for_two, veto_voting, borda_voting, round_voting = voting_schemes
_, compromising, burying, _, bullet_voting = voting_strategies

class Situation:
    def __init__(self, preference_matrix, voting_scheme):
        self.voter_num = len(preference_matrix)
        self.candidate_num = len(preference_matrix[0])
        self.preference_matrix = preference_matrix

        self.candidates = None
        self.agenda = None
        self.round_winner = None
        self.voting_strategy = ''
        self.voters = None
        self.voting_scheme = voting_scheme
        self.candidates_outcome = None
        self.strategic_voting_options = None


        # if we have 2 rounds then overall_happiness = [1, 2]

        self.overall_happiness = []

        self.reset_situation()

    def calculate_outcome(self, agenda=None):
        if self.voting_scheme == 'Round voting':
            self.round_winner = self.candidates[0]
            for i in range(1, len(agenda)):
                participants = [self.round_winner, self.candidates[i]]
                for voter in self.voters:
                    voter.vote_round(self.voting_scheme, participants)
                if self.round_winner.score < self.candidates[i].score:
                    self.round_winner.score = 0
                    self.round_winner = self.candidates[i]
                self.round_winner.score = 0
                self.candidates[i].score = 0
        else:
            for voter in self.voters:
                voter.vote(self.voting_strategy == 'Bullet voting')
            self.candidates_outcome = sorted(self.candidates, key=lambda c: c.score, reverse=True)

        for voter in self.voters:
            voter.calculate_happiness(self.candidates_outcome)

        self.calculate_overall_happiness()

    def set_voting_strategy(self, voting_strategy):
        self.voting_strategy = voting_strategy

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
                for l in range(k - 1, -1, -1):
                    preference_vector = voter.get_preference_vector()
                    preference_vector.insert(k, preference_vector.pop(l))

                    voter.set_vote_order(preference_vector, self.candidates)

                    self.calculate_outcome(self.voting_scheme)
                    self.reset_candidate_scores()

                    self.strategic_voting_options.append(self.create_stategic_option(voter))

                voter.set_vote_order(voter.get_preference_vector(), self.candidates)

    def apply_burying(self):
        for i in range(self.voter_num):
            voter = self.voters[i]
            for k in range(0, self.candidate_num):
                for l in range(k + 1, self.candidate_num):
                    preference_vector = voter.get_preference_vector()
                    preference_vector.insert(k, preference_vector.pop(k - l))

                    voter.set_vote_order(preference_vector, self.candidates)

                    self.calculate_outcome(self.voting_scheme)
                    self.reset_candidate_scores()

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

    def reset_candidate_scores(self):
        for c in self.candidates:
            c.score = 0

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
            voting_scheme=self.voting_scheme,
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

    def generate_output(self):
        result_string = ""
        for voter in self.voters:
            result_string += voter.generate_output()
            result_string += "\n"
        result_string += "Candidate {} won with a score of {}\n".format(self.candidates_outcome[0].id,
                                                           self.candidates_outcome[0].score)
        result_string += "Overall voter happiness is {}\n".format(self.overall_happiness)
        return result_string

    def generate_strategic_voting_output(self):

        if self.voting_strategy == bullet_voting:
            return self.generate_output()

        result_string = "\n\n\nApplying strategy: {}\n".format(self.voting_strategy)
        for option in self.strategic_voting_options:
            v_id, v, O, H, z = option
            result_string += "v_id: {}, v: {}, O^~: {}, H^~: {}, z: {}\n".format(v_id, v, O, H, z)

        result_string += "Overall risk of strategic voting: {}\n".format(len(self.strategic_voting_options)/self.voter_num)

        return result_string



class Voter:
    def __init__(self,
                 voter_id,
                 candidates,
                 voting_scheme,
                 ):
        self.id = voter_id
        self.preferences = candidates
        self.vote_order = candidates
        self.preference_vector = None
        self.voting_scheme = voting_scheme
        self.happiness = 0.0

    def set_preference(self, preference_vector):
        new_preferences = []
        self.preference_vector = preference_vector

        if self.voting_scheme == borda_voting:
            for idx in preference_vector:
                candidate = self.preferences[idx]
                new_preferences.append(candidate)

        if self.voting_scheme == voting_for_one:
            indices = [i for i, x in enumerate(preference_vector) if x == 1]
            new_preferences.append(self.preferences[indices[0]])
            for candidate in self.preferences:
                if candidate == new_preferences[0]:
                    continue
                new_preferences.append(candidate)

        if self.voting_scheme == voting_for_two:
            indices = [i for i, x in enumerate(preference_vector) if x == 1]
            new_preferences.append(self.preferences[indices[0]])
            new_preferences.append(self.preferences[indices[1]])

            for candidate in self.preferences:
                if candidate == new_preferences[0] or candidate == new_preferences[1]:
                    continue
                new_preferences.append(candidate)

        if self.voting_scheme == veto_voting:
            indices = [i for i, x in enumerate(preference_vector) if x == 0]
            last_candidate = self.preferences[indices[0]]

            for candidate in self.preferences:
                if candidate == last_candidate:
                    continue
                new_preferences.append(candidate)
            new_preferences.append(last_candidate)

        self.preferences = new_preferences
        self.vote_order = copy(self.preferences)

    def get_preference_vector(self):
        return copy(self.preference_vector)

    def calculate_happiness(self, candidates_outcome):
        total_distance = 0
        reversed_outcome = list(reversed(candidates_outcome))
        k = 1
        for candidate in list(reversed(self.preferences)):
            j = reversed_outcome.index(candidate) + 1
            total_distance += (k - j) * j
            k += 1
        self.happiness = 1 / (1 + abs(total_distance))

    def set_vote_order(self, preference_vector, candidates):
        new_vote_order = []

        if self.voting_scheme == borda_voting:
            for idx in preference_vector:
                candidate = candidates[idx]
                new_vote_order.append(candidate)

        if self.voting_scheme == voting_for_one:
            indices = [i for i, x in enumerate(preference_vector) if x == 1]
            new_vote_order.append(candidates[indices[0]])
            for candidate in candidates:
                if candidate == new_vote_order[0]:
                    continue
                new_vote_order.append(candidate)

        if self.voting_scheme == voting_for_two:
            indices = [i for i, x in enumerate(preference_vector) if x == 1]
            new_vote_order.append(candidates[indices[0]])
            new_vote_order.append(candidates[indices[1]])

            for candidate in candidates:
                if candidate == new_vote_order[0] or candidate == new_vote_order[1]:
                    continue
                new_vote_order.append(candidate)

        if self.voting_scheme == veto_voting:
            indices = [i for i, x in enumerate(preference_vector) if x == 0]
            last_candidate = candidates[indices[0]]

            for candidate in candidates:
                if candidate == last_candidate:
                    continue
                new_vote_order.append(candidate)
            new_vote_order.append(last_candidate)

        self.vote_order = new_vote_order

    def vote(self, bullet_voting=False):
        if self.voting_scheme == voting_for_one:
            self.vote_order[0].score += 1
        if self.voting_scheme == voting_for_two:
            self.vote_order[0].score += 1
            if bullet_voting:
                return
            self.vote_order[1].score += 1
        if self.voting_scheme == veto_voting:
            for i in range(len(self.vote_order) - 1):
                self.vote_order[i].score += 1
                if bullet_voting:
                    return
        if self.voting_scheme == borda_voting:
            candidate_num = len(self.vote_order)
            for i in range(len(self.vote_order)):
                self.vote_order[i].score += candidate_num - 1 - i
                if bullet_voting:
                    return

    def vote_round(self, round_participants):
        if self.voting_scheme == "Voting for one":
            for candidate in self.vote_order:
                if candidate in round_participants:
                    candidate.score += 1
                    return

    def set_voting_scheme(self, voting_scheme):
        self.voting_scheme = voting_scheme

    def generate_output(self):
        return "Voter: {}\nTrue preference: {}\nAdjusted preference: {}\nHappiness: {}\n".format(
            self.id, [c.id for c in self.preferences], [c.id for c in self.vote_order], self.happiness
        )


class Candidate:
    def __init__(self,
                 candidate_id,
                 ):
        self.id = candidate_id
        self.score = 0


if __name__ == "__main__":
    preference_matrix = [
        [0, 1, 1],
        # [1, 2, 0],
    ]

    s = Situation(preference_matrix=preference_matrix, voting_scheme=voting_for_two)
    s.calculate_outcome()
    print(s.generate_output())
    s.apply_voting_strategy(compromising)
    print(s.generate_strategic_voting_output())
    #
    # s.voting_scheme = bullet_voting
    # s.calculate_outcome(round_voting)
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
