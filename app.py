import time
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from collections import OrderedDict
from domain.hand_game.entities.hand_game import *
from domain.hand_game.entities.player import *
from officialAI.ai_model import *
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')  

current_table = {}
playing_games = {}
playing_ais = {}



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('logging', 'hello world')


@socketio.on('message')
def handle_message():
    print('handle_message called')
    emit('logging', 'hello world')

@socketio.on('newTable')
def handle_newTable(msg):
    print('newTable')
    msg_dict = json.loads(msg)
    # create new players
    player_cnt = int(msg_dict['playerCnt'])
    print('player_cnt = ' + str(player_cnt))
    new_players = create_newTable_players(player_cnt).copy()
    

    for i in range(2, player_cnt + 1):
        playing_ais[i] = TexasAI(i)
        
    
    current_table['players'] = new_players.copy()
    current_table['order'] = list(new_players.keys())
    
    print('order = ')
    print(current_table['order'])
    print_table(current_table)
    response = {}
    response['order'] = current_table['order'].copy()
    emit('newTableResponse', json.dumps(response))

def create_newTable_players(player_cnt):
    new_players = OrderedDict()
    for i in range(2, player_cnt + 1):
        new_player = Player(i, str(i), True, 1000)
        new_players[i] = new_player
    new_player = Player(1, '1', False, 1000)
    new_players[1] = new_player
    
    return new_players

@socketio.on('newGame')
def handle_newGame():
    print('in handle_newGame')
    current_table['order'].append(current_table['order'].pop(0))
    new_players = OrderedDict()
    for player_id in current_table['order']:
        new_players[player_id] = current_table['players'][player_id]
    new_game(new_players)
    
    
    


def new_game(players):
    print('in new_game')
    new_players = players.copy()
    for player_id in players:
        print('player_id = ' + str(player_id))
        print('remaining_chips = ' + str(players[player_id].remaining_chips))
    with open('db.json') as f:
        db = json.load(f)
    
    # notify ai models
    for player_id in players:
        if players[player_id].is_ai:
            start_chip = new_players[player_id].remaining_chips
            position = current_table['order'].index(player_id)
            playing_ais[player_id].new_game(len(players), start_chip, 20, 10, position)


    new_game = Hand_game(new_players, 10, 20)
    print(str(new_game))
    playing_games[db['cur_id']] = new_game
    print('newGame button is pressed')
    response = {}
    response['game_id'] = db['cur_id']
    opponent_ids = []
    for player_id in players:
        if players[player_id].is_ai:
            opponent_ids.append(player_id)
        else:
            response['player_id'] = player_id
    response['opponent_ids'] = opponent_ids
    response['order'] = list(players.keys())
    print('response order = ')
    print(list(players.keys()))
    emit('logging', 'hand_game id = ' + str(db['cur_id']))
    emit('newGameResponse', json.dumps(response))
    notify_ai_hand(new_game)#
    pot_msg = {}
    pot_msg['pot'] = new_game.pot
    emit('rcvPot', json.dumps(pot_msg))
    notify_player_status(new_game)
    db['cur_id'] += 1
    new_game_sb_bb(new_game, db['cur_id']-1)
    notify_player_status(new_game)
    with open('db.json', 'w') as f:
        f.write(json.dumps(db, indent=4))
    next_player = new_game.get_current_player()
    if next_player.is_ai:
        game_over = handle_all_ai_actions(db['cur_id']-1, 1)
        if not game_over:
            prompt_player_action(db['cur_id']-1, 1)
    else:
        prompt_player_action(db['cur_id']-1, 1)

    

def new_game_sb_bb(game_obj, game_id):
    # 0th bets sb
    next_player = game_obj.cur_round.get_current_player()
    action = {'action': 'raise', 'amount': game_obj.sb}
    action_taken = game_obj.take_action(next_player.id, action)
    notify_action(game_id, action_taken, next_player.id)

    # 1st bets bb
    next_player = game_obj.cur_round.get_current_player()
    action = {'action': 'raise', 'amount': game_obj.bb}
    action_taken = game_obj.take_action(next_player.id, action)
    notify_action(game_id, action_taken, next_player.id)

