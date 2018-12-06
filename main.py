# Blackjack testing parallel program. Well test 4 AIs playing different strageties over a large number of iterations and track which does best
import cards
import multiprocessing as mp
from threading import Thread
from queue import Queue
import time

q = Queue()

myDict = {
    "rock" : 0,
    "fish" : 0,
    "savvy" : 0


}

# adds card rank with Black Jack logic resolving Ace as 11 if possible
def add_cards(hand):
    x = 0
    a = 0
    for card in hand.cards:
        if card.rank == 1:
            a += 1
        if card.rank < 11:
            x += card.rank
        else:
            x += 10
    for q in range(a):
        if x + 10 <= 21:
            x += 10
    return x

# returns 1 if player wins, -1 if player loses, 0 if tie
def check_winner(dealer_hand, player_hand):
    if add_cards(player_hand) > 21:
        return -1
    elif add_cards(dealer_hand) > 21:
        return 1
    elif add_cards(dealer_hand) > add_cards(player_hand):
        return -1
    elif add_cards(dealer_hand) < add_cards(player_hand):
        return 1
    else:
        return 0

# rock hardly ever hits
def player_rock(num_hands, num_threads, remainder):
    for i in range((num_hands // num_threads) + remainder):
        fitness = 0
        for i in range(num_hands):
            #set deck
            deck = cards.Deck()
            deck.shuffle()
            #deal cards
            player_hand = cards.Hand()
            deck.move_cards(player_hand, 2)
            dealer_hand = cards.Hand()
            deck.move_cards(dealer_hand,2)
            #player logic
            while add_cards(player_hand) <= 13:
                deck.move_cards(player_hand, 1)
            #dealer logic
            while add_cards(dealer_hand) <= 17:
                deck.move_cards(dealer_hand, 1)
            #evaluate fitness
            fitness += check_winner(dealer_hand, player_hand)
        value = myDict.get("rock")
        myDict["rock"] = value + fitness 

# fish hits all the time
def player_fish(num_hands, num_threads, remainder):
    for i in range((num_hands // num_threads) + remainder):
        fitness = 0
        while num_hands > 0:
            #set deck
            deck = cards.Deck()
            deck.shuffle()
            #deal cards
            player_hand = cards.Hand()
            deck.move_cards(player_hand, 2)
            dealer_hand = cards.Hand()
            deck.move_cards(dealer_hand,2)
            #player logic
            while add_cards(player_hand) <= 16:
                deck.move_cards(player_hand, 1)
            #dealer logic
            while add_cards(dealer_hand) <= 17:
                deck.move_cards(dealer_hand, 1)
            #evaluate fitness
            fitness += check_winner(dealer_hand, player_hand)
            num_hands -= 1
        value = myDict.get("fish")
        myDict["fish"] = value + fitness 

#savvy player helper -- decideds to hit (return 1) or stand (return 0) based on current hand and 1 of dealers cards
def savvy_decide(player_hand, dealer_hand):
	a = 0
	for card in player_hand.cards:
		if (card.rank == 1):
			a += 1
	p = add_cards(player_hand)
	d = dealer_hand.cards[0].rank

	if (p > 21):
		return 0
	if (p <= 11 and a == 0):
		return 1
	if (p == 12 and a == 0):
		if (d >= 4 and d <= 6):
			return 0
		else:
			return 1
	if (p >= 13 and p <= 16 and a == 0):
		if (d >= 2 and d <= 6):
			return 0
		else:
			return 1
	if (p >= 17 and a == 0):
		return 0
	if (p <= 17 and a > 0):
		return 1
	if (p == 18 and a > 0):
		if (d >= 9 or d == 1):
			return 1
		else:
			return 0
	if (p >= 19 and a > 0):
		return 0
	print("**** Savvy Error ****")
	return -1

#savvy plays smart
def player_savvy(num_hands, num_threads, remainder):
    #num_hands = num_simulations
    for i in range((num_hands // num_threads) + remainder):
        fitness = 0
        while num_hands > 0:
	    #set deck
            deck = cards.Deck()
            deck.shuffle()
            #deal cards
            player_hand = cards.Hand()
            deck.move_cards(player_hand, 2)
            dealer_hand = cards.Hand()
            deck.move_cards(dealer_hand,2)
	    #player logic
            while (savvy_decide(player_hand, dealer_hand) > 0):
                deck.move_cards(player_hand, 1)
            fitness += check_winner(dealer_hand, player_hand)
            num_hands -= 1
        value = myDict.get("savvy")
        myDict["savvy"] = value + fitness 
    
"""
def player_genetic():
    #add genetic player
"""
def main():
    user_input = input(" How many hands do you want to play: ")
    num_hands = int(user_input)
    players = []
    num_threads = 10
    remainder = 0
    for i in range(num_threads):
        if i == num_threads - 1:
            remainder = num_hands % num_threads
        result = Thread(target=player_rock, args=[num_hands, num_threads, remainder])
        result.start()
        players.append(result)
            
        result = Thread(target=player_fish, args=[num_hands, num_threads, remainder])
        result.start()
        players.append(result)
            
        result = Thread(target=player_savvy, args=[num_hands, num_threads, remainder])
        result.start()
        players.append(result)
            
    for result in players:
        result.join()
        
    print(myDict)    

    
if __name__ == "__main__":
    start = time.time()
    main()
    overall_time = time.time()- start
    print("Elapsed time: {}".format(overall_time))
