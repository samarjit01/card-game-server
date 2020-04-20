from flask import Flask, jsonify
from flask import abort , make_response , request
import json , ast
import random
from flask_cors import CORS


app = Flask(__name__)
CORS(app)




Games = [
    {
        'id': 1,
        'isActive':False,
        'playerName': ['samar','vikas','sagar','neil'],
        'playerId':{'p1':0,'p2':1,'p3':2,'p4':3},
        'playerActive': [False , False , False , False],
        'playerCardPassed' : [False , False , False , False],
        'gamePlayed' : 0,
        'gameState':{
            'round':0,
            'cards':{
                'p1':[],
                'p2':[],
                'p3':[],
                'p4':[]
            },
            'gameScores':[0,0,0,0],
            'onTableCards':[],
            'suit':'HEART',
            'turn':'p1',
            'isCardPassed':False,
            'cardPassed':{
                'p1':[],
                'p2':[],
                'p3':[],
                'p4':[],

            },
            'cardPassDir':'SELF',
            'gamePlayDir':'RIGHT',
            'state':'NOTSTARTED'
        }
    }
]

Players = [
    {
        'game_id':1,
        'player_id':'p1',
        'username':'samar',
        'password':'samar',
    },
    {
        'game_id':1,
        'player_id':'p2',
        'username':'vikas',
        'password':'vikas',
    },
    {
        'game_id':1,
        'player_id':'p3',
        'username':'sagar',
        'password':'sagar',
    },
    {
        'game_id':1,
        'player_id':'p4',
        'username':'neil',
        'password':'neil',
    }
]

Logs = {
    '1' : {
        'msg':[]
    }
}

def getGame(game_id):
    game = [game for game in Games if game['id'] == game_id]
    if len(game) == 0:
        abort(404)
    return game[0]

def getPlayer(game_id , player_id):
    player = [player for  player in Players
                 if (player['game_id'] == game_id and player['player_id'] == player_id)]
    if(len(player) == 0):
        abort(404)

    player = player[0]
    return player



def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def isValidCard(passedcards , cards):
    cardPresent = [i for i in passedcards if i in cards]
    return len(passedcards) == len(cardPresent)

def isValidPass(passedcards , cards):
    if(len(passedcards) == 6 and isValidCard) :
        return True
    return False

def distributeCards():
    cards = [i+1 for i in range(52)]
    random.shuffle(cards)
    return list(chunks(cards,13))

def getNeighbours(passDir):
    if(passDir == 'LEFT'):
        neighbours=  {
            'p1':'p4',
            'p2':'p1',
            'p3':'p2',
            'p4':'p1'
        }
        return neighbours
    elif(passDir == 'RIGHT'):
        neighbours =  {
            'p1':'p2',
            'p2':'p3',
            'p3':'p4',
            'p4':'p1'
        }
        return neighbours
    elif(passDir == 'FRONT'):
        neighbours = {
            'p1':'p3',
            'p2':'p4',
            'p3':'p1',
            'p4':'p2'
        }
        return neighbours
    else:
        neighbours = {
            'p1':'p1',
            'p2':'p2',
            'p3':'p3',
            'p4':'p4'
        }
        return neighbours


def getNextTurn(turn , orientation):
    neighbours = getNeighbours(orientation)
    return neighbours[turn]



def passCards(cards , cardsPassed , neighbours):
    p1 = cards['p1']
    p2 = cards['p2']
    p3 = cards['p3']
    p4 = cards['p4']

    c1 = cardsPassed['p1']
    c2 = cardsPassed['p2']
    c3 = cardsPassed['p3']
    c4 = cardsPassed['p4']

    p1 = [e for e in p1 if e not in c1]
    p2 = [e for e in p2 if e not in c2]
    p3 = [e for e in p3 if e not in c3]
    p4 = [e for e in p4 if e not in c4]


    p1.extend(cardsPassed[neighbours['p1']])
    p2.extend(cardsPassed[neighbours['p2']])
    p3.extend(cardsPassed[neighbours['p3']])
    p4.extend(cardsPassed[neighbours['p4']])

    cards = {
        'p1':p1,
        'p2':p2,
        'p3':p3,
        'p4':p4
    }
    return cards


