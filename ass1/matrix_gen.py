import numpy as np
import random


def borda_voting(v, p):
    prefs = []
    for voter in range(v):
        v_pref = np.arange(p)
        random.shuffle(v_pref)
        prefs.append(v_pref)
    prefs = np.array(prefs)

    return prefs


def convert_to_plurality(prefs):
    high = prefs.max()

    plural_prefs = []
    for voter in prefs:
        vp = []
        for p in voter:
            if p == high:
                vp.append(1)
            else:
                vp.append(0)
        plural_prefs.append(vp)

    plural_prefs = np.array(plural_prefs)
    return plural_prefs


def convert_to_two(prefs):
    high = prefs.max()

    two_prefs = []
    for voter in prefs:
        vp = []
        for p in voter:
            if p == high:
                vp.append(1)
            elif p == (high - 1):
                vp.append(1)
            else:
                vp.append(0)
        two_prefs.append(vp)

    two_prefs = np.array(two_prefs)
    return two_prefs


def convert_to_veto(prefs):
    low = prefs.min()

    veto_pref = []
    for voter in prefs:
        vp = []
        for p in voter:
            if p == low:
                vp.append(0)
            else:
                vp.append(1)
        veto_pref.append(vp)

    veto_pref = np.array(veto_pref)
    return veto_pref


def matrix_writer(matrix, f):
    f.write('[')
    for i, voter in enumerate(matrix):
        f.write('[')
        for j, p in enumerate(voter):
            txt = str(p)
            if j != len(voter)-1:
                txt += ', '
            f.write(txt)
        brack = ']'
        if i != len(matrix)-1:
            brack += ','
        f.write(brack)
    f.write(']')


def main():
  n_voters = int(input("Voters: "))
  n_preferences = int(input("Preferences: "))

  preferences = borda_voting(n_voters, n_preferences)

  p1 = preferences
  p2 = convert_to_plurality(preferences)
  p3 = convert_to_two(preferences)
  p4 = convert_to_veto(preferences)

  f = open('matrices/voting_{}_{}.txt'.format(n_voters, n_preferences), 'a+')
  f.write("Borda\n")
  matrix_writer(p1, f)
  f.write('\n\n')

  f.write("Plurality\n")
  matrix_writer(p2, f)
  f.write('\n\n')

  f.write("For two\n")
  matrix_writer(p3, f)
  f.write('\n\n')

  f.write("Veto\n")
  matrix_writer(p4, f)
  f.write('\n\n')
  f.write("-"*50)


if __name__ == "__main__":
  main()
