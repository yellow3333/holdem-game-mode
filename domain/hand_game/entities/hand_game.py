import random

from domain.hand_game.entities.player import *
from domain.hand_game.entities.round import *
from domain.hand_game.entities.hand_cleanup import *

#   This class is for single hand_game entity
class Hand_game():
    # players: {$id: $player_obj, ...}
    def __init__(self, players, sb, bb):
        self.players = players.copy()
        self.remaining_players = players.copy()
        self.remaining_players_ids = list(players.keys())
        self.sb = sb
        self.bb = bb
        self.pot = 0
        self.flop = None
        self.turn = None
        self.river = None
        self.cur_position = 0       # the current player to action, starting from sb
        self.still_raise = True     # a raise is not checked
        self.top_bet = bb           # the current highest bet
        self.cur_round = Round(self.remaining_players)
        self.cur_round_cnt = 0      # 0-preflop / 1-flop / 2-turn / 3-river
        self.game_over = False
        self.__deal_cards()
        # self.__sb_bb()

    
    def __create_deck(self):
        deck = []
        suites = ["club", "diamond", "heart", "spade"]
        for i in range(1, 14):
            for s in suites:
                deck.append({"suite": s, "face": i})
        return deck

    def __shuffle(self, arr):
        for i in range(len(arr)-1, 0, -1):
            j = random.randint(0, i)
            tmp = arr[i]
            arr[i] = arr[j]
            arr[j] = tmp
        return arr


    # deal cards to all players
    def __deal_cards(self):
        random_deck = self.__shuffle(self.__create_deck())
        for i in range(len(self.players)):
            player_id = self.remaining_players_ids[i]
            self.players[player_id].deal([random_deck[2 * i], random_deck[2 * i + 1]])
        next_index = len(self.players) * 2
        self.flop = [random_deck[next_index], random_deck[next_index + 1], random_deck[next_index + 2]]
        self.turn = [random_deck[next_index + 3]]
        self.river = [random_deck[next_index + 4]]
    
    # handles sb and bb
    def __sb_bb(self):
        # 0th bets sb
        cur_id = self.cur_round.get_current_player_id()
        self.players[cur_id].remaining_chips -= self.sb
        self.pot += self.sb
        self.cur_round.raise_bet(self.sb)
        self.cur_round.advance_player()
        # 1st bets bb
        cur_id = self.cur_round.get_current_player_id()
        self.players[cur_id].remaining_chips -= self.bb
        self.pot += self.bb
        self.cur_round.raise_bet(self.bb)
        self.cur_round.advance_player()

    # get single player by id
    def get_player(self, player_id):
        return self.players[player_id]


    # get the current player that takes action
    def get_current_player(self):
        return self.cur_round.get_current_player()

    # palyer_id takes action
    def take_action(self, player_id, action):
        return_action = None
        if player_id != self.cur_round.get_current_player().id:
            return return_action
        # fold
        if action['action'] == 'fold':
            self.__fold()
            return_action = action
        
        # call
        elif action['action'] == 'call':
            # not calling correct amount
            if action['amount'] != self.cur_round.to_call(player_id):
                self.__fold()
                return_action = {'action': 'fold', 'amount': 0}
            # don't own enough chips
            elif self.players[player_id].remaining_chips < action['amount']:
                self.__fold()
                return_action = {'action': 'fold', 'amount': 0}
            else:
                self.__call(player_id, action['amount'])
                return_action = action

        # check
        elif action['action'] == 'check':
            # someone raised before
            if self.cur_round.still_raise:
                self.__fold()
                return_action = {'action': 'fold', 'amount': 0}
            else:
                self.__check()
                return_action = action

        # raise
        elif action['action'] == 'raise':
            # amount smaller than current top bet
            if (action['amount'] < self.cur_round.top_bet) or (action['amount'] > self.players[player_id].remaining_chips):
                self.__fold()
                return_action = {'action': 'fold', 'amount': 0}
            else:
                self.__raise(player_id, action['amount'])
                return_action = action
            
        # allin###
        elif action['action'] == 'allin':
            if (action['amount'] <= self.cur_round.top_bet):
                self.__fold()
                return_action = {'action': 'fold', 'amount': 0}
            else:
                action['amount']=self.players[player_id].remaining_chips
                self.__raise(player_id, action['amount'])
                return_action = {'action': 'allin', 'amount': action['amount']}
        else:
            self.__fold()
            return_action = {'action': 'fold', 'amount': 0}
        
        self.__update_round()
        return return_action

    def __fold(self):
        # remove from remaining players
        self.cur_round.remove_current_player()
        

    def __call(self, player_id, amount):
        self.players[player_id].remaining_chips -= amount
        self.pot += amount
        self.cur_round.advance_player()
    
    def __check(self):
        self.cur_round.advance_player()
    
    def __raise(self, player_id, amount):
        self.pot += amount
        self.players[player_id].remaining_chips -= amount
        self.cur_round.raise_bet(amount)
        self.cur_round.advance_player()

    # checks if current round is over and update self.cur_round
    def __update_round(self):
        if not self.cur_round.completed:
            return
        self.cur_round_cnt += 1
        # check if river round is finished
        if self.cur_round_cnt > 3:
            self.__set_game_ended()
            return
        # check if only 1 player remains
        if len(self.cur_round.remaining_players) == 1:
            self.__set_game_ended()
            return
        self.remaining_players = self.cur_round.remaining_players.copy()
        self.remaining_players_ids = self.cur_round.remaining_players_ids.copy()
        self.cur_round = Round(self.remaining_players)

    # set game ended
    def __set_game_ended(self):
        self.game_over = True
    
    def cleanup(self):
        print('in cleanup()')
        hands = {}
        board = self.flop + self.turn + self.river
        
        for player_id in self.players:
            hands[player_id] = self.players[player_id].current_hand
            print("hand game player id:", player_id)
            print("hand game self.players:", self.players)
            print("hand game hands[player id]:",hands[player_id] )
            
        cleanup_obj = HandCleanup(board, hands, self.pot)
        print("hand_game cleanup : ",hands)
        if len(self.cur_round.remaining_players) == 1:
            res = cleanup_obj.all_fold(self.cur_round.remaining_players_ids[0])
            print(res)
        else:
            res = cleanup_obj.multiple_players(self.cur_round.remaining_players_ids)
            print(res)
        return res
    
    def debug_print(self):
        print(self.remaining_players)

    # defines the string representation of the hand_game obj
    def __str__(self):
        res_str = ''
        res_str += '=================\n'
        res_str += 'players:\n'
        for player_id in self.players:
            res_str += str(self.players[player_id])
            res_str += '\n'
        res_str += ('sb: ' + str(self.sb) + '\n')
        res_str += ('bb: ' + str(self.bb) + '\n')
        res_str += ('pot: ' + str(self.pot) + '\n')
        res_str += ('flop: ' + str(self.flop) + '\n')
        res_str += ('turn: ' + str(self.turn) + '\n')
        res_str += ('river: ' + str(self.river) + '\n')
        res_str += ('cur_round_cnt: ' + str(self.cur_round_cnt) + '\n')
        res_str += ('game_over: ' + str(self.game_over) + '\n')
        return res_str
