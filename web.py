# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask import abort , make_response , request
import json , ast
import random
import copy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room ,send,leave_room


app = Flask(__name__)
CORS(app)
socket = SocketIO(app, cors_allowed_origins="*")


InitialStatusGame =  {
        "breBoys": [],
        "breCount": [
            0,
            0,
            0,
            0
        ],
        "doStartNewGame": [
            False,
            False,
            False,
            False
        ],
        "gamePlayed": 0,
        "gameState": {
            "cardPassDir": "RIGHT",
            "cardPassed": {
                "p1": [],
                "p2": [],
                "p3": [],
                "p4": []
            },
            "cardTaker": "p1",
            "cards": {
                "p1": [],
                "p2": [],
                "p3": [],
                "p4": []
            },
            "gamePlayDir": "RIGHT",
            "gameScores": [
                0,
                0,
                0,
                0
            ],
            "isCardPassed": False,
            "lastRoundCards": [
                0,
                0,
                0,
                0
            ],
            "onTableCards": [
                0,
                0,
                0,
                0
            ],
            "playerTableCards": {
                "p1": [
                    0,
                    0,
                    0,
                    0
                ],
                "p2": [
                    0,
                    0,
                    0,
                    0
                ],
                "p3": [
                    0,
                    0,
                    0,
                    0
                ],
                "p4": [
                    0,
                    0,
                    0,
                    0
                ]
            },
            "playerTableUsernames": {
                "p1": [
                    "player1",
                    "player2",
                    "player3",
                    "player4"
                ],
                "p2": [
                    "player2",
                    "player3",
                    "player4",
                    "player1"
                ],
                "p3": [
                    "player3",
                    "player4",
                    "player1",
                    "player2"
                ],
                "p4": [
                    "player4",
                    "player1",
                    "player2",
                    "player3"
                ]
            },
            "round": 0,
            "state": "NOTSTARTED",
            "suit": "HEART",
            "turn": "p1"
        },
        "id": 1,
        "isActive": False,
        "playerActive": [
            False,
            False,
            False,
            False
        ],
        "playerCardPassed": [
            False,
            False,
            False,
            False
        ],
        "playerId": {
            "p1": 0,
            "p2": 1,
            "p3": 2,
            "p4": 3
        },
        "playerName": [
            "player1",
            "player2",
            "player3",
            "player4"
        ]
    }



Games = [
    {
        'id': 1,
        'isActive':False,
        'playerName': ['player1','player2','player3','player4'],
        'playerId':{'p1':0,'p2':1,'p3':2,'p4':3},
        'playerActive': [False , False , False , False],
        'playerCardPassed' : [False , False , False , False],
        'doStartNewGame' : [False , False , False , False],
        'breCount' : [0,0,0,0],
        'gamePlayed' : 0,
        'breBoys':[],
        'gameState':{
            'round':0,
            'cardTaker':'p1',
            'playerTableCards':{
                'p1':[0,0,0,0],
                'p2':[0,0,0,0],
                'p3':[0,0,0,0],
                'p4':[0,0,0,0]
            },'playerTableUsernames':{
                'p1':[],
                'p2':[],
                'p3':[],
                'p4':[]
            },
            'cards':{
                'p1':[],
                'p2':[],
                'p3':[],
                'p4':[]
            },
            'gameScores':[0,0,0,0],
            'onTableCards':[0,0,0,0],
            'lastRoundCards' :[0,0,0,0],
            'suit':'HEART',
            'turn':'p1',
            'isCardPassed':False,
            'cardPassed':{
                'p1':[],
                'p2':[],
                'p3':[],
                'p4':[],

            },
            'cardPassDir':'RIGHT',
            'gamePlayDir':'RIGHT',
            'state':'NOTSTARTED'
        }
    }
]

