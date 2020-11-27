from ass1.voting import *
from ass1.matrix_gen import *


voting_schemes = [
    'Borda voting',
    'Voting for one',
    'Voting for two',
    'Veto voting'
]


def test_situation(preferences, scheme):
    situation = Situation(preferences, scheme)
    situation.calculate_outcome()
    return situation.overall_happiness


if __name__ == "__main__":
    n_voters = int(input("Voters: "))
    n_preferences = int(input("Preferences: "))
    n_tests = int(input("Number of tests: "))

    results = [0, 0, 0, 0]
    for i in range(n_tests):
        preference = borda_voting(n_voters, n_preferences)
        pref_list = [
            preference,
            convert_to_plurality(preference),
            convert_to_two(preference),
            convert_to_veto(preference)
        ]

        for i in range(len(voting_schemes)):
            scheme = voting_schemes[i]
            prefs = pref_list[i]

            results[i] += test_situation(prefs, scheme)

    for k in range(len(results)):
        results[k] = results[k] / n_tests

    print(results)