def startGame(game_id):
    game = getGame(game_id)
    activePlayerCount = 0
    for player in game['playerActive']:
        if(player == True):
            activePlayerCount += 1
    if(activePlayerCount == 4):
        cards = distributeCards()
        game['isActive'] = True
        game['gameState']['cards']['p1'] = cards[0]
        game['gameState']['cards']['p2'] = cards[1]
        game['gameState']['cards']['p3'] = cards[2]
        game['gameState']['cards']['p4'] = cards[3]
        game['gameState']['state'] = "NOTPASSED"
        msg = 'Game Started '
        Logs[str(game_id)]['msg'].append(msg)

    else:
        print("4 players required")


def startPlayingGame(game_id):
    game = getGame(game_id)
    passedPlayerCount = 0

    for player in game['playerCardPassed']:
        if(player == True):
            passedPlayerCount += 1
    if(passedPlayerCount == 4):
        game['gameState']['state'] = "STARTED"
        game['gameState']['isCardPassed'] = True
        cards = game['gameState']['cards']
        cardPassed = game['gameState']['cardPassed']
        orientation =  game['gameState']['cardPassDir']
        neighbours = getNeighbours(orientation)

        game['gameState']['cards'] = passCards(cards , cardPassed , neighbours)
        msg = 'All players get Passed Cards'

        Logs[str(game_id)]['msg'].append(msg)


def getLog(game_id):
    msg = Logs[str(game_id)]['msg']
    return msg


@app.route('/logs/<int:game_id>', methods=['GET'])
def getLogs(game_id):
    if request.method == 'GET' :
        game = getGame(game_id)
        if len(game) == 0:
            return jsonify({'Message': 'No Such Game'})
        logs = getLog(game_id)
        print(logs)
        return jsonify({'Logs': logs})



@app.route('/<int:game_id>', methods=['GET','POST','PUT'])
def gameOps(game_id):
    if request.method == 'GET' :
        game = getGame(game_id)
        if len(game) == 0:
            return jsonify({'Message': 'No Such Game'})
        return jsonify({'game': game})

    if  request.method == 'PUT':
        idx = [idx for idx, game in enumerate(Games) if game['id'] == game_id]
        if(len(idx) == 0):
            return jsonify({'Message': 'No Such Game'})
        idx = idx[0]
        request_body = request.json
        Games[idx] = request_body['game']
        return jsonify({'isSuccessful': True})



@app.route('/<int:game_id>/<string:player_id>', methods=['GET','POST','PUT'])
def addPlayers(game_id , player_id):

    if  request.method == 'POST':
        request_body = request.json
        player = getPlayer(game_id , player_id)
        if(len(player) == 0):
            return jsonify({'Message': 'No such Player'})

        if(player['password'] ==  request_body['password']):
             player['username'] = request_body['username']
             game = getGame(game_id)
             idx = game['playerId'][player['player_id']]
             game['playerActive'][idx] = True
             game['playerName'][idx] = request_body['username']
             msg = player['username'] + ' joined the Game '
             Logs[str(game_id)]['msg'].append(msg)
             startGame(game_id)


        return jsonify({'isSuccessful': True})

def getSuit(card):
    if(card >= 0 and card <= 12):
        return 'HEART'
    elif(card >=13 and card <= 25):
        return 'CLUB'
    elif(card >= 26 and card <= 38):
        return 'DIAMOND'
    else:
        return 'SPADE'

def isPlayerHaveSuit(cards , suit):
    for card in cards:
        if(getSuit(cards) == suit):
            return True
    return False

def isValidMove(card , playerTurn , game , playerId):
    playerCards = game['gameState']['cards'][playerId]
    onTable = game['gameState']['onTableCards']
    playerSuit = getSuit(card)
    suit = game['gameState']['suit']

    if(game['gameState']['turn'] != playerTurn):
        return False
    if(card not in playerCards):
        return False
    if(len(onTable) == 0):
        game['gameState']['suit'] = playerSuit
        return True

    if(len(onTable) >= 1):
        if(isPlayerHaveSuit(playerCards , suit) == False):
            return True
        return playerSuit == suit


def getBoardPoints(cards):
    point = 0
    for i in cards :
        if(i==51):
            point += 12
        else:
            point += 1
    return point


def getScores(gameScores , onTableCards , suit):
    valuedCards = []
    for i in onTableCards:
        if getSuit(i) == suit:
            valuedCards.append(i)
        else:
            valuedCards.append(-1)

    pointCards = [i for i in onTableCards if (getSuit(i) == 'HEART' or i == 50)]
    pointsOnBoard = getBoardPoints(pointCards)
    idx = valuedCards.index(max(valuedCards))
    cardTaker = 'p' + str(idx+1)
    for i in range(len(gameScores)):
        if i == idx:
            gameScores[i] += pointsOnBoard
    return cardTaker , gameScores