Players = [
    {
        'game_id':1,
        'player_id':'p1',
        'username':'player1',
        'password':'1',
    },
    {
        'game_id':1,
        'player_id':'p2',
        'username':'player2',
        'password':'2',
    },
    {
        'game_id':1,
        'player_id':'p3',
        'username':'player3',
        'password':'3',
    },
    {
        'game_id':1,
        'player_id':'p4',
        'username':'player4',
        'password':'4',
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
    if(game['gameState']['state'] == 'NOTSTARTED' or game['gameState']['state'] == 'FINISHED'):
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

            game['gameState']['turn'] = 'p'+str(random.randint(1,4))
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


@app.route('/reset/<int:game_id>', methods=['GET'])
def gameReset(game_id):
    Games[0] = InitialStatusGame
    return jsonify({'isSuccessful': True})


@app.route('/restart/<int:game_id>', methods=['GET'])
def gameRestart(game_id):
    game = getGame(game_id)
    if len(game) == 0:
        return jsonify({'Message': 'No Such Game'})

    endOfRound(game)
    cards = distributeCards()

    game['gameState']['cards']['p1'] = cards[0]
    game['gameState']['cards']['p2'] = cards[1]
    game['gameState']['cards']['p3'] = cards[2]
    game['gameState']['cards']['p4'] = cards[3]
    game['gameState']['state'] = "NOTPASSED"
    msg = 'Game Restarted '
    Logs[str(game['id'])]['msg'].append(msg)
    game['doStartNewGame'] = [False , False , False , False]
    game['gameState']['gameScores'] = [0,0,0,0]
    game['gameState']['breCount'] = [0,0,0,0]

    return jsonify({'isSuccessful': True})


@app.route('/logs/<int:game_id>', methods=['GET'])
def getLogs(game_id):
    if request.method == 'GET' :
        game = getGame(game_id)
        if len(game) == 0:
            return jsonify({'Message': 'No Such Game'})
        logs = getLog(game_id)
        print(logs)
        return jsonify({'Logs': logs})


def endOfRound(game):
    if(game['gameState']['state'] != 'FINISHED') :
        game['gamePlayed'] = game['gamePlayed']
    else:
        game['gamePlayed'] = game['gamePlayed'] + 1

    game['gameState']['state'] = 'FINISHED'
    game['playerCardPassed'] = [False , False , False , False]
    game['gameState']['cards']['p1'] = []
    game['gameState']['cards']['p2'] = []
    game['gameState']['cards']['p3'] = []
    game['gameState']['cards']['p4'] = []
    game['gameState']['onTableCards'] = [0,0,0,0]
    game['gameState']['lastRoundCards'] = [0,0,0,0]

    game['gameState']['cardPassed']['p1'] = []
    game['gameState']['cardPassed']['p2'] = []
    game['gameState']['cardPassed']['p3'] = []
    game['gameState']['cardPassed']['p4'] = []

    if(len(game['breBoys']) > 0 ):
        game['gameState']['turn'] = game['breBoys'][len(game['breBoys'])-1]
    else:
        game['gameState']['turn'] = 'p'+str(random.randint(1,4))

    game['gameState']['isCardPassed'] = False

    game['gameState']['cardPassDir'] = getNextCardPassDir(game['gameState']['cardPassDir'])


    msg = 'Game ' + str(game['gamePlayed'])+' is Finished '
    Logs[str(game['id'])]['msg'].append(msg)

@app.route('/continue/<int:game_id>/<string:player_id>', methods=['GET','POST','PUT'])
def renewGame(game_id , player_id):
    if request.method == 'GET' :
        game = getGame(game_id)
    if len(game) == 0:
            return jsonify({'Message': 'No Such Game'})

    game['doStartNewGame'][game['playerId'][player_id]] = True
    doAllagree = [i for i in game['doStartNewGame'] if i == True ]
    if(len(doAllagree) != 4) :
        return jsonify({'game': game})
    else:
        endOfRound(game)
        cards = distributeCards()

        game['gameState']['cards']['p1'] = cards[0]
        game['gameState']['cards']['p2'] = cards[1]
        game['gameState']['cards']['p3'] = cards[2]
        game['gameState']['cards']['p4'] = cards[3]
        game['gameState']['state'] = "NOTPASSED"
        msg = 'Game Started '
        Logs[str(game['id'])]['msg'].append(msg)
        game['doStartNewGame'] = [False , False , False , False]
        return jsonify({'game': game})








@app.route('/<int:game_id>', methods=['GET','POST','PUT'])
def gameOps(game_id):
    if request.method == 'GET' :
        game = getGame(game_id)

        if len(game) == 0:
            return jsonify({'Message': 'No Such Game'})

        if(len(game['gameState']['playerTableUsernames']['p1']) == 0):
            tempUsernames = copy.copy(game['playerName'])
            game['gameState']['playerTableUsernames']['p1'] = getOnTableCards(tempUsernames,0)
            game['gameState']['playerTableUsernames']['p2'] = getOnTableCards(tempUsernames,1)
            game['gameState']['playerTableUsernames']['p3'] = getOnTableCards(tempUsernames,2)
            game['gameState']['playerTableUsernames']['p4'] = getOnTableCards(tempUsernames,3)

        return jsonify({'game': game})

    if  request.method == 'PUT':
        idx = [idx for idx, game in enumerate(Games) if game['id'] == game_id]
        if(len(idx) == 0):
            return jsonify({'Message': 'No Such Game'})
        idx = idx[0]
        request_body = request.json
        Games[idx] = request_body['game']
        return jsonify({'isSuccessful': True})


@app.route('/showPlayers/<int:game_id>', methods=['GET'])
def showPlayers(game_id):
    return jsonify({'Data': Players})

@app.route('/<int:game_id>/<string:player_id>', methods=['GET','POST','PUT'])
def addPlayers(game_id , player_id):

    if  request.method == 'POST':
        request_body = request.json



        player = getPlayer(game_id , player_id)
        game = getGame(game_id)
        idx = game['playerId'][player['player_id']]
        inputUserName = str(request_body['username'])
        player['username'] = inputUserName[0:8]

        if(game['playerActive'][idx] == True):
            if(player['password'] == request_body['password'] ):

                msg = player['username'] + ' changed name '
                Logs[str(game_id)]['msg'].append(msg)

                game['playerName'][idx] = inputUserName[0:5]
                tempUsernames = copy.copy(game['playerName'])
                game['gameState']['playerTableUsernames']['p1'] = getOnTableCards(tempUsernames,0)
                game['gameState']['playerTableUsernames']['p2'] = getOnTableCards(tempUsernames,1)
                game['gameState']['playerTableUsernames']['p3'] = getOnTableCards(tempUsernames,2)
                game['gameState']['playerTableUsernames']['p4'] = getOnTableCards(tempUsernames,3)

                return jsonify({'isSuccessful':True})
            else:
                return jsonify({'isSuccessful':False})
        else:
            player['password'] = request_body['password']



        msg = ""
        msg = player['username'] + ' joined the Game '

        game['playerActive'][idx] = True
        game['playerName'][idx] = inputUserName[0:8]
        tempUsernames = copy.copy(game['playerName'])
        game['gameState']['playerTableUsernames']['p1'] = getOnTableCards(tempUsernames,0)
        game['gameState']['playerTableUsernames']['p2'] = getOnTableCards(tempUsernames,1)
        game['gameState']['playerTableUsernames']['p3'] = getOnTableCards(tempUsernames,2)
        game['gameState']['playerTableUsernames']['p4'] = getOnTableCards(tempUsernames,3)

        Logs[str(game_id)]['msg'].append(msg)
        startGame(game_id)

        return jsonify({'isSuccessful': True})

def getSuit(card):
    if(card == 0):
        return 'JOKER'
    if(card >= 1 and card <= 13):
        return 'HEART'
    elif(card >=14 and card <= 26):
        return 'CLUB'
    elif(card >= 27 and card <= 39):
        return 'DIAMOND'
    else:
        return 'SPADE'

def isPlayerHaveSuit(cards , suit):
    for card in cards:
        if(getSuit(card) == suit):
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
    if(onTable.count(0) == 4 ):
        game['gameState']['suit'] = playerSuit
        return True
    if(onTable.count(0) < 4):
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

def getActualValue(card):
    if(card == 0):
        return 0
    if(card % 13 == 1):
        return 14
    elif(card % 13 == 11):
        return 11
    elif(card % 13 == 12):
        return 12
    elif(card % 13 == 0):
        return 13
    else:
        return card%13

def getScores(gameScores , onTableCards , suit):
    valuedCards = []
    isBrePoint = False
    for i in onTableCards:
        if getSuit(i) == suit:
            actual_value = getActualValue(i)
            if(actual_value == 12) :
                isBrePoint = True
            else:
                isBrePoint = False
            valuedCards.append(actual_value)
        else:
            valuedCards.append(-1)

    pointCards = [i for i in onTableCards if (getSuit(i) == 'HEART' or i == 51)]
    pointsOnBoard = getBoardPoints(pointCards)
    idx = valuedCards.index(max(valuedCards))
    cardTaker = 'p' + str(idx+1)


    for i in range(len(gameScores)):
        if i == idx:
            gameScores[i] += pointsOnBoard
    return cardTaker , gameScores , isBrePoint , idx

def rotateArray(a,n,c = 1):
    n = n*c
    r_a = (a[n:] + a[:n])
    return r_a


@app.route('/playerCard/<int:game_id>/<string:player_id>', methods=['GET'])
def getPlayerCards(game_id , player_id):
    game = getGame(game_id)
    playerCards =  game['gameState']['cards'][player_id]
    return jsonify({'playerCards': playerCards})

def getOnTableCards(onTableCards , playerIdx):
    onTableCards= rotateArray(onTableCards ,playerIdx )
    return onTableCards

@app.route('/turn/<int:game_id>', methods=['GET'])
def getTurn(game_id):
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
                return jsonify({'isSuccessful': False , 'error':'Card does not matches to Playing Suit'})
            game['gameState']['cardPassed'][player_id] = cards
            idx = game['playerId'][player['player_id']]
            game['playerCardPassed'][idx]  = True
            msg =  player['username'] + ' Selected Cards to Pass '
            Logs[str(game_id)]['msg'].append(msg)
            startPlayingGame(game_id)


        elif(game['gameState']['state'] == 'STARTED'):

            if(isValidCard(cards ,playerCards) == False):
                return jsonify({'isSuccessful': False , 'error':'Card not in your Hand'})

            if(len(cards) == 1):
                card = cards[0]
                if(isValidMove(card,playerTurn,game,player_id)):
                    playerCards.remove(card)
                    onTableCards[game['playerId'][player['player_id']]] = card
                    game['gameState']['turn'] = getNextTurn(playerTurn,orientation)
                    game['gameState']['onTableCards'] = onTableCards
                    tempCards = copy.copy(game['gameState']['onTableCards'])
                    game['gameState']['playerTableCards']['p1'] = getOnTableCards(tempCards,0)
                    game['gameState']['playerTableCards']['p2'] = getOnTableCards(tempCards,1)
                    game['gameState']['playerTableCards']['p3'] = getOnTableCards(tempCards,2)
                    game['gameState']['playerTableCards']['p4'] = getOnTableCards(tempCards,3)

                    game['gameState']['cards'][player_id] = playerCards
                    msg = player['username'] + ' Played Card '

                    Logs[str(game_id)]['msg'].append(msg)
                    doRefresh()


                    if(onTableCards.count(0) == 0):
                        round += 1
                        cardTaker , scores  , isBrePoint , idx = getScores(gameScores , onTableCards , suit)
                        print('show',cardTaker , scores  , isBrePoint , idx)
                        if(isBrePoint):
                            game['breCount'][idx] += 1
                            game['breBoys'].append('p'+str(idx+1))


                        game['gameState']['lastRoundCards'] = tempCards
                        print('temp cards : ',tempCards)
                        game['gameState']['onTableCards'] = [0,0,0,0]
                        game['gameState']['playerTableCards']['p1'] = [0,0,0,0]
                        game['gameState']['playerTableCards']['p2'] = [0,0,0,0]
                        game['gameState']['playerTableCards']['p3'] = [0,0,0,0]
                        game['gameState']['playerTableCards']['p4'] = [0,0,0,0]

                        game['gameState']['gameScores'] = scores
                        game['gameState']['round'] = round
                        game['gameState']['turn'] = cardTaker
                        game['gameState']['cardTaker'] = cardTaker


                        msg =  'Round ' + str(round) + ' Finished '

                        Logs[str(game_id)]['msg'].append(msg)
                        doRefresh()

                        if(round > 0 and round%13 == 0):
                            endOfRound(game)
                else:
                    return jsonify({'isSuccessful': False , 'error':'Select a valid suit'})

        elif(game['gameState']['state'] == 'FINISHED'):
            print("game finished")

        return jsonify({'isSuccessful': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def getNextCardPassDir(Direction):
    if(Direction == 'LEFT'):
        return 'FRONT'
    if(Direction == 'RIGHT'):
        return 'LEFT'
    if(Direction == 'FRONT'):
        return 'SELF'
    if(Direction == 'SELF'):
        return 'RIGHT'

@socket.on('connect')
def on_connect():
    msg = 'Connected socket '

    Logs['1']['msg'].append(msg)
    # socket.emit('doRefresh', {'refresh': True})



def sendScoreData(game_id):
    game = getGame(game_id)
    scores = game['gameState']['gameScores']
    breCount = game['breCount']
    playerNames = game['playerName']

    scoreidx = [i[0] for i in sorted(enumerate(scores), key=lambda x:x[1])]
    scoreData ="Scores of current players : \n\n"
    for i in range(4):
        idx = scoreidx[i]
        scoreData += (str(i+1) + '. ' +playerNames[idx] + " " + str(scores[idx]) + " " + str(breCount[idx])+"\n")
    return scoreData



@socket.on('sendMessage')
def on_sendMessage(data):
    msg = 'Send message to  socket '
    Logs['1']['msg'].append(msg)

    if(data['chatMsg'] == 'score'):
        socket.emit('message', { 'user': 'BOT', 'text': sendScoreData(1) })
    else:
        socket.emit('message', { 'user': data['userName'], 'text': data['chatMsg'] , 'player_id':data['player_id'] })



def doRefresh():
    msg = 'Refreshed'

    Logs['1']['msg'].append(msg)
    socket.emit('doRefresh', {'refresh': True})

app.debug = True
if __name__ == '__main__':
    socket.run(app)
