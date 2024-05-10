import numpy as np
import matplotlib.pyplot as plt
import math
import random
import numpy as np  
import joblib
import sys
from collections import Counter
import itertools
from keras.models import Sequential
from keras.models import model_from_json


class Old_Cnn():
    def new_game_data(self):
        self.game_data = np.full((13, 13), 0)
        #flop1,2,3,turn,river initial=-1 
        self.game_data[1:6, :] = -1
        self.in_chips=np.zeros(4)# Old Cnn is for two players but 2 more for extention
        self.in_chips_level=np.zeros(4)
        self.strength=0
        self.chips_to_call=0
        self.is_river=0
        return None
    
    def set_blind_bet(self,sb,bb):
        self.sb=sb
        self.bb=bb
        return None

    def set_chips_to_call(self,to_call):
        self.chips_to_call=to_call
        #print("in old cnn set chips to call: ",self.chips_to_call)
        return None

    def set_blind_order(self,position): #ai itself is small blind 0110 else 0011
        #0 for small blind 1 for big blind
        self.position=position
        if self.position==0:
            self.game_data[11,0:4]=[0,1,1,0]
        else:
            self.game_data[11,0:4]=[0,0,1,1]
        return None

    def print_game_data(self):
        print("game data from old cnn: \n",self.game_data)
        return None
    
    def set_hands(self,hands):
        #print("old_cnn receive hand1 and hand2 from ai model: ",hands)
        self.hand1=hands[0]
        self.hand2=hands[1]
        self.store_to_game_data(hands[0],6)
        self.store_to_game_data(hands[1],7)
        #once you know the hands value you can update strength
        cards=[self.hand1,self.hand2]
        #print("strength from set hands: ",self.set_strength(cards))
        self.store_strength_to_game_data(self.set_strength(cards))
        return None
    
    def store_to_game_data(self,cards,row):
        #row 1 means storing to array row index 1
        #1~3: flop1~3
        #4: turn
        #5: river
        #6: hand0
        #7: hand1
        #print("in old cnn id 2 store to game data: cards, r: ",cards,row)
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
    
    def store_strength_to_game_data(self,strength):
        self.game_data[0][:] = [0]
        self.game_data[0][strength]=1
        return None
    
    def set_hand_level(self,cards):
        #You can change the hand level simply by changing the array value 
        self.level_array = np.array([[1,1,1,1,1,3,3,3,3,2,2,2,4], 
                                     [1,1,1,1,2,3,3,4,4,4,4,4,5], 
                                     [1,2,1,1,2,3,4,4,4,4,4,5,5],
                                     [2,3,3,1,2,3,4,4,4,4,5,5,5],
                                     [3,3,3,3,1,2,3,4,4,5,5,5,5],
                                     [3,4,4,3,3,2,2,3,4,5,5,5,5],
                                     [4,4,4,4,4,3,2,2,3,4,5,5,5],
                                     [4,4,4,5,4,4,4,2,3,3,4,5,5],
                                     [4,4,5,5,5,5,4,4,2,3,4,4,5],
                                     [4,5,5,5,5,5,5,4,4,3,4,4,5],
                                     [4,5,5,5,5,5,5,5,5,5,3,4,5],
                                     [4,5,5,5,5,5,5,5,5,5,5,3,5],
                                     [5,5,5,5,5,5,5,5,5,5,5,5,3]])
        #print("level array in old cnn:\n",self.level_array)   
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

    def set_level(self,hand1,hand2,suit_same):
        #find hand1 and hand2 in level array
        if(suit_same):
            level=self.level_array[14-hand1][14-hand2]
        else:
            level=self.level_array[14-hand2][14-hand1]
        return level

    #decide which level and store level are seperate functions, considering old cnn and new cnn store data differently
    #You can see more info in the document
    def store_level_to_game_data(self,level):
        if(level<=3):
            self.game_data[8][level-1:level-1+level]=[1]
        elif(level>3):
            self.game_data[8][level*3-7:level*3-7+level]=[1]
        return None

    def set_flops(self,flop1,flop2,flop3):
        #print("old_cnn receive flops from ai model: ",flop1,flop2,flop3)
        self.flop1=flop1
        self.flop2=flop2
        self.flop3=flop3
        self.store_to_game_data(flop1,1)
        self.store_to_game_data(flop2,2)
        self.store_to_game_data(flop3,3)
        cards=[self.hand1,self.hand2,self.flop1,self.flop2,self.flop3]
        print("strength from set flops: ",self.get_highest_strength(cards))
        return None

    def get_highest_strength(self,all_cards):
        strength = self.set_strength(all_cards)
        self.strength = max(self.strength, strength)
        self.store_strength_to_game_data(self.strength)
        return self.strength
    
    def set_turn(self,turn):
        #print("old_cnn receive turn from ai model: ",turn)
        self.turn=turn
        self.store_to_game_data(turn,4)
        #print("game_data_from new_cnn after turn: ",self.game_data)
        cards=[self.hand1,self.hand2,self.flop1,self.flop2,self.flop3,self.turn]
        print("strength from set turn: ",self.get_highest_strength(cards))
        return None
    
    def set_river(self,river):
        #print("old_cnn receive river from ai model: ",river)
        self.river=river
        self.is_river=1
        self.store_to_game_data(river,5)
        cards=[self.hand1,self.hand2,self.flop1,self.flop2,self.flop3,self.turn,self.river]
        print("strength from set river: ",self.get_highest_strength(cards))
        return None
    
    #set_strength() to be changed
    #I didint write strength 9 because it exists design bug, can't fix this bug unless you change the strength definition or it will always be recorded as strength 12
    #note that if it fits more than one strength,
    #it will be recorded as the higher one
    def set_strength(self,cards):
        if len(cards)<=2:
            if self.find_one_pair(cards):
                return 1
            else:
                return 0
        
        if self.count_continuous_faces(cards)==4:#strength 12 still need one card to be straight
            return 12
        if self.count_continuous_faces(cards)==3:
            face_array=[card.get('face') for card in cards]
            if max(self.longest_subsequence(cards))+2 in face_array or max(self.longest_subsequence(cards))-4 in face_array:
                return 12
        if self.is_straight_still_need_one_card(cards):
            return 12
        
        if self.count_same_suites(cards)==3 :
            return 11
        if self.count_same_suites(cards)==4:
            return 10
        if len(cards)>=5 and self.find_straight_flush(cards):
            return 8
        if self.count_same_faces(cards)==4:
            return 7
        if self.find_fullhouse(cards)==1:
            return 6
        if self.count_same_suites(cards)>=5:
            return 5
        if self.count_continuous_faces(cards)>=4:
            if self.count_continuous_faces(cards)>=5:
                return 4
            elif self.find_card_with_value(cards,1)['face']==1:
                if self.face_A_is_straight(cards):
                    return 4
        if self.count_same_faces(cards)==3:
            return 3
        if self.find_two_pairs(cards):
            return 2
        if self.find_one_pair(cards):
            return 1
        else:
            return 0

    def set_in_chips(self,player,action):
        #print("old cnn set_in_chips player: ",player,"action amount: ",action)
        self.in_chips[player-1]+=action['amount']
        self.store_chips_level(player)
        #self.print_in_chips()
        #self.print_in_chips_level()
        #self.print_game_data()
        return None

    def store_chips_level(self,player_id):
        if self.in_chips[player_id-1]<=1:
            self.in_chips_level[player_id-1]=0
        elif self.in_chips[player_id-1]<17:
            self.in_chips_level[player_id-1]=1
        elif self.in_chips[player_id-1]<30:
            self.in_chips_level[player_id-1]=2
        elif self.in_chips[player_id-1]<45:
            self.in_chips_level[player_id-1]=3
        elif self.in_chips[player_id-1]<57:
            self.in_chips_level[player_id-1]=4
        elif self.in_chips[player_id-1]<80:
            self.in_chips_level[player_id-1]=5
        elif self.in_chips[player_id-1]<125:
            self.in_chips_level[player_id-1]=6
        elif self.in_chips[player_id-1]<200:
            self.in_chips_level[player_id-1]=7
        elif self.in_chips[player_id-1]<225:
            self.in_chips_level[player_id-1]=8
        elif self.in_chips[player_id-1]<290:
            self.in_chips_level[player_id-1]=9
        elif self.in_chips[player_id-1]<400:
            self.in_chips_level[player_id-1]=10 
        elif self.in_chips[player_id-1]<650:
            self.in_chips_level[player_id-1]=11
        elif self.in_chips[player_id-1]>=650: 
            self.in_chips_level[player_id-1]=12 
        self.store_chips_level_to_game_data(1,self.in_chips_level[0])
        self.store_chips_level_to_game_data(2,self.in_chips_level[1])
        return None

    def store_chips_level_to_game_data(self,player_id,chips_level):
        self.game_data[player_id+8][:]=0
        self.game_data[player_id+8][int(chips_level)]=1
        return None
    
    def print_in_chips(self):
        print("old cnn in_chips: ",self.in_chips)
        return None
    
    def print_in_chips_level(self):
        print("old cnn in_chips_level: ",self.in_chips_level)

    def predict(self):
        if self.strength==0 and self.is_river==1:
            action={'action':'fold','amount':0}
            return action
        else:
            with open('..\\model\\OCmodel\\model.config', 'r') as text_file: #path
                json_string = text_file.read()
            model = Sequential()
            model = model_from_json(json_string)
            model.load_weights("..\\model\\OCmodel\\model.weight", by_name=False) #path
            # read my data
            input=np.array(self.game_data)
            X2 = input.astype('float32')  
            X1 = X2.reshape(1,13,13,1)
            predictions = model.predict(X1)
            predict = np.argmax(predictions,1)
            predict = predict[0]
            #self.print_game_data()
            #print("predict in old cnn:",predict)
            if predict==0:#raise
                if 8<=self.strength<=12:
                    action={"action":"raise", "amount":min(self.remaining_chips,self.chips_to_call+8*self.sb)}
                elif 4<=self.strength<=7:
                    action={"action":"raise", "amount":min(self.remaining_chips,self.chips_to_call+6*self.sb)}
                elif 0<=self.strength<=3:
                    action={"action":"raise", "amount":min(self.remaining_chips,self.chips_to_call+5*self.sb)}
            elif predict==1:#call
                action={"action":"call", "amount":self.chips_to_call}
            elif predict==2:#check
                if self.chips_to_call>0:
                    action={"action":"call", "amount":self.chips_to_call}
                else:
                    action={"action":"check", "amount":0}
            print("old cnn action: ",action)
            return action
    

    def set_remaining_chips(self,remaining_chips):
        self.remaining_chips=remaining_chips
        #print("oc remainingchips",self.remaining_chips)
        return None

