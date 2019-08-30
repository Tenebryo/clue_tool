Clue Solver
===

I had the idea for this project while playing Clue with my family. I have a rigorous notekeeping strategy for playing clue, but it took too long to look back through the notes to reconcile new information with the old. Thus, I thought I could automate the deductions I typically apply using Z3 (as well as some that would be humanly impractical/impossible).

# Usage

The game information is parsed from the file given as the first command line argument. The file format is as follows (its made to be general to expanded versions of Clue):
```
<line with each suspect, space separated>
<line with each weapon, space separated>
<line with each room, space separated>
<number of players>
<player> <number of cards>
... (one line for each player)
(guess | accusation) <player making guess/accusation> <suspect> <weapon> <room> <player who responded (none, if no one did)> <revealed card (unknown if not your guess)>
... (one line for each guess)
```

There is an example file in [data.txt](data.txt). Note that the order of the players in the file must match the turn order because the order is used to rule out cards for players who didn't respond to a guess.

Once the data file is prepared, just run `python solver.py data.txt` to see how each guess reduces the number of possible scenarios.

# Theory of Operation

This tool is made using Z3, an SMT solver. The variables in this case are one for each card each player's hand (representing which card it is), and one for each hidden card. Which card is represented in each variable is determined by the integer value of the card. The card variables are restricted to be in the range of all cards (0..num_cards) for those in the players' hands and the hidden cards are restricted to be one of each type (suspect, weapon, and room). Furthermore, each of the card variables must be distinct so that each card is only in one location.

Then, for each guess, we have a number of constraints we can add. First, for each player that passes on revealing a conflict between the guess and their cards, we know that none of their cards can be any of the cards in the guess. Second, if someone reveals a card to you, you know that one of their cards is that card. Third, if someone reveals a card to someone else, all you know is that one of their cards is one of the cards from the guess.

Failed accusations are simpler. If an accusation fails, then you know that the suspect, weapon, or room that was guessed was wrong.

In order to find all solutions, we query the solver for a solution, add it to a list, then add a new constraint that prevents that solution from being valid (the disjunction of the inequality of each of the variables with their values from that particular solution). Furthermore, in order to reduce the total number of possible solutions and because we are mostly interested in the hidden cards, we add another similar constraint to enforce that in each new solution, the triple of hidden cards is unique.

# Results and Applications

I have not used this in a game of Clue yet, but I retroactively applied it to the notes I took from the last game I played. It turns out that I figured out what the 3 hidden cards were as early as this solver did. In other words, it failed in the sense that it could calculate the solution any earlier that I would have. This might not be the case for all games of Clue, but it seems unlikely that it will dominate a human player (who may be able to infer extra information from table talk, intuition, etc.). 

# Other Thoughts

The tool is likely more valueable as an aide to optimize your guesses (as opposed to merely sifting through the deductions) for reducing the number of possible triples of hidden cards, although the current interface would be cumbersome for this use. Implementation of a procedure to simulate the results of different guesses in each of the possible card assignments would likely be necessary to effectively use the tool in that capacity. 

However, even then there are still some strategy considerations that might need to be made, such as "how much information will this guess give to my opponent." If you want the tool to make considerations such as this, the problem becomes a very expensive tree search problem, and an automatic system would likely have to be some sort of hueristic or learned procedure. Such a hybrid SMT+MCTS+ML model might be interesting to apply to other imperfect information, hightly deduction-based games other than Clue.