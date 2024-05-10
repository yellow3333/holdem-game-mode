# Written by Tyler Fisher, 20 Feb 2017. For sample boards, see https://goo.gl/19jGRx
# Note: input must be given in the precise format described (there's no error-checking)

class HandComparator():
    def __init__(self):
        self.ranks = ["just a high card","one pair","two pair","trips","a straight","a flush","a boat","quads","a straight flush"]
        self.r = ["highCard", "pair-", "2pair-", "trips-", "straight", "flush", "boat", "quads-", "straightFlush"]

    def firstHandIsBetter(self, h1, h2): # given two hands, with the 5 cards + rank + relevant kicker details, say which wins
        if h1[5] != h2[5]: return h1[5] > h2[5] # different ranks
        if h1[5]==8 or h1[5]==4: return h1[2] > h2[2] if h1[2] != h2[2] else None # SF or straight: check middle card
        if h1[5]==5 or h1[5]==0: # flush or high card: check all five cards
            for wooper in range(5):
                if h1[4 - wooper] != h2[4 - wooper]: return h1[4 - wooper] > h2[4 - wooper]
            return None # chop
        for scromp in range(6,10):
            if h1[scromp] != h2[scromp]: return h1[scromp] > h2[scromp] # one is higher, so that one wins
            if len(h1) == scromp+1: return None # all were the same, so it's a chop

    def getBestFrom7(self, sevenCards, sevenSuits): # given 7 cards, call the 5-card comparator on each of the 21 poss. combos
        bestHand = None
        for i in range(7):
            for j in range(i+1, 7):
                s = []
                for k in range(7):
                    if k != i and k != j: s.extend([sevenCards[k], sevenSuits[k]])
                newHand = self.getHandRankFromFiveCards(sorted([s[0],s[2],s[4],s[6],s[8]]), [s[1],s[3],s[5],s[7],s[9]])
                if bestHand is None or self.firstHandIsBetter(newHand, bestHand): bestHand = newHand
        return bestHand

    def getHandRankFromFiveCards(self, fC, fS): # given 5 cards, determine what the rank of the hand is and add kicker info to it
        if fS.count(fS[0])==len(fS): fC.append(8) if ((fC[0]==fC[1]-1==fC[2]-2==fC[3]-3) and (fC[4]-1==fC[3] or fC[4]-12==fC[0])) else fC.append(5)
        elif ((fC[0] == fC[1]-1 == fC[2]-2 == fC[3]-3) and (fC[4]-1 == fC[3] or fC[4]-12 == fC[0])): fC.append(4) # straight
        elif fC[1]==fC[2]==fC[3] and (fC[0]==fC[1] or fC[3]==fC[4]): fC.extend([7, fC[0], fC[4]]) if fC[0]==fC[1] else fC.extend([7, fC[4], fC[0]]) # quads
        elif fC[0]==fC[1]==fC[2] and fC[3]==fC[4]: fC.extend([6, fC[0], fC[4]]) # boat, high set full of low pair
        elif fC[0] == fC[1] and fC[2] == fC[3] == fC[4]: fC.extend([6, fC[4], fC[0]]) # boat, low set full of high pair
        elif fC[0]==fC[1]==fC[2]: fC.extend([3, fC[0], fC[4], fC[3]]) # trips, both kickers higher; other kicker-types of trips in next line
        elif fC[2]==fC[3] and (fC[1]==fC[2] or fC[3]==fC[4]): fC.extend([3, fC[1], fC[4], fC[0]]) if fC[1]==fC[2] else fC.extend([3, fC[2], fC[1], fC[0]])
        elif (fC[0]==fC[1] and (fC[2]==fC[3] or fC[3]==fC[4])) or (fC[1]==fC[2] and fC[3]==fC[4]): # two pair
            if fC[0]==fC[1] and fC[2]==fC[3]: fC.extend([2, fC[3], fC[1], fC[4]]) # kicker higher than both pairs
            else: fC.extend([2, fC[4], fC[1], fC[2]]) if fC[0]==fC[1] and fC[3]==fC[4] else fC.extend([2,fC[4],fC[1],fC[0]])
        elif fC[0]==fC[1] or fC[1]==fC[2]: fC.extend([1, fC[0], fC[4], fC[3], fC[2]]) if fC[0]==fC[1] else fC.extend([1, fC[1], fC[4], fC[3], fC[0]])
        elif fC[2]==fC[3] or fC[3]==fC[4]: fC.extend([1, fC[2], fC[4], fC[1], fC[0]]) if fC[2]==fC[3] else fC.extend([1, fC[3], fC[2], fC[1], fC[0]])
        return fC if len(fC) > 5 else fC + [0] # return hand, but first if we haven't appended anything else note that it's just a high card hand

    def getBestHandOverall(self, allTheHands): # given a list containing a variable number of hands, return the index of the winner
        best = 0
        choppers = []
        for counter in range(1, len(allTheHands)):
            firstPlayerWins = self.firstHandIsBetter(allTheHands[counter], allTheHands[best])
            if firstPlayerWins:
                best = counter
                choppers = []
            if firstPlayerWins is None: choppers.append(counter)
        return (best, choppers)

    def translate_and_compare(self, board, hands):
        board_translated = ''
        hands_translated = []
        for card in board:
            board_translated += self._translate(card)
        for hand in hands:
            hand_translated = ''
            for card in hand:
                hand_translated += self._translate(card)
            hands_translated.append(hand_translated)
        return self._compare(board_translated, hands_translated)

    # translates card into native notation
    def _translate(self, card):
        res = ''
        if card['face'] <= 9:
            res += str(card['face'])
        elif card['face'] == 10:
            res += 'T'
        elif card['face'] == 11:
            res += 'J'
        elif card['face'] == 12:
            res += 'Q'
        elif card['face'] == 13:
            res += 'K'
        elif card['face'] == 14:
            res += 'A'
        
        if card['suite'] == 'club':
            res += 'c'
        elif card['suite'] == 'diamond':
            res += 'd'
        elif card['suite'] == 'heart':
            res += 'h'
        elif card['suite'] == 'spade':
            res += 's'

        return res

    def _compare(self, board, hands):
        print('compare broad,hands: ',board,hands)
        cards = ''
        cards += board
        for hand in hands:
            cards += ' '
            cards += hand
        lenCards = len(cards)

        cards = cards.replace("T", ":").replace("J", ";").replace("Q", "<").replace("K", "=").replace("A", ">")
        listOfCards = (",".join(str(ord(card)) for card in cards)).split(',')
        c = [ int(item) for item in listOfCards ]

        allHands = []
        x = 10
        while x < lenCards:
            print('lenCards',lenCards,'compare:',[c[0], c[2], c[4], c[6], c[8], c[x+1], c[x+3]], [c[1], c[3], c[5], c[7], c[9], c[x+2], c[x+4]])
            allHands.append(self.getBestFrom7([c[0], c[2], c[4], c[6], c[8], c[x+1], c[x+3]], [c[1], c[3], c[5], c[7], c[9], c[x+2], c[x+4]] ))
            x += 5

        winnerInfo = self.getBestHandOverall(allHands) # now that we have all the hands, figure out whose is best
        winner = winnerInfo[0]
        print('winner',winner)
        choppers = winnerInfo[1]
        print('winner info',winnerInfo)
        if len(choppers) > 0:
            chopNums = [chopper+1 for chopper in choppers]
            print("The following players chop: " + str(winner+1) + ", " + ", ".join(str(x) for x in chopNums) + " (all have " + self.ranks[allHands[winner][5]] + ")")
        else: print('Player %s wins, with ' % str(winner+1) + self.ranks[allHands[winner][5]])

        for i in range(len(allHands)):
            pH = allHands[i]
            for poop in range(len(pH)): pH[poop] -= 48 if poop != 5 else -51
            print(' Player %s\'s best hand: ' % str(i+1) + " ".join(str(x) for x in pH).replace("10","T").replace("11","J").replace("12","Q").replace("13","K").replace("14","A").replace("51",self.r[0]).replace("52 ",self.r[1]).replace("53",self.r[2]).replace("54",self.r[3]).replace("55",self.r[4]).replace("56",self.r[5]).replace("57",self.r[6]).replace("58",self.r[7]).replace("59",self.r[8]))

        return winnerInfo

#test_obj = HandComparator()
#print(test_obj._compare('5c6dTh4dJd', ['KhQh', 'KhQh']))
