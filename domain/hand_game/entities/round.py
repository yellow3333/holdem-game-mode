# This class is for the state of a round of game play
class Round():
    def __init__(self, starting_players):
        self.starting_players = starting_players.copy()
        self.remaining_players = starting_players.copy()
        self.remaining_players_ids = list(self.remaining_players.keys())
        self.bet = self.__init_bet().copy()
        self.current_position = 0
        self.top_bet = 0
        self.still_raise = False
        self.last_raise_id = self.remaining_players_ids[0]
        self.completed = False
    
    def __init_bet(self):
        res = {}
        for i in self.remaining_players_ids:
            res[i] = 0
        return res

    def advance_player(self):
        self.current_position += 1
        self.current_position %= len(self.remaining_players)
        self.__check_and_set_completed()
    
    # remove the current player
    # also advances the current player
    def remove_current_player(self):
        current_id = self.remaining_players_ids.pop(self.current_position)
        self.remaining_players.pop(current_id)
        self.current_position %= len(self.remaining_players)
        self.__check_and_set_completed()
        # fix strange guys folding their card as raise leader
        if self.last_raise_id not in self.remaining_players_ids:
            self.last_raise_id = self.remaining_players_ids[self.current_position]
    
    def raise_bet(self, amount):
        self.top_bet = amount
        self.still_raise = True
        cur_id = self.get_current_player_id()
        self.bet[cur_id] = amount
        self.last_raise_id = self.remaining_players_ids[self.current_position]
    
    def get_current_player(self):
        current_id = self.remaining_players_ids[self.current_position]
        return self.remaining_players[current_id]
    
    def get_current_player_id(self):
        return self.remaining_players_ids[self.current_position]
    
    def to_call(self, player_id):
        return self.top_bet - self.bet[player_id]

    def __check_and_set_completed(self):
        if len(self.remaining_players) == 1:
            self.completed = True
            return
        if self.remaining_players_ids[self.current_position] == self.last_raise_id:
            self.completed = True
            return
        self.completed = False
    
    
