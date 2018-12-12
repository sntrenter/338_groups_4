# Blackjack testing parallel program. Well test 4 AIs playing different strageties over a large number of iterations and track which does best
import cards
import neatnn as nn
import multiprocessing as mp
import time

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

# adds card rank with Black Jack logic, always resolving Ace as 1
def low_add_cards(hand):
    x = 0
    for card in hand.cards:
        if card.rank < 11:
            x += card.rank
        else:
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
def player_rock(num_hands, totals):
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
    totals.put(("rock", fitness))

# fish hits all the time
def player_fish(num_hands, totals):
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
    totals.put(("fish", fitness))

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
def player_savvy(num_hands, totals):
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
	totals.put(("savvy", fitness))



def player_genetic(entities, num_hands, totals, training=True):
    for entity in entities:
        if not training: fitness = 0
        entity.rawFitness = 0
        deck = cards.Deck()
        for i in range(num_hands):
            #set deck
            deck.shuffle()
            #deal cards
            player_hand = cards.Hand()
            deck.move_cards(player_hand, 2)
            dealer_hand = cards.Hand()
            deck.move_cards(dealer_hand,2)
            #player logic
            nn = entity.getNN() #Get the player's Neural Network
            while add_cards(player_hand) < 21 and nn.update([add_cards(player_hand)/31,low_add_cards(player_hand)/31, min(dealer_hand.cards[0].rank/10,1),1])[0] >= 0.5:
                deck.move_cards(player_hand, 1)
            #dealer logic
            while add_cards(dealer_hand) <= 17:
                deck.move_cards(dealer_hand, 1)
            #evaluate fitness
            if not training: fitness += check_winner(dealer_hand, player_hand)
            entity.rawFitness += check_winner(dealer_hand, player_hand)
            #return all cards to the deck
            player_hand.move_cards(deck, len(player_hand.cards))
            dealer_hand.move_cards(deck, len(dealer_hand.cards))
        if training:
            totals.put(entity)
        else:
            totals.put(("genetic", fitness))
    totals.close()
    totals.join_thread()

def main():
        
    totals = mp.Queue() #holds total fitness of tests in key-number pairs
    user_input = input(" How many hands do you want to play: ")
    num_hands = int(user_input) #hard-coded -- consider switching to user imput
    players = []
    
    num_training_hands = 800 # The number of games to play in each training generation
    num_genetic = 200 # The number of genetic neural networks to include in each generation
    num_generations = 50 # The number of generations to train the neural networks
    num_workers = 10
    entities_per_worker = num_genetic / num_workers
    genetic_population = nn.Population(num_genetic, 4, 1, 0.4,c3=0.8)

    #Train the neural network beforehand
    print("Training our genetic player...")
    for i in range(num_generations):
        trainees = []
        local_entities = []
        for x in range(num_workers):
            p = mp.Process(target = player_genetic, args = [genetic_population.entities[int(x*entities_per_worker):int((x+1)*entities_per_worker)], num_training_hands, totals])
            trainees.append(p)
            p.start()
        for p in trainees:
            while p.is_alive():
                while not totals.empty():
                    local_entities.append(totals.get())
            p.join()
        genetic_population.entities = local_entities.copy()
        genetic_population.fixEntities()
        genetic_population.speciateEntities()
        genetic_population.setSharedFitnesses()
        genetic_population.sortEntities()
        print("\t",str(((i+1)/num_generations)*100)+"% complete. Highest fitness:",max(genetic_population.entities,key=lambda x:x.rawFitness).rawFitness,"Lowest fitness:",min(genetic_population.entities,key=lambda x:x.rawFitness).rawFitness)
        if(i<num_generations-1):
            genetic_population.createNextGeneration(0.03,0.05,0.8)
    print("Training complete. Running test.")
    start = time.time()
    best_genetic = max(genetic_population.entities, key = lambda x: x.rawFitness)
    
    p = mp.Process(target = player_rock, args = [num_hands, totals])
    players.append(p)
    
    p = mp.Process(target = player_fish, args = [num_hands, totals])
    players.append(p)

    p = mp.Process(target = player_savvy, args = [num_hands, totals])
    players.append(p)

    p = mp.Process(target = player_genetic, args = [[best_genetic], num_hands, totals, False])
    players.append(p)

    for p in players:
        p.start()
    for p in players:
        p.join()

    results = []
    while not totals.empty() > 0:
        results.append(totals.get())
    results.sort(key = lambda x: x[1], reverse = True)
    for r in results:
        print(r)
    overall_time = time.time() - start
    print("Elapsed time: {}".format(overall_time))
    
if __name__ == "__main__":  
    main()