#----functions used for strength-----------------------------------
    def count_same_suites(self,cards):
        suits_count = Counter(card['suite'] for card in cards)
        max_same_suit_count = max(suits_count.values(), default=0)
        return max_same_suit_count
    
    def get_max_faces(self,cards):
        max_face = -1
        for card in cards:
            if card['face'] > max_face:
                max_face = card['face']
        return max_face
    
    def get_min_faces(self,cards):
        min_face = 20 
        for card in cards:
            if card['face'] < min_face :
                min_face = card['face']
        return min_face
    
    def count_continuous_faces(self,cards):
        faces = set(card['face'] for card in cards)
        continuous_count = 0
        max_continuous_count = 0
        previous_face = None

        for face in sorted(faces):
            if previous_face is not None and face - previous_face == 1:
                continuous_count += 1
            else:
                continuous_count = 1
            max_continuous_count = max(max_continuous_count, continuous_count)

            previous_face = face
        return max_continuous_count
        
    def count_same_faces(self,cards):
        face_count = Counter(card['suite'] for card in cards)
        max_same_face_count = max(face_count.values(), default=0)
        return max_same_face_count
    
    def is_straight_flush(self,hand):
            sorted_hand = sorted(hand, key=lambda x: (x['face'], x['suite']))
            suite = sorted_hand[0]['suite']
            faces = [card['face'] if card['face'] != 1 else 14 for card in sorted_hand]
            
            if len(set(faces)) != 5:
                return False
            for i in range(1, 5):
                if sorted_hand[i]['suite'] != suite or faces[i] != faces[i - 1] + 1:
                    return False
            return True

    def find_straight_flush(self,cards):
        if len(cards) < 5:
            return False
        
        if self.find_card_with_value(cards,1):
            cards.append({'suite': self.find_card_with_value(cards,1)['suite'], 'face': 14})

        combinations = itertools.combinations(cards, 5)

        for combination in combinations:
            if self.is_straight_flush(combination):
                sorted_cards = sorted(combination, key=lambda x: (x['face'], x['suite']))
                print("Found a straight flush combination:")
                for card in sorted_cards:
                    if card['face']==14:
                        card['face']=1
                    print(card)
                return True
        print("No straight flush combination found.")
        return False
    
    def find_card_with_value(self,cards, value):
        for card in cards:
            if card['face'] == value:
                return card
        return None

    def face_A_is_straight(self,cards):
        cards.append({'suite': self.find_card_with_value(cards,1)['suite'], 'face': 14})
        if self.count_continuous_faces(cards)>=5:
            return True
        else:
            return False
    
    def find_fullhouse(self,cards):
        combinations = itertools.combinations(cards, 5)
        for combination in combinations:
            if self.is_fullhouse(combination):
                sorted_cards = sorted(combination, key=lambda x: (x['face'], x['suite']))
                print(sorted_cards)
                return True 
        return False

    def is_fullhouse(self,hand):
        ranks = [card['face'] for card in hand]
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        if len(rank_counts) != 2 or 3 not in rank_counts.values() or 2 not in rank_counts.values():
            return False
        return True
    
    def find_two_pairs(self,cards):
        if len(cards) < 4:
            return False
        
        combinations = itertools.combinations(cards, 4)

        for combination in combinations:
            if self.is_two_pairs(combination):
                sorted_cards = sorted(combination, key=lambda x: (x['face'], x['suite']))
                print(sorted_cards)
                return True 
        return False
    
    def is_two_pairs(self,hand):
        ranks = [card['face'] for card in hand]
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        if len(rank_counts) != 2 or not all(count >= 2 for count in rank_counts.values()):
            return False
        return True
    
    def find_one_pair(self,cards):
        if len(cards) < 2:
            return False
        print('cards find one pair:',cards)
        combinations = itertools.combinations(cards, 2)

        for combination in combinations:
            if self.is_one_pair(combination):
                sorted_cards = sorted(combination, key=lambda x: (x['face'], x['suite']))
                print(sorted_cards)
                return True 
        return False
    
    def is_one_pair(self,hand):
        ranks = [card['face'] for card in hand]
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        if len(rank_counts) != 1 or not all(count >= 2 for count in rank_counts.values()):
            return False
        return True

    def longest_subsequence(self,cards):
        a=[card.get('face') for card in cards]
        n=len(a)
        # stores the index of elements
        mp = {i:0 for i in range(13)}
        # stores the length of the longest
        # subsequence that ends with a[i]
        dp = [0 for i in range(n)]
    
        maximum = -sys.maxsize - 1
        # iterate for all element
        index = -1
        for i in range(n):
            
            # if a[i]-1 is present before
            # i-th index
            if ((a[i] - 1 ) in mp):
                
                # last index of a[i]-1
                lastIndex = mp[a[i] - 1] - 1
    
                # relation
                dp[i] = 1 + dp[lastIndex]
            else:
                dp[i] = 1
    
            # stores the index as 1-index as we
            # need to check for occurrence, hence
            # 0-th index will not be possible to check
            mp[a[i]] = i + 1
    
            # stores the longest length 
            if (maximum < dp[i]):
                maximum = dp[i]
                index = i
        # We know last element of sequence is
        # a[index]. We also know that length
        # of subsequence is "maximum". So We
        # print these many consecutive elements
        # starting from "a[index] - maximum + 1"
        # to a[index].
        sequence=[]
        for curr in range(a[index] - maximum + 1,a[index] + 1, 1):
            sequence.append(curr)
            print(curr, end = " ")
        return sequence

    def is_straight_still_need_one_card(self,cards):
        ranks=[card['face'] for card in cards]
        ranks=list(set(sorted(ranks)))
        if 1 in ranks:
            ranks.append(14)
        for card_rank in range(len(ranks)-3):
            if (ranks[card_rank+1]-ranks[card_rank]==1) and (ranks[card_rank+3]-ranks[card_rank+2]==1) and (ranks[card_rank+2]-ranks[card_rank+1]==2):
                return True
        return False