@app.route('/playerCard/<int:game_id>/<string:player_id>', methods=['GET'])
def getPlayerCards():
    player = getPlayer(game_id , player_id)
    game = getGame(game_id)
    playerCards =  game['gameState']['cards'][player_id]
    return jsonify({'playerCards': playerCards})

@app.route('/onTableCard/<int:game_id>/<string:player_id>', methods=['GET'])
def getOnTableCards():
    player = getPlayer(game_id , player_id)
    game = getGame(game_id)
    onTableCards = game['gameState']['onTableCards']
    return jsonify({'onTableCards': onTableCards})

@app.route('/turn/<int:game_id>/<string:player_id>', methods=['GET'])
def getTurn():
    player = getPlayer(game_id , player_id)
    game = getGame(game_id)
    turn = game['gameState']['turn']
    return jsonify({'turn': turn})





@app.route('/play/<int:game_id>/<string:player_id>', methods=['GET','POST','PUT'])
def playGame(game_id , player_id):

    if  request.method == 'POST':
        player = getPlayer(game_id , player_id)
        game = getGame(game_id)
        onTableCards = game['gameState']['onTableCards']
        gameScores = game['gameState']['gameScores']
        playerCards =  game['gameState']['cards'][player_id]
        request_body = request.json
        cards = request_body['cards']
        startNewGame = request_body['startNewGame']
        playerTurn = player_id
        orientation = game['gameState']['gamePlayDir']

        suit = game['gameState']['suit']

        round = game['gameState']['round']


        if(game['gameState']['state'] == 'NOTPASSED'):
            if(isValidPass(cards ,playerCards) == False):
                return jsonify({'Message': 'Not Valid Pass'})
            game['gameState']['cardPassed'][player_id] = cards
            idx = game['playerId'][player['player_id']]
            game['playerCardPassed'][idx]  = True
            msg =  player['username'] + ' Selected Cards to Pass '

            Logs[str(game_id)]['msg'].append(msg)
            startPlayingGame(game_id)

        elif(game['gameState']['state'] == 'STARTED'):

            if(isValidCard(cards ,playerCards) == False):
                return jsonify({'Message': 'Card Not Present in Players Hand'})

            if(len(cards) == 1):
                card = cards[0]
                if(isValidMove(card,playerTurn,game,player_id)):

                    playerCards.remove(card)
                    onTableCards.append(card)
                    game['gameState']['turn'] = getNextTurn(playerTurn,orientation)
                    game['gameState']['onTableCards'] = onTableCards
                    game['gameState']['cards'][player_id] = playerCards
                    msg = player['username'] + ' Played Card '

                    Logs[str(game_id)]['msg'].append(msg)


                    if(len(onTableCards) == 4):
                        round += 1
                        cardTaker , scores = getScores(gameScores , onTableCards , suit)
                        game['gameState']['onTableCards'] = []
                        game['gameState']['gameScores'] = scores
                        game['gameState']['round'] = round
                        game['gameState']['turn'] = cardTaker

                        msg =  'Round ' + str(round) + ' Finished '

                        Logs[str(game_id)]['msg'].append(msg)

                        if(round == 13):
                            game['gameState']['state'] = 'FINISHED'
                            game['playerCardPassed'] = [False , False , False , False]
                            game['gameState']['cards']['p1'] = []
                            game['gameState']['cards']['p2'] = []
                            game['gameState']['cards']['p3'] = []
                            game['gameState']['cards']['p4'] = []

                            game['gameState']['cardPassed']['p1'] = []
                            game['gameState']['cardPassed']['p2'] = []
                            game['gameState']['cardPassed']['p3'] = []
                            game['gameState']['cardPassed']['p4'] = []

                            game['gameState']['isCardPassed'] = False

                            game['gameState']['cardPassDir'] = getNextCardPassDir(game['gameState']['cardPassDir'])
                            game['gamePlayed'] = game['gamePlayed'] + 1
                            msg = 'Game ' + str(game['gamePlayed'])+' is Finished '
                            Logs[str(game_id)]['msg'].append(msg)

        elif(game['gameState']['state'] == 'FINISHED'):
            return jsonify({'msg': 'Game finished'})

        return jsonify({'isSuccessful': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def getNextCardPassDir(Direction):
    print("hullaa")
    if(Direction == 'LEFT'):
        return 'FRONT'
    if(Direction == 'RIGHT'):
        return 'LEFT'
    if(Direction == 'FRONT'):
        return 'SELF'
    if(Direction == 'SELF'):
        return 'RIGHT'
