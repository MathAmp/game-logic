"""A script to play mighty in the console, using the game.py module."""

import random
import game

__author__ = "Jake Hyun (SyphonArch)"
__copyright__ = "Copyright 2019, The Mighty-Online Team"
__credits__ = ["Jake Hyun (SyphonArch)"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Jake Hyun (SyphonArch)"
__email__ = "jake.hyun@hotmail.com"
__status__ = "Development"

space = 100


def random_random_player(perspective):
    """A very random AI player of Mighty."""
    hand, tricks, suit_led, setup = perspective
    declarer, trump, bid, friend_card, friend = setup

    trick_number = len(tricks) - 1
    trick = tricks[-1]

    valid_moves = [c for c in hand if game.is_valid_move(trick_number, trick, suit_led, trump, hand, c)]

    return random.choice(valid_moves)


def random_random_bidder(hand, prev_trump, prev_bid, minimum_bid):
    """A very random AI bidder of Mighty"""
    # Note that you can call one less with a no-trump
    suit_counts = {}
    for suit in game.suits:
        count = 0
        for card in hand:
            if card[0] == suit:
                count += 1
        suit_counts[suit] = count

    maximum_suit_num = max(suit_counts.values())
    trump = game.uninit['suit']
    for suit in suit_counts:
        if suit_counts[suit] == maximum_suit_num:
            trump = suit

    if random.random() > 0.5:
        for bid in range(1, 21):
            if game.is_valid_bid(trump, bid, prev_trump, prev_bid, minimum_bid):
                return trump, bid

    return game.uninit['suit'], 0


def imma_call_miss_deal(hand):
    """Will always call miss-deal. That is, this function simply returns True."""
    return True


def random_random_exchanger(hand, trump):
    """Returns three cards to discard and the trump to change to, on a very random basis."""
    random.shuffle(hand)
    return hand[:3], trump


def mighty_joker_trump_friend_caller(hand, trump):
    mighty = game.trump_to_mighty(trump)
    if mighty not in hand:
        return mighty
    elif game.joker not in hand:
        return game.joker
    else:
        rank_priority_order = ['A', 'K', 'Q', 'J', 'X', '9', '8', '7', '6']
        for rank in rank_priority_order:
            card = trump + rank
            if card not in hand:
                return card
        print("Nope. This can't have happened.")
        exit(1)


def introduce_hands(hands, players):
    for player in players:
        input("Press Enter to reveal Player {}'s hand.".format(player))
        print(' '.join(hands[player]))
        input("Press Enter to clear screen.")
        print('\n' * space)


################### SETUP ####################


ai_bidder = random_random_bidder
ai_miss_deal_caller = imma_call_miss_deal
ai_exchanger = random_random_exchanger
ai_friend_caller = mighty_joker_trump_friend_caller
ai_player = random_random_player

##############################################

while True:
    ai_num = input("How many AI agents?: ")
    print()
    if ai_num.isdigit() and int(ai_num) in range(6):
        ai_num = int(ai_num)
        break
    print("Invalid input.")

ai_players_seed = [True] * ai_num + [False] * (5 - ai_num)
random.shuffle(ai_players_seed)

ai_players = []
for i in range(len(ai_players_seed)):
    if ai_players_seed[i]:
        ai_players.append(i)

human_players = [p for p in range(5) if p not in ai_players]

ai_nums_str = ', '.join([str(x) for x in ai_players])
print('Player numbers {} are AI agents.'.format(ai_nums_str))
print()

# Initiating the game object.
mighty_game = game.GameEngine()
feedback = -1
final_trump = game.uninit['suit']

introduce_hands(mighty_game.hands, human_players)

# Here starts the game loop.
while True:
    call_type = mighty_game.next_call
    if call_type == game.GameEngine.calltype['bid']:
        print("Player {}'s turn to make a bid.".format(mighty_game.next_bidder))

        if mighty_game.highest_bid == game.uninit['bid']:
            lower_bound = mighty_game.minimum_bid
        else:
            lower_bound = mighty_game.highest_bid + 1

        print("Bid must be greater or equal to {}.".format(lower_bound))

        if mighty_game.next_bidder in ai_players:

            trump, bid = ai_bidder(mighty_game.hands[mighty_game.next_bidder], mighty_game.trump_candidate,
                                   mighty_game.highest_bid, mighty_game.minimum_bid)
        else:
            print("To pass, enter 0 for the bid.")
            while True:
                while True:
                    trump = input("Enter trump: ")
                    bid = input("Enter bid: ")
                    if (trump in game.suits + ['N'] and bid.isdigit()) or bid == '0':
                        bid = int(bid)
                        break
                    print('Invalid bid.')
                if game.is_valid_bid(trump, bid, mighty_game.trump_candidate, mighty_game.highest_bid,
                                     mighty_game.minimum_bid) or bid == 0:
                    break
                print("Invalid bid.")

        if bid != 0:
            print("Player {} bids {} {}.".format(mighty_game.next_bidder, game.suits_short_to_long[trump], bid))
        else:
            print("Player {} passes.".format(mighty_game.next_bidder))

        feedback = mighty_game.bidding(mighty_game.next_bidder, trump, bid)

    elif call_type == game.GameEngine.calltype['exchange']:
        print('Declarer: {}'.format(mighty_game.declarer))
        print("Final bid: {} {}".format(game.suits_short_to_long[mighty_game.trump], mighty_game.bid))
        print("Card exchange in process.")
        if mighty_game.declarer in ai_players:
            to_discard, final_trump = ai_exchanger(mighty_game.hands[mighty_game.declarer] + mighty_game.kitty,
                                                   mighty_game.trump)
        else:
            input('Player {} - Press Enter to reveal the kitty'.format(mighty_game.declarer))
            print(' '.join(mighty_game.kitty))
            while True:
                to_discard = input("Enter the three cards to discard, space seperated: ")
                to_discard = to_discard.split()
                if all([x for x in to_discard if x in mighty_game.hands[mighty_game.declarer] + mighty_game.kitty]):
                    break
                print("Invalid input.")

            print('\n' * space)

        print('Exchange over.')
        feedback = mighty_game.exchange(to_discard)

    elif call_type == game.GameEngine.calltype['miss-deal check']:
        input('HALT')

    elif call_type == game.GameEngine.calltype['trump change']:
        input("HALT")

    elif call_type == game.GameEngine.calltype['friend call']:
        input("HALT")

    elif call_type == game.GameEngine.calltype['redeal']:
        print("REDEAL IN PROCESS.")
        mighty_game = game.GameEngine()
        introduce_hands(mighty_game.hands, human_players)

    elif call_type == game.GameEngine.calltype['play']:
        input("HALT")

    elif call_type == game.GameEngine.calltype['game over']:
        input("HALT")

    else:
        print("CRITICAL: There is no method of handling specified for call type '{}'".format(call_type))
        exit(1)

    if feedback:
        print('Calltype: {}, Error #{}'.format(mighty_game.next_call, feedback))
        exit(1)
    print('-------------------------------')
