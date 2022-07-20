import time
import logging
from random import shuffle
from pynput import keyboard
#logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')

class Deck:
    def __init__(self):
        self.card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
        self.suits = ["♦", "♣", "♥", "♠"]
        self.card_deck = self.generate_full_cards()
        self.card_ranking = self.card_hierarchy()

    # Generate a 52 card deck, with order for each suit?
    def generate_full_cards(self):
        deck = []
        for _, suit in enumerate(self.suits):
            for number in self.card_values:
                card = str(number) + suit
                deck.append(card)
        return deck

    # Get deck hierarchy of values
    def card_hierarchy(self):
        ranking={}
        for i,value in enumerate(self.card_values):
            ranking.update({value:i})
        return ranking

class Player:
    def __init__(self, name, dealer):
        self.name = name
        self.dealer = dealer # True, or False
        self.cards = None # start with None, then allocate list of cards

class Game:
    def __init__(self, p1, p2):
        self.deck = Deck().card_deck
        logging.info(f"Created deck: {self.deck}")
        logging.info(f"Size of deck: {len(self.deck)}")
        self.ranking = Deck().card_ranking
        shuffle(self.deck)
        print("Shuffling deck...")
        time.sleep(2)
        logging.info(f"Shuffled deck: {self.deck}")
        self.p1 = p1
        self.p2 = p2

    def color_text(self, color=None, text=None):
        if color == "green":
            return print("\033[92m {}\033[00m" .format(text))
        elif color == "yellow":
            return print("\033[93m {}\033[00m" .format(text))
        elif color == "cyan":
            return print("\033[96m {}\033[00m" .format(text))
        elif color == "purple":
            return print("\033[95m {}\033[00m" .format(text))

    # Allocate cards to each player and keep track of order
    # This should update the self.cards state in the Player class
    def distribute_cards(self, deck=None):
        p1_cards, p2_cards = [], []
        while len(deck) > 0:
            p1_cards.append(deck.pop())
            p2_cards.append(deck.pop())
        logging.info(f"Player 1 cards: {p1_cards}")
        logging.info(f"Player 2 cards: {p2_cards}")
        assert len(p1_cards) + len(p2_cards) == 52
        return p1_cards, p2_cards

    # List of conditions to check if there is a slap or not
    def slap_rules(self, top_card=None, bottom_card=None, below_bottom_card=None):
        if top_card[-1:] == bottom_card[-1:]: # same suits
            self.color_text(color="green", text="Same suits...\n")
            return 1
        elif top_card[:-1] == "J": # slap jack
            self.color_text(color="green", text="Slap jack...\n")
            return 1
        elif top_card[:-1] == bottom_card[:-1]: # even value
            self.color_text(color="green", text="Even value...\n")
            return 1
        else: # Comparing more card values
            try:
                top_card_value = int(top_card[:-1])
            except:
                top_card_value = top_card[:-1]

            try:
                bottom_card_value = int(bottom_card[:-1])
            except:
                bottom_card_value = bottom_card[:-1]

            top_card_ranking = self.ranking[ top_card_value]
            bottom_card_ranking = self.ranking[ bottom_card_value]
            if (top_card_ranking - 1) == bottom_card_ranking: # plus one 
                self.color_text(color="green", text="Plus one rule...\n")
                return 1
            elif top_card_ranking == (bottom_card_ranking - 1): # minus one
                self.color_text(color="green", text="Minus one rule...\n")
                return 1
            else:
                return 0

        # Sandwich rule
        if below_bottom_card is not None:
            if top_card[:-1] == below_bottom_card[:-1]: # sandwich
                self.color_text(color="green", text="Sandwich...\n")
                return 1
            else:
                return 0

    def gameplay(self):

        def slap_board(key):
            nonlocal p1_cards, p2_cards, common_pile
            if key.char == "a":
                print("Player 1 slapped!")
                slap_result = self.slap_rules(top_card, bottom_card, below_bottom_card)
                # Apply slap rules for card distribution
                if slap_result == 1:
                    p1_cards = common_pile + p1_cards
                    common_pile = []
                    print("Resetting the common pile...")
                else:
                    print("Invalid slap...Player 1 losing cards.")
                    if len(p1_cards) >= 1:
                        first_card = p1_cards.pop()
                        common_pile.append(first_card)
                        #common_pile = list(first_card) + common_pile
                    if len(p1_cards) >= 1:
                        second_card = p1_cards.pop()
                        common_pile.append(second_card)
                        #common_pile = list(second_card) + common_pile
            elif key.char == "l":
                print("Player 2 slapped!")
                slap_result = self.slap_rules(top_card, bottom_card, below_bottom_card)
                # Apply slap rules for card distribution
                if slap_result == 1:
                    p2_cards = common_pile + p2_cards
                    common_pile = []
                    print("Resetting the common pile...")
                else:
                    print("Invalid slap...Player 2 losing cards.")
                    if len(p2_cards) >= 1:
                        first_card = p2_cards.pop()
                        common_pile.append(first_card)
                        #common_pile = list(first_card) + common_pile
                    if len(p2_cards) >= 1:
                        second_card = p2_cards.pop()
                        common_pile.append(second_card)
                        #common_pile = list(second_card) + common_pile
            else:
                print(self.color_text(color="yellow", text="Not a slap key!"))

        def print_released_key(key):
            print(f"Released {key}!")

        # Allocate cards to players
        print("Allocating cards to players by the dealer...")
        time.sleep(2)
        p1_cards, p2_cards = self.distribute_cards(self.deck)

        listener = keyboard.Listener(lambda event: slap_board(event),on_release = print_released_key)
        gameclock = True
        common_pile = []

        # Initiate keyboard listener
        listener.start()

        # Start gameplay
        while gameclock == True:
            # Break game if a player has lost all cards
            if len(p1_cards) == 0:
                print(f"Player 2 wins...with {len(p2_cards)} cards vs. Player 1 with {len(p1_cards)} cards!")
                gameclock = False
                break
            elif len(p2_cards) == 0:
                print(f"Player 1 wins...with {len(p1_cards)} cards vs. Player 2 with {len(p2_cards)} cards!")
                gameclock = True
                break

            # Gameplay
            # Non-dealer goes first
            non_dealer_card = p2_cards.pop()
            time.sleep(0.1)
            self.color_text(color="purple", text=f"Player 2 plays: {non_dealer_card}")
            common_pile.append(non_dealer_card)

            # Dealer plays next
            dealer_card = p1_cards.pop()
            time.sleep(0.1)
            self.color_text(color="purple", text=f"Player 1 plays: {dealer_card}")
            common_pile.append(dealer_card)

            # Count cards among players and common pile
            self.color_text(color="purple", text=f"Player 1 card count: {len(p1_cards)}")
            self.color_text(color="purple", text=f"Player 2 card count: {len(p2_cards)}")
            self.color_text(color="purple", text=f"Common pile count: {len(common_pile)}")
            #self.color_text(color="purple", text=f"TOTAL: {len(common_pile) + len(p2_cards) + len(p1_cards)}")
            assert len(common_pile) + len(p1_cards) + len(p2_cards) == 52

            # Pulse if a slap event
            top_card = common_pile[-1:][0]
            bottom_card = common_pile[-2:-1][0]
            if len(common_pile) == 2:
                below_bottom_card=None
            else:
                below_bottom_card=common_pile[-3:-2][0]
            self.color_text(color="purple", text=f"Top card: {top_card}, Bottom card: {bottom_card}, Below bottom: {below_bottom_card}\n")
            # Time for players to slap
            time.sleep(5)

        # Initiate listener stop
        listener.stop()


if __name__ == "__main__":
    # Create players
    p1 = Player("dealer", dealer=True)
    p2 = Player("non-dealer", dealer=False)

    # Initiate the gameplay and start with a shuffled deck
    g = Game(p1, p2)
    g.gameplay()

