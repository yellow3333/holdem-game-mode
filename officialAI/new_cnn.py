import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import math
import random
import numpy as np  
import joblib
import itertools
from keras.models import Sequential
from keras.models import model_from_json
#new_cnn.py handles the data from front-end, transform it to 2d-array and send it to new cnn that has been trained

class New_Cnn():
    def set_chips_to_call(self,to_call):
        self.chips_to_call=to_call
        return None
    
    def set_blind_bet(self,sb,bb):
        self.sb=sb
        self.bb=bb
        return None
    
    def set_blind_order(self,position): 
        #ai itself is small blind 0 else 1
        #0 for small blind 1 for big blind
        self.position=position
        if self.get_players()==3:
            if self.position==0:
                self.game_data[11]=[1,-1,-1,-1,-1,-1,0,-1,-1,-1,-1,-1,2]
            elif self.position==1:
                self.game_data[11]=[-1,-1,-1,0,-1,-1,1,-1,-1,-1,-1,-1,1]
            elif self.position==2:
                self.game_data[11]=[0,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,3]

        elif self.get_players()==4:
            if self.position==0:
                self.game_data[11]=[-1,-1,-1,-1,-1,-1,0,-1,-1,1,-1,-1,2]
            elif self.position==1:
                self.game_data[11]=[-1,-1,-1,0,-1,-1,1,-1,-1,-1,-1,-1,1]
            elif self.position==2:
                self.game_data[11]=[1,-1,-1,-1,-1,-1,-1,-1,-1,0,-1,-1,3]
            elif self.position==3:
                self.game_data[11]=[0,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,4]

        #print("new_cnn blind/show in blind: ",self.game_data[11])
        #self.print_game_data()
        return None
    
    def print_game_data(self):
        print("game data from new cnn: \n",self.game_data)
        return None
    
    def store_to_game_data(self,cards,row):
        #row 1 means storing to array row index 1
        #1~3: flop1~3
        #4: turn
        #5: river
        #6: hand0
        #7: hand1
        r=row
        face=cards['face']
        suite=cards['suite']
        #card1 face 1 trans to 14
        if(face==1):
            face=14

        #[row][culumn]
        if(suite=='club'):#club=1
            self.game_data[r, :] = 0
            self.game_data[r][face-2]=1

        elif(suite=='diamond'):#diamond=2
            self.game_data[r, :] = 0
            self.game_data[r][face-2]=2

        elif(suite=='heart'):#heart=3
            self.game_data[r, :] = 0
            self.game_data[r][face-2]=3

        elif(suite=='spade'):#spade=4
            self.game_data[r, :] = 0
            self.game_data[r][face-2]=4
        return None
    
    def set_flops(self,flop1,flop2,flop3):
        #print("new_cnn receive flops from ai model: ",flop1,flop2,flop3)
        self.flop1=flop1
        self.flop2=flop2
        self.flop3=flop3
        self.store_to_game_data(flop1,1)
        self.store_to_game_data(flop2,2)
        self.store_to_game_data(flop3,3)
        cards=[self.hand1,self.hand2,self.flop1,self.flop2,self.flop3]
        print("strength from set flops: ",self.get_highest_strength(cards))
        return None
    
    def set_players(self,player_count):
        self.player_count=player_count
        return None
    
    def get_players(self):
        return self.player_count

    def new_game_data(self):
        self.game_data = np.full((12, 13), 0)
        #flop1,2,3,turn,river initial=-1 
        self.game_data[1:6, :] = -1
        #action initial=-1
        self.game_data[10:11,:]=-1
        self.chips_to_call=0
        self.strength=0
        self.in_chips=np.zeros(4)
        self.action_count=0
        return None
    
    def set_turn(self,turn):
        #print("new_cnn receive turn from ai model: ",turn)
        self.turn=turn
        self.store_to_game_data(turn,4)
        cards=[self.hand1,self.hand2,self.flop1,self.flop2,self.flop3,self.turn]
        print("strength from set turn: ",self.get_highest_strength(cards))
        return None
    
    def set_river(self,river):
        #print("new_cnn receive river from ai model: ",river)
        self.river=river
        self.store_to_game_data(river,5)
        cards=[self.hand1,self.hand2,self.flop1,self.flop2,self.flop3,self.turn,self.river]
        print("strength from set river: ",self.get_highest_strength(cards))
        return None
    
    def set_hands(self,hands):
        #print("new_cnn receive hand1 and hand2 from ai model: ",hands)
        self.hand1=hands[0]
        self.hand2=hands[1]
        self.store_to_game_data(hands[0],6)
        self.store_to_game_data(hands[1],7)
        #once you know the hands value you can update strength
        cards=[self.hand1,self.hand2]
        #print("strength from set hands: ",self.set_strength(cards))
        self.store_strength_to_game_data(self.set_strength(cards))
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
        self.store_level_to_game_data(self.level)
        return None
    
    #decide which level and store level are seperate functions, considering old cnn and new cnn store data differently
    #You can see more info in the document
    def store_level_to_game_data(self,level):
        self.game_data[8][2*level-2:2*level+1] = [1]
        return None
            
    def set_level(self,hand1,hand2,suit_same):
        #find hand1 and hand2 in level array
        if(suit_same):
            level=self.level_array[14-hand1][14-hand2]
        else:
            level=self.level_array[14-hand2][14-hand1]
        return level

    def set_strength(self,cards):
    # Count the occurrences of each face value and suit
        face_counts = {}
        suit_counts = {}
        
        for card in cards:
            face = card['face']
            suit = card['suite']

            face_counts[face] = face_counts.get(face, 0) + 1
            suit_counts[suit] = suit_counts.get(suit, 0) + 1

        # Check for flush
        flush = any(count >= 5 for count in suit_counts.values())

        # Check for straight
        straight = False
        faces = sorted(face_counts.keys())

        if len(faces) >= 5:
            for i in range(len(faces) - 4):
                if faces[i] + 4 == faces[i + 4]:
                    straight = True
                    break

        # Check for straight flush and royal flush
        straight_flush = straight and flush
        royal_flush = straight_flush and 1 in faces and 10 in faces and 11 in faces and 12 in faces and 13 in faces

        # Determine the strength based on the hand
        if royal_flush:
            return 12
        elif straight_flush:
            return 11
        elif any(count == 4 for count in face_counts.values()):
            return 10
        elif set(face_counts.values()) == {2, 3}:
            return 9
        elif flush:
            return 8
        elif straight:
            return 7
        elif any(count == 3 for count in face_counts.values()):
            return 6
        elif len(face_counts) == 3 and set(face_counts.values()) == {1,2,2}:
            return 5
        elif any(count == 2 for count in face_counts.values()):
            return 4
        elif len(faces) >= 5:
            return 3
        elif len(faces) >= 4:
            return 2
        elif len(faces) >= 3:
            return 1
        else:
            return 0

    def get_highest_strength(self,all_cards):
        combinations = itertools.combinations(all_cards, 5)
        max_strength = 0

        for combination in combinations:
            strength = self.set_strength(combination)
            max_strength = max(max_strength, strength)

        self.strength=max_strength
        self.store_strength_to_game_data(max_strength)
        return max_strength
    
    def store_strength_to_game_data(self,strength):
        self.game_data[0][:] = [0]
        self.game_data[0][strength]=1
        return None
    
    def set_in_chips(self,player,action):
        #print("new cnn set_in_chips player: ",player,"action: ",action)
        self.in_chips[player-1]+=action['amount']
        self.set_chips_strength()
        #self.print_in_chips()
        #self.print_game_data()
        return None
    
    def print_in_chips(self):
        print("new cnn in_chips:",self.in_chips)
        return None

    def set_chips_strength(self):
        #print("new cnn set chips strength:",self.in_chips)
        for index,chips_value in enumerate(self.in_chips):
            if chips_value < np.max(self.in_chips)/3:
                #print("index", index)
                self.store_chips_to_game_data(index,1)
            elif np.max(self.in_chips)/3 <= chips_value < np.max(self.in_chips)*2/3:
                self.store_chips_to_game_data(index,2)
            else:
                self.store_chips_to_game_data(index,3)
        return None

    def store_chips_to_game_data(self,index,chip_strength):
        self.game_data[9][index+chip_strength] = 1
        #chip strength 3:001,2:010,1:100
        #print("new cnn store chips to game data game data:",self.game_data)
        return None
    
    def get_action(self,action):
        if(action['action']=="raise"):
            if self.chips_to_call>0:
                return 2
            else:
                return 5 #bet
        elif(action['action']=="call"):
            return 3
        elif(action['action']=="check"):
            return 4
        elif(action['action']=="fold"):
            return 8
        else:
            return 4

    def set_player_action(self,player,action):
        self.action_count+=1
        if self.action_count<2:
            pass
        else:
            if self.get_action(action)==8: # action==fold
                if player!=1:
                    self.game_data[11,player*3-2:player*3]=0
                else:
                    self.game_data[11][1:3]=0                   

            if(self.get_players()==3):
                indices = np.argwhere(self.game_data[10] == -1)
                if indices.size > 0:
                    index = indices[0][0]
                    self.game_data[10][index] = self.get_action(action)

                    

            elif(self.get_players()==4):
                indices = np.argwhere(self.game_data[10] == -1)
                if indices.size > 0:
                    index = indices[0][0]
                    self.game_data[10][index] = self.get_action(action)
                    if self.get_action(action)==8: # action==fold
                        if player!=1:
                            self.game_data[11,player*3-2:player*3]=0
                        else:
                            self.game_data[11][0:2]=0

        #self.print_game_data()
        return None
    
    def print_player_in_chips(self):
        print("players_in_chips total: ",self.in_chips)
        return None
    

    def predict(self):
        
        if self.get_players()==3:
            with open("..\\model\\NCmodel\\model-3p\\model3.config", "r") as json_file:#path
                json_string = json_file.read()
            model = Sequential()
            model = model_from_json(json_string)
            model.load_weights("..\\model\\NCmodel\\model-3p\\model3.weight", by_name=False) #path
        elif self.get_players()==4:
            with open("..\\model\\NCmodel\\model-4p\\model4.config", "r") as json_file:#path
                json_string = json_file.read()
            model = Sequential()
            model = model_from_json(json_string)
            model.load_weights("..\\model\\NCmodel\\model-4p\\model4.weight", by_name=False) #path
            
        input=np.array(self.game_data)
        X2 = input.astype('float32') 
        X1 = X2.reshape(1,12,13,1)
        predictions = model.predict(X1)
        predict = np.argmax(predictions,1)
        predict = predict[0]
        #self.print_game_data()
        print("predict number in new cnn:",predict)

        if predict==0 or predict==3:#raise #bet
            action=self.raise_and_all_in_strategy()
        elif predict==1 or predict==2:#call , check
            action=self.call_and_check_strategy()
        elif predict==4:#fold
            action={"action":"fold","amount":0}
        return action
    
    def call_and_check_strategy(self):
        if self.chips_to_call>0:
            action={"action":"call", "amount":self.chips_to_call}
        else:
            action={"action":"check", "amount":0}
        return action
    
    def raise_and_all_in_strategy(self):
        if 8<=self.strength<=12:#all_in
            action={'action':"raise",'amount':self.remaining_chips}
        elif 4<=self.strength<=7:#raise
            if self.chips_to_call>0:#re_raise
                action={'action':"raise",'amount':min(self.remaining_chips,self.chips_to_call+3*self.sb)}
            else:#raise
                action={'action':"raise",'amount':min(self.remaining_chips,3*self.sb)}
        elif 2<=self.strength<=3:#raise
            if self.chips_to_call>0:#re_raise
                action={'action':"raise",'amount':min(self.remaining_chips,self.chips_to_call+3*self.sb)}
            else:#raise
                action={'action':"raise",'amount':min(self.remaining_chips,2*self.sb)}
        else:
            if self.chips_to_call>0:#re_raise
                action={'action':"raise",'amount':min(self.remaining_chips,self.chips_to_call+3*self.sb)}
            else:#raise
                action={'action':"raise",'amount':min(self.remaining_chips,2*self.sb)}
        return action
    
    def set_remaining_chips(self,remaining_chips):
        self.remaining_chips=remaining_chips
        #print("nc remainingchips",self.remaining_chips)
        return None



