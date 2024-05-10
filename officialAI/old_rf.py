import numpy as np
import matplotlib.pyplot as plt
import math
import random
import numpy as np  
import joblib
from keras.models import Sequential
from keras.models import model_from_json

class Old_Rf():
    def new_game_data(self):
        self.game_data = np.zeros(15)
        self.game_data[8]=0
        self.game_data[9]=1
        self.game_data[10:16] = -1
        self.action_count=0
        self.in_chips = np.zeros(10)
        self.chips_to_call = -1
        #print("game_data_from_old_rf: \n",self.game_data)
        return None
    
    def set_hand_level(self,cards):
        #change the hand level simply by changing the array value 
        self.level_array = np.array([[1,1,2,2,3,3,3,3,3,3,3,3,3], 
                                     [1,1,2,3,3,4,5,6,6,6,6,6,6], 
                                     [2,2,1,3,4,4,5,6,6,6,6,6,6],
                                     [3,3,3,2,4,4,5,6,6,6,6,6,6],
                                     [4,4,4,4,2,4,4,5,6,6,6,6,6],
                                     [4,5,5,5,5,3,4,5,5,6,6,6,6],
                                     [4,6,6,5,5,5,3,4,5,6,6,6,6],
                                     [4,6,6,6,6,5,5,4,4,5,6,6,6],
                                     [4,6,6,6,6,6,5,5,4,4,5,6,6],
                                     [4,6,6,6,6,6,6,6,5,4,5,6,6],
                                     [5,6,6,6,6,6,6,6,6,6,4,5,6],
                                     [5,6,6,6,6,6,6,6,6,6,6,4,6],
                                     [5,6,6,6,6,6,6,6,6,6,6,6,4]])  
        hand1=cards[0]
        hand2=cards[1]
        #hand face 1 trans to 14
        if(hand1['face']==1):
            hand1['face']=14
        if(hand2['face']==1):
            hand2['face']=14
        #hand1 is random variable always bigger than hand2
        if(cards[0]['face']>cards[1]['face']):
            hand1=cards[0]
            hand2=cards[1]
        else:
            hand1=cards[1]
            hand2=cards[0]
        #print("set_hand_level hand1,hand2:",hand1," ", hand2)
        suit_same=0
        if(hand1['suite']==hand2['suite']):
            suit_same=1
        self.level=self.set_level(hand1['face'],hand2['face'],suit_same)
        #print("level from set_hand_level: ",self.level)
        return None

    def set_level(self,hand1,hand2,suit_same):
        #find hand1 and hand2 in level array
        if(suit_same):
            level=self.level_array[14-hand1][14-hand2]
        else:
            level=self.level_array[14-hand2][14-hand1]
        return level
    
    def set_blind_bet(self,sb,bb):
        self.sb=sb
        self.bb=bb
        return None

    def card_convert(self,card):
        card_converted=card
        #note that card face A should be sent in as 1 
        if card_converted['face']==1:
            card_converted['face']=14
        card_converted=card
        if card['suite']=="club":
            card_converted['face']=-4+(card['face']-1)*4
        elif card['suite']=="diamond":
            card_converted['face']=-3+(card['face']-1)*4
        elif card['suite']=="heart":
            card_converted['face']=-2+(card['face']-1)*4
        elif card['suite']=="spade":
            card_converted['face']=-1+(card['face']-1)*4
        return card_converted['face']

    def set_flops(self,flop1,flop2,flop3):
        self.flop1=flop1
        self.flop2=flop2
        self.flop3=flop3
        self.game_data[0]=self.card_convert(flop1.copy())
        self.game_data[1]=self.card_convert(flop2.copy())
        self.game_data[2]=self.card_convert(flop3.copy())
        #print(self.flop1)

        #print("set flop in rf: ",self.card_convert(flop1),self.card_convert(flop2),self.card_convert(flop3))
        #print("set flop in rf: ",self.game_data)
        return None
    
    def set_turn(self,turn):
        self.game_data[3]=self.card_convert(turn.copy())
        #print("set turn in rf: ",self.game_data)
        return None
    
    def set_river(self,river):
        self.game_data[4]=self.card_convert(river.copy())
        #print("set river in rf: ",self.game_data)
        return None
    
    def set_hands(self,hands):
        self.hand1=hands[0]
        self.hand2=hands[1]
        self.game_data[6]=self.card_convert(hands[0].copy())
        self.game_data[7]=self.card_convert(hands[1].copy())
        #print("set hands in rf: ",self.game_data)
        return None
    
    def get_action(self,action):
        if(action['action']=="post small blind"):
            return 0
        elif(action['action']=="post big blind"):
            return 1
        elif(action['action']=="raise"):
            return 2
        elif(action['action']=="call"):
            return 3
        elif(action['action']=="check"):
            return 4
        elif(action['action']=="fold"):
            return 8
        elif(action['action']=="allin"):
            return 9
        return -1
    
    def set_action(self,player,action):
        if (player==1 or player==4) and self.action_count<5:
            self.game_data[self.action_count+10]=self.get_action(action.copy())
            self.action_count+=1
        #print("rf set_action: ",self.game_data)
        return None
    
    def set_in_chips(self,player,action):
        #print("old rf set_in_chips player: ",player,"action: ",action)
        self.in_chips[player-1]+=action['amount']
        self.game_data[5]=max(self.in_chips)
        return None
    
    def print_game_data(self):
        print("rf game data: \n",self.game_data,'\n')
        return None


    def predict(self):
        model = joblib.load(r"..\model\RFmodel\my_random_forest.joblib")#path
        action = int(float(model.predict(np.array(self.game_data).reshape(1, -1))))
        #self.print_game_data()
        #print("RF predict number:",action)
        predict_action=self.get_predict_action(action)
        #print("RF predict action: ",predict_action)
        return predict_action 
    
    def set_chips_to_call(self,to_call):
        self.chips_to_call=to_call
        return None

    def get_predict_action(self,action):
        if action==2:
            predict_action={'action':'raise' ,"amount":self.get_raise_amount()}
            return predict_action
        elif action==3:
            predict_action={'action':'call' ,"amount":self.chips_to_call}
            return predict_action
        elif action==4:
            if self.chips_to_call>0:
                predict_action={'action':'call' ,"amount":self.chips_to_call}
            else:
                predict_action={'action':'check' ,"amount":0}
            return predict_action
        elif action==8:
            predict_action={'action':'fold' ,"amount":0}
            return predict_action
        elif action==9:
            predict_action={'action':'raise' ,"amount":self.remaining_chips}
            return predict_action
        else:
            predict_action={'action':'check' ,"amount":0}
            return predict_action
        
    def get_raise_amount(self):
        if 1<=self.level<=2:
            raise_amount= min(self.remaining_chips,self.chips_to_call+3*self.sb)
        elif 3<=self.level<=4:
            raise_amount= min(self.remaining_chips,self.chips_to_call+2*self.sb)
        elif 5<=self.level<=6:
            raise_amount= min(self.remaining_chips,self.chips_to_call+ self.sb)
        return raise_amount

    def set_remaining_chips(self,remaining_chips):
        self.remaining_chips=remaining_chips
        # print("rf remainingchips",self.remaining_chips)
        return None
        