# Gets the hand of a player
# {"game_id": "id", "player_id": "id"}
@socketio.on('getPlayerHand')
def handle_getPlayerHand(msg):
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    player_id = int(msg_dict['player_id'])
    game = playing_games[game_id]
    player = game.get_player(player_id)
    hand = player.current_hand
    res = {
        'isCard': True,
        'card':
            [{'hand': hand, 'player_id': player_id}]
    }
    emit('rcvPlayerHand', json.dumps(res))

# Gets the hands of opponent players
# {"game_id": "id", "player_id": "id"}
@socketio.on('getOpponentPlayerHand')
def handle_getOpponentPlayerHand(msg):
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    player_id = int(msg_dict['player_id'])
    game = playing_games[game_id]
    res = {
        'isCard': False,
        'card':[]
    }
    if not game.game_over:
        emit('rcvPlayerHand', json.dumps(res))
        return
    
    res['isCard'] = True
    for p_id in game.players:
        player = game.players[p_id]
        if player.id != player_id:
            hand = player.current_hand
            res['card'].append({'hand': hand, 'player_id': player_id})
    emit('rcvPlayerHand', json.dumps(res))

def send_all_player_hand(game_obj):
    res = {
        'isCard': True,
        'card':[]
    }
    for p_id in game_obj.players:
        hand = game_obj.players[p_id].current_hand
        print('app.py players', game_obj.players)
        res['card'].append({'hand': hand, 'player_id': p_id})
    emit('rcvPlayerHand', json.dumps(res))

# Get Flop
# {"game_id": "id"}
@socketio.on('getFlopCard')
def handle_getFlopCard(msg):
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    game = playing_games[game_id]
    if game.cur_round_cnt >= 1:
        flop_cards = game.flop
        is_card = True 
    else:
        flop_cards = None
        is_card = False
    msg = {"isCard": is_card, "card": flop_cards}
    emit('rcvFlopCard', json.dumps(msg))

# sends flop card to player
def sendFlopCard(game_obj):
    msg = {"isCard": True, "card": game_obj.flop}
    emit('rcvFlopCard', json.dumps(msg))

# Get Turn
# {"game_id": "id"}
@socketio.on('getTurnCard')
def handle_getTurnCard(msg):
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    game = playing_games[game_id]
    if game.cur_round_cnt >= 2:
        turn_cards = game.turn
        is_card = True
    else:
        turn_cards = None
        is_card = False
    msg = {"isCard": is_card, "card": turn_cards}
    emit('rcvTurnCard', json.dumps(msg))

# sends turn card to player
def sendTurnCard(game_obj):
    msg = {"isCard": True, "card": game_obj.turn}
    emit('rcvTurnCard', json.dumps(msg))

# Get Turn
# {"game_id": "id"}
@socketio.on('getRiverCard')
def handle_getRiverCard(msg):
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    game = playing_games[game_id]
    if game.cur_round_cnt >= 3:
        river_cards = game.river
        is_card = True
    else:
        river_cards = None
        is_card = False
    msg = {"isCard": is_card, "card": river_cards}
    emit('rcvRiverCard', json.dumps(msg))

# sends river card to player
def sendRiverCard(game_obj):
    msg = {"isCard": True, "card": game_obj.river}
    emit('rcvRiverCard', json.dumps(msg))

@socketio.on('check')
def handle_check(msg):
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    player_id = int(msg_dict['player_id'])
    action = msg_dict['action']
    action['amount'] = int(action['amount'])
    print('check button is pressed')
    emit('logging', 'check request ack')
    advance_hand_game_by_human(game_id, player_id, action)
    print('finished advance_hand_game_by_human')


@socketio.on('raise')
def handle_raise(msg):
    print('raise button is pressed')
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    player_id = int(msg_dict['player_id'])
    action = msg_dict['action']
    action['amount'] = int(action['amount'])
    print('action')
    print(action)
    emit('logging', 'raise request ack')
    advance_hand_game_by_human(game_id, player_id, action)
    print('finished advance_hand_game_by_human')


