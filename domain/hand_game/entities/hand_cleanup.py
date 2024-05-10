# This class handles game cleanup

from domain.hand_game.entities.hand_comparator import *

class HandCleanup():
    # hand: {$player_id: $hand}
    def __init__(self, board, hands, pot):
        self.board = board.copy()
        self.hands = hands.copy()
        self.pot = pot

    def all_fold(self, remaining_player_id):
        return [(remaining_player_id, self.pot)]

    def multiple_players(self, remaining_player_id):
        print('in multiple_players')
        print('remaining player id',remaining_player_id)
        compare_obj = HandComparator()
        hands = []
        hands_id = []
        for player_id in remaining_player_id:
            hands.append(self.hands[player_id])
            hands_id.append(player_id)
            print('hand_cleanup player id: ',player_id)
            print('hand_cleanup board', self.board)
            print('hand_cleanup hands : ',hands)
            print('hand_cleanup hands id: ',hands_id)
            
        comp_res = compare_obj.translate_and_compare(self.board, hands)
        print('hand_cleanup comp_res = ')
        print(comp_res)
        if len(comp_res[1]) > 0: # chop pot
            res = []
            chop_size = self._calculate_chop(self.pot, len(comp_res[1]))
            for p in comp_res[1]:
                res.append((hands_id[p], chop_size))
            return res
        else:
            return [(hands_id[comp_res[0]], self.pot)]
    
    # use floor to chop pot
    def _calculate_chop(self, pot, count):
        print("hand_cleanup pot // count",pot//count)
        return pot // count
    