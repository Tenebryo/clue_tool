from z3 import *

import sys

filename = sys.argv[1]

solver = Solver()

with open(filename, 'r') as fd:
    variables = []
    card_names = []
    cards = {}
    # Read in all suspects
    for s in fd.readline().split():
        cards[s] = len(card_names)
        card_names += [s]
        
    suspects_max = len(card_names)
    
    # Read in all weapons
    for s in fd.readline().split():
        cards[s] = len(card_names)
        card_names += [s]

    weapons_max = len(card_names)
    
    # Read in all rooms
    for s in fd.readline().split():
        cards[s] = len(card_names)
        card_names += [s]

    num_cards = len(card_names)

    # read in players and how many cards each has
    num_players = int(fd.readline().strip())
    players = {}
    player_cards = []
    player_names = []
    for i in range(num_players):
        s, cnum = fd.readline().split()
        s = s.strip()
        cnum = int(cnum.strip())
        player_names += [s]
        players[s] = i
        card_vars = [Int("{}_card_{}".format(s, j)) for j in range(cnum)]
        player_cards += [card_vars]
        variables += card_vars

        # reduce number of solutions by ordering each player's cards, might not affect number of results
        for c0, c1 in zip(card_vars[:-1], card_vars[1:]):
            print("{} < {}".format(c0, c1))
            solver.add(c0 < c1)

    # read in the cards from the first player
    for (c, v) in zip(sorted([cards[c] for c in fd.readline().split()]), player_cards[0]):
        solver.add(v == c)
    
    true_suspect = Int("True_Suspect")
    true_weapon = Int("True_Weapon")
    true_room = Int("True_Room")

    variables += [true_suspect, true_weapon, true_room]

    # ensure that the solution cards contain one of each kind
    solver.add(And(0 <= true_suspect, true_suspect < suspects_max))
    solver.add(And(suspects_max <= true_weapon, true_weapon < weapons_max))
    solver.add(And(weapons_max <= true_room, true_room < num_cards))


    # check that the number of cards is correct
    assert(sum(map(len, player_cards)) + 3 == num_cards)

    # add constraints to enforce 
    for var in variables:
        solver.add(0 <= var)
        solver.add(var < num_cards)

    # no card can repeat
    solver.add(Distinct(variables))

    def get_all_solutions():
            
        solutions = []

        solver.push()

        while solver.check() == sat:
            m = solver.model()

            solutions.append(m)

            # restrict the solution space further
            solver.add(Or([d() != m[d] for d in m]))

            # we are particularly interested in solutions where the three hidden cards are different
            solver.add(Or([d != m[d] for d in [true_suspect, true_weapon, true_room]]))
        
        solver.pop()

        return solutions

    # add constraints that each guess imposses on the state space
    for i, line in enumerate(fd.readlines()):

        print("Possible Solutions Before Guess {}: {}".format(i + 1, len(get_all_solutions())))

        gtype, guesser, suspect, weapon, room, responder, card = line.split()
        guesser = players[guesser]
        suspect = cards[suspect]
        weapon = cards[weapon]
        room = cards[room]
        if responder in players:
            responder = players[responder]
        else:
            responder = None

        if card in cards:
            card = cards[card]
        else:
            card = None

        if gtype == 'guess':
            # add constraints for cards players don't have
            i = (guesser + 1) % num_players
            while i != responder and i != guesser:
                # if they were passed over, none of their cards can be those from the guess
                for c in player_cards[i]:
                    solver.add(And(c != suspect, c != weapon, c != room))
                i = (i + 1) % num_players
            
            if responder:
                if card:
                    # the card that was passed is known
                    solver.add(Or([c == card for c in player_cards[responder]]))
                else:
                    # one of the responder's cards is one of the guess cards (cross inequality)
                    solver.add(Or([g == c for g in [suspect, weapon, room] for c in player_cards[responder]]))
        elif gtype == 'accusation':
            # assume the accusation was false, since the game is still being considered
            solver.add(Or(true_suspect != suspect, true_weapon != weapon, true_room != room))

    print()
    print("+===================+")
    print("| Getting Solutions |")
    print("+===================+")
    print()

    solutions = get_all_solutions()

    print("Found {} Possible Solution(s)".format(len(solutions)))
    print()
    for i, m in enumerate(solutions):

        #print out the possible solution
        print("Possible Solution {}".format(i+1))
        for i in range(num_players):
            print("  {}: {}".format(player_names[i], str([card_names[m[c].as_long()] for c in player_cards[i]])))
        print("  Hidden Cards: {} {} {}".format(
            card_names[m[true_suspect].as_long()],
            card_names[m[true_weapon].as_long()],
            card_names[m[true_room].as_long()])
        )
        print()