@socketio.on('fold')
def handle_fold(msg):
    print('fold button is pressed')
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    player_id = int(msg_dict['player_id'])
    action = msg_dict['action']
    action['amount'] = int(action['amount'])
    print('action')
    print(action)
    emit('logging', 'fold request ack')
    advance_hand_game_by_human(game_id, player_id, action)
    print('finished advance_hand_game_by_human')

#@socketio.on('allIn')#
#def handle_allIn(msg):
    #print('allIn button is pressed')
    #msg_dict = json.loads(msg)
    #game_id = int(msg_dict['game_id'])
    #player_id = int(msg_dict['player_id'])
    #action = msg_dict['action']
    #action['amount']= int(action['amount'])
    #print('action')
    #print(action)
    #emit('logging', 'allIn request ack')
    #advance_hand_game_by_human(game_id, player_id, action)
    #print('finished advance_hand_game_by_human')

@socketio.on('call')
def handle_call(msg):
    print('call button is pressed')
    msg_dict = json.loads(msg)
    game_id = int(msg_dict['game_id'])
    player_id = int(msg_dict['player_id'])
    action = msg_dict['action']
    action['amount'] = int(action['amount'])
    print('action')
    print(action)
    emit('logging', 'call request ack')
    advance_hand_game_by_human(game_id, player_id, action)
    print('finished advance_hand_game_by_human')


# handles action from human
def advance_hand_game_by_human(game_id, player_id, action):
    game_obj = playing_games[game_id]
    action_taken = game_obj.take_action(player_id, action)
    notify_action(game_id, action_taken, player_id)
    notify_player_status(game_obj)
    game_over = handle_all_ai_actions(game_id, player_id)
    if game_over:
        cleanup(game_obj)
    else:
        prompt_player_action(game_id, player_id)
        notify_status(game_obj)
    
# handles all actions of ai
def handle_all_ai_actions(game_id, human_player_id):
    print('in handle_al_ai_actions')
    game_obj = playing_games[game_id]
    next_player = game_obj.get_current_player()
    #print("current cnt ",game_obj.cur_round_cnt)
    while (next_player.id != human_player_id) and not game_obj.game_over:
        print('this next_player.id = ' + str(next_player.id))
        # require ai to take action
        action = playing_ais[next_player.id].action()
        print("action in app: ",action)
        # take action to hand_game
        action_taken = game_obj.take_action(next_player.id, action)
        print('ai action_take:')
        print(action_taken)
        # notify others
        notify_action(game_id, action_taken, next_player.id)
        notify_status(game_obj)
        next_player = game_obj.get_current_player()
    return game_obj.game_over

def notify_action(game_id, action, action_taker_id):
    game = playing_games[game_id]
    print('in notify_action')
    print(game.cur_round.remaining_players_ids)
    for player_id in game.players:
        if player_id not in game.cur_round.remaining_players_ids:
            to_call = -1
        else:
            to_call = game.cur_round.to_call(player_id)
        if game.players[player_id].is_ai:
            notify_ai_action(player_id, action, action_taker_id, to_call)
        else:
            notify_player_action(player_id, action, action_taker_id, to_call)



# notifies the human users
# {'playerId': int, 'actionTakerId': int, 
#   'action': action, 'toCall': int}
def notify_player_action(player_id, action, action_taker_id, to_call):
    msg = {
        'playerId': player_id,
        'actionTakerId': action_taker_id,
        'action': action,
        'toCall': to_call
    }
    emit('notifyPlayerAction', json.dumps(msg))

# notifies the ai players
def notify_ai_action(player_id, action, action_taker_id, to_call):
    playing_ais[player_id].observe_action(action_taker_id, action, to_call)

# notify all the status of the players
# remaining_chips, pot_size
def notify_status(game_obj):
    print('in notify_status')
    notify_player_status(game_obj)
    notify_player_board(game_obj)
    notify_ai_player_board(game_obj)
    notify_ai_player_chips(game_obj)

