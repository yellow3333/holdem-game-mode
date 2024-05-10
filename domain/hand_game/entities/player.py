#   This class is for single player entity

class Player():
    def __init__(self, id, name, is_ai, remaining_chips):
        self.id = id
        self.name = name
        self.is_ai = is_ai
        self.remaining_chips = remaining_chips
        self.current_hand = None
    
    # deal cards to this player
    def deal(self, hand):
        self.current_hand = hand
    
    def __str__(self):
        res_str = ''
        res_str += '----\n'
        res_str += ('id: ' + str(self.id) + '\n')
        res_str += ('name: ' + str(self.name) + '\n')
        res_str += ('is_ai: ' + str(self.is_ai) + '\n')
        res_str += ('remaining_chips: ' + str(self.remaining_chips) + '\n')
        res_str += ('current_hand: ' + str(self.current_hand) + '\n')
        return res_str
