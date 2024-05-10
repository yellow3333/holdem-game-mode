import numpy as np
import matplotlib.pyplot as plt
import math
import random
import numpy as np
import joblib
from keras.models import Sequential
from keras.models import model_from_json
from officialAI.new_cnn import New_Cnn
from officialAI.old_cnn import Old_Cnn
from officialAI.old_rf import Old_Rf



class TexasAI():
    def __init__(self,i):
        self.ai_model_id=i
        
        if(self.ai_model_id==2):
            self.ai_model_id=2
            self.old_cnn=Old_Cnn()
        elif(self.ai_model_id==3):
            self.ai_model_id=3
            self.new_cnn=New_Cnn()
        elif(self.ai_model_id==4):
            self.ai_model_id=4
            self.old_rf=Old_Rf()
        return None

    def new_game(self, player_count, start_chip, bb, sb, position):
        self.player_count=player_count
        self.position=position    
        self.remaining_chips=start_chip
        self.bb=bb
        self.sb=sb
        
        if(self.get_ai_model_id()==1):
            print("ai_model new_game id 1 position",self.position)
        elif(self.get_ai_model_id()==2):
            print("ai_model new_game id 2 position",self.position)
            self.old_cnn.new_game_data()
            self.old_cnn.set_remaining_chips(self.remaining_chips)
            self.old_cnn.set_blind_bet(sb,bb)
            self.old_cnn.set_blind_order(self.position)
            #self.old_cnn.print_game_data()
        elif(self.get_ai_model_id()==3):
            print("ai_model new_game id 3 position",self.position)
            self.new_cnn.set_players(self.player_count)
            self.new_cnn.new_game_data()
            self.new_cnn.set_blind_bet(sb,bb)
            self.new_cnn.set_remaining_chips(self.remaining_chips)
            self.new_cnn.set_blind_order(self.position)
            #self.new_cnn.print_game_data()
        elif(self.get_ai_model_id()==4):
            print("ai_model new_game id 4 position",self.position)
            self.old_rf.new_game_data()
            self.old_rf.set_blind_bet(sb,bb)
            self.old_rf.set_remaining_chips(self.remaining_chips)
        return None
    

    
    def get_ai_model_id(self):
        return self.ai_model_id

    def observe_board(self, card_tier, cards):
        #print("observe board in ai_model: \n",card_tier ,"observe hand in ai_model: ",cards)
        self.card_tier = card_tier
        if self.card_tier == 1:
            self.flop1 = cards[0]
            self.flop2 = cards[1]
            self.flop3 = cards[2]
            self.turn = None
            self.river = None
            if(self.get_ai_model_id()==1):
                #print("ai_model id 1")
                pass
            elif(self.get_ai_model_id()==2):
                #print("ai_model id 2")
                self.old_cnn.set_flops(self.flop1,self.flop2,self.flop3)
                #print("old cnn id 2 flops",self.flop1,self.flop2,self.flop3)
                #self.old_cnn.print_game_data()
            elif(self.get_ai_model_id()==3):
                #print("ai_model id 3")
                self.new_cnn.set_flops(self.flop1,self.flop2,self.flop3)
                #self.new_cnn.print_game_data()
            elif(self.get_ai_model_id()==4):
                #print("ai_model id 4")
                self.old_rf.set_flops(self.flop1,self.flop2,self.flop3)

        elif self.card_tier == 2:
            self.turn = cards[0]
            self.river = None
            if(self.get_ai_model_id()==1):
                #print("ai_model id 1")
                pass
            elif(self.get_ai_model_id()==2):
                #print("ai_model id 2")
                self.old_cnn.set_turn(cards[0])
            elif(self.get_ai_model_id()==3):
                #print("ai_model id 3")
                self.new_cnn.set_turn(cards[0])
            elif(self.get_ai_model_id()==4):
                #print("ai_model id 4")
                self.old_rf.set_turn(cards[0])

        elif self.card_tier == 3:
            self.river = cards[0]
            if(self.get_ai_model_id()==1):
                #print("ai_model id 1")
                pass
            elif(self.get_ai_model_id()==2):
                #print("ai_model id 2")
                self.old_cnn.set_river(cards[0])
            elif(self.get_ai_model_id()==3):
                #print("ai_model id 3")
                self.new_cnn.set_river(cards[0])
            elif(self.get_ai_model_id()==4):
                #print("ai_model id 4")
                self.old_rf.set_river(cards[0])
        # print("observe board: ", self.flop1,self.flop2,self.flop3,self.turn,self.river)
        return None

    def observe_hand(self, cards):
        print("observe hand in ai_model: \n",self.ai_model_id ,"observe hand in ai_model: ",cards)
        self.hands=[cards[0],cards[1]]
        if(self.get_ai_model_id()==1):
            #print("ai_model action id 1")
            pass
        elif(self.get_ai_model_id()==2):
            print("ai_model action id 2")
            self.old_cnn.set_hands(self.hands)
            self.old_cnn.set_hand_level(self.hands)
        elif(self.get_ai_model_id()==3):
            print("ai_model action id 3")
            self.new_cnn.set_hands(self.hands)
            self.new_cnn.set_hand_level(self.hands)
        elif(self.get_ai_model_id()==4):
            print("ai_model action id 4")
            self.old_rf.set_hands(self.hands)
            self.old_rf.set_hand_level(self.hands)
        return None

    def observe_action(self, player, action, to_call):
        print('in TexasAI.observe_action: action ',action,'to_call ',to_call)
        if(self.get_ai_model_id()==1):
            #print("ai_model new_game id 1")
            pass
        elif(self.get_ai_model_id()==2):
            print("ai_model new_game id 2")
            self.old_cnn.set_in_chips(player,action)
            if to_call!=-1:
                self.old_cnn.set_chips_to_call(to_call)
        elif(self.get_ai_model_id()==3):
            print("ai_model new_game id 3")
            self.new_cnn.set_player_action(player,action)
            self.new_cnn.set_in_chips(player,action)
            if to_call!=-1:
                self.new_cnn.set_chips_to_call(to_call)
        elif(self.get_ai_model_id()==4):
            print("ai_model new_game id 4")
            self.old_rf.set_in_chips(player,action)
            self.old_rf.set_action(player,action)
            if to_call!=-1:
                self.old_rf.set_chips_to_call(to_call)
        return None

    def action(self):
        action={"action":"fold", "amount":0}
        if(self.get_ai_model_id()==1):
            #print("ai_model action id 1")
            pass
        elif(self.get_ai_model_id()==2):
            #print("ai_model action id 2")
            action=self.old_cnn.predict()
            print("action id 2 predict:",action)
            return action
        elif(self.get_ai_model_id()==3):
            #print("ai_model action id 3")
            action=self.new_cnn.predict()
            print("action id 3 predict:",action)
            return action
        elif(self.get_ai_model_id()==4):
            #print("ai_model action id 4")
            action=self.old_rf.predict()
            print("action id 4 predict:",action)
            return action
        return action

    def end_game(self, winners, prizes, observe_hands):
        print('in TexasAI.end_game')
        print(winners)
        print(prizes)
        print(observe_hands)
        pass
    
    def observe_remaining_chips(self,remaining_chips):
        self.remaining_chips=remaining_chips
        if(self.get_ai_model_id()==1):
            #print("ai_model remaining_chips id 1:",remaining_chips)
            pass
        elif(self.get_ai_model_id()==2):
            #print("ai_model action id 2")
            self.old_cnn.set_remaining_chips(self.remaining_chips)
        elif(self.get_ai_model_id()==3):
            #print("ai_model action id 3")
            self.new_cnn.set_remaining_chips(self.remaining_chips)
        elif(self.get_ai_model_id()==4):
            #print("ai_model remaining_chips id 4:",remaining_chips)
            self.old_rf.set_remaining_chips(self.remaining_chips)

        return None
    