def notify_ai_hand(game_obj):
    for player_id in game_obj.players:
        if game_obj.players[player_id].is_ai and game_obj.players[player_id].current_hand!=None:
            playing_ais[player_id].observe_hand(game_obj.players[player_id].current_hand)
           
def notify_ai_player_chips(game_obj):
    for player_id in game_obj.players:
        if not game_obj.players[player_id].is_ai:
            continue
        print("chips:",game_obj.players[player_id].remaining_chips)
        playing_ais[player_id].observe_remaining_chips(game_obj.players[player_id].remaining_chips)

def notify_ai_player_board(game_obj):
    for player_id in game_obj.players:
        if not game_obj.players[player_id].is_ai:
            continue
        if game_obj.cur_round_cnt >= 1:
            playing_ais[player_id].observe_board(game_obj.cur_round_cnt, game_obj.flop)
        if game_obj.cur_round_cnt >= 2:
            playing_ais[player_id].observe_board(game_obj.cur_round_cnt, game_obj.turn)
        if game_obj.cur_round_cnt >= 3:
            playing_ais[player_id].observe_board(game_obj.cur_round_cnt, game_obj.river)


def notify_player_status(game_obj):
    print('in notify_player_status')
    pot_size = game_obj.pot
    remaining_chips = []
    for player_id in game_obj.players:
        remaining_chips.append({
            'playerId': player_id,
            'remainingChips': game_obj.players[player_id].remaining_chips
        })

    msg = {
        'pot': pot_size,
        'remainingChips':remaining_chips
    }
    print(json.dumps(msg))
    emit('notifyPlayerStatus', json.dumps(msg))

def notify_player_board(game_obj):
    if game_obj.cur_round_cnt >= 1:
        sendFlopCard(game_obj)
    if game_obj.cur_round_cnt >= 2:
        sendTurnCard(game_obj)
    if game_obj.cur_round_cnt >= 3:
        sendRiverCard(game_obj)
    if game_obj.game_over:
        send_all_player_hand(game_obj)
        
        

def prompt_player_action(game_id, player_id):
    print('in prompt_player_action')
    print('game_id = ' + str(game_id))
    print('player_id = ' + str(player_id))
    msg = {'myMove': True}
    emit('promptMyMove', json.dumps(msg))

def notify_ai_endgame(game_obj, endgame_info):
    winners = []
    prizes = []
    hands = []
    for i in endgame_info:
        winners.append(i[0])
        prizes.append(i[1])
    for player_id in game_obj.players:
        hands.append(game_obj.players[player_id].current_hand)

    for player_id in game_obj.players:
        if game_obj.players[player_id].is_ai:
            playing_ais[player_id].end_game(winners, prizes, hands)

# notify human player endgame
def notify_player_endgame(endgame_info):
    msg = {}
    msg['winner'] = []
    for i in endgame_info:
        msg['winner'].append(list(i))
    emit('rcvEndgameInfo', json.dumps(msg))

# cleanup a finished game
def cleanup(game_obj):
    # calculate winner and prize
    endgame_info = game_obj.cleanup()
    print('endgame_info=')
    print(endgame_info)
    # distribute prize to winner(s)
    for i in range(len(endgame_info)):
        player_id = endgame_info[i][0]
        game_obj.players[player_id].remaining_chips += endgame_info[i][1]
        print('game_obj.players[player_id],player_id',game_obj.players[player_id],player_id)
    for player_id in game_obj.players:
        current_table['players'][player_id] = game_obj.players[player_id]
    # move playing order
    print('order = ')
    print(current_table['order'])
    notify_player_status(game_obj)
    notify_ai_endgame(game_obj, endgame_info)
    notify_player_endgame(endgame_info)

# prints out the table info nicely
def print_table(table):
    res_str = ''
    res_str += '=================\n'
    res_str += ('order: ' + str(table['order']) + '\n')
    res_str += 'players:\n'

    for player_id in table['players']:
        res_str += str(table['players'][player_id])
    print(res_str)

if __name__ == '__main__':
    cur_id = 0
    socketio.run(app, host='127.0.0.1', port=5000, use_reloader=True, debug=True)
    

