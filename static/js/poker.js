// 牌組
var socket = io.connect('http://localhost:5000');

const cardValues = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const cardSuits = ["♠", "♡", "♢", "♣"];
const cardBack = "🃏"
const inputValue = document.getElementById("input");

var currentStage = 0;
var flopCards = [];
var turnCards = [];
var riverCards = [];
var player1Cards = [];
var player2Cards = [];
var player3Cards = [];
var player4Cards = [];
var remainChips = []; 

var pot = 0;
var potString = "Pot: $";
var myMove = false

function getValue() {
    raiseValue = document.getElementById("input").value;
    inputValue.value = "";
}
// 回傳選到哪張卡片
function getCard(value, suit) {
    return `${value}${suit}`;
}

// translate card object to representation image
function translateCard(card) {
    let f = cardValues[card.face - 1];
    let s = "";
    console.log('in translateCard');
    if (card.suite == "club") {
        s = "clubs";
    } else if (card.suite == "diamond") {
        s = "diamonds";
    } else if (card.suite == "heart") {
        s = "hearts";
    } else if (card.suite == "spade") {
        s = "spades";
    }
    if (card.face == 11)
        return "static/images/jack_of_"+s + ".png";
    else if(card.face ==12)
        return "static/images/queen_of_" +s + ".png";
    else if (card.face==13)
        return "static/images/king_of_"+s + ".png";
    else if (card.face==1 || card.face==14)
        return "static/images/ace_of_"+s+".png";
    else
        return "static/images/" + card.face + "_of_"+s + ".png";
}

function displayCard(card, elementId) {
    console.log('in displayCard');
    console.log(card);
    var element = document.getElementById(elementId);
    element.style.backgroundImage = "url('" + translateCard(card) + "')";
}


function displayCards(cards, elementIds) {
    for (let i = 0; i < cards.length; i++) {
        displayCard(cards[i], elementIds[i]);
    }
}

// function displayPotString(elementId) {
//     document.getElementById(elementId).textContent = potString;
// }

function displayPot() {
    console.log("display pot in");
    var potAmount = Cookies.get('potAmount') || 0;
    document.getElementById("pot").textContent = "Total pot: $" + potAmount;
  }

function displayCardBack(elementId) {
    var element = document.getElementById(elementId);
    element.style.backgroundImage = "url('static/images/cardback.png')";
}

function displayCardBacks(elementIds) {
    for (let i in elementIds) {
        displayCardBack(elementIds[i]);
    }
}

// shuffle the cards using Durstenfeld shuffle
function shuffle(arr) {
    let j = 0;
    for (let i = arr.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

// create full deck
function createDeck() {
    let deck = [];
    let suites = ["club", "diamond", "heart", "spade"];
    for (let i = 1; i <= 13; i++) {
        for (let s in suites) {
            deck.push({
                suite: suites[s],
                face: i
            })
        }
    }
    return deck
}

function displayChips(remainingChips) {
    console.log("display Chips in ")
    // Accessing remainingChips and playerId values
    for (let i = 0; i < remainingChips.length; i++) {
        let playerId = remainingChips[i].playerId;
        let chips = remainingChips[i].remainingChips;

        // Use the playerId and chips as needed
        console.log('Player ID: ' + playerId);
        console.log('Remaining Chips: ' + chips);
        Cookies.set('player1Chips',remainingChips[0].remainingChips);
        // Update the display for the player's chips
        let playerChipsElement = document.getElementById(`player${playerId}-chips`);
        playerChipsElement.textContent = `Chips: ${chips}`;
        playerChipsElement.style.display = "block";
    }
}



function hideChips(remainingChips) {
    console.log("Hiding chips");
  
    // Accessing remainingChips and playerId values
    for (let i = 0; i < remainingChips.length; i++) {
      let playerId = remainingChips[i].playerId;
      let chips = remainingChips[i].remainingChips;
  
      // Use the playerId and chips as needed
      console.log('Player ID: ' + playerId);
      console.log('Remaining Chips: ' + chips);
  
      // Hide the player's chips
      let playerChipsElement = document.getElementById(`player${playerId}-chips`);
      playerChipsElement.style.display = 'none';
    }
  }
  
function showNewGame() {
    $('#new-game').show();
    displayCardBacks(["player1-card1", "player1-card2"]);
    displayCardBacks(["player2-card1", "player2-card2"]);
    displayCardBacks(["player3-card1", "player3-card2"]);
    displayCardBacks(["player4-card1", "player4-card2"]);
    displayCardBacks(["community-card1","community-card2","community-card3","community-card4","community-card5"]);
   
    //   document.getElementById('new-game').style.display = 'block';

    
}

function showOverlay(){
    document.getElementById('overlay').style.display = 'block';
}

function hideOverlay() {
    document.getElementById('overlay').style.display = 'none';
  }
  
function makeSelection(option) {
    // Perform actions based on the selected option
    console.log('Selected option:', option);
    Cookies.set('playerCnt', option);
    hideOverlay();
}


function displayAction(playerId, action) {
    // Modify this function based on your desired display logic
    // For example, you can update the HTML element associated with the player's ID

    // Example: Update a specific element with the action information
    let actionElementId = `#player${playerId}-action`;  // Assuming the element ID follows a specific pattern
    // $(actionElementId).text(`Action: ${action.action}`);
    if (action.action === 'fold') {
        // let cardElementId = `player${playerId}-fold`; // Adjust this based on the ID of the player's card element
        foldCard(playerId);
    }
    $(actionElementId).text(`${action.action}`);

}


function removeAction(){
    for (let i=1;i<=4;i++)
    {
        let actionElementId = `#player${playerId}-action`;
        $(actionElementId).empty();
    }
}  

function displayPrompt() {
    let promptElement = document.getElementById('prompt');
    promptElement.innerHTML = "It's your turn!";
}

function removePrompt(){
    let promptElement = document.getElementById('prompt');
    promptElement.innerHTML = "";
}

function displayWinner(winner) {
    console.log("display winner in");
    console.log(winner[0][0]);
    let winElement = document.getElementById('winner');
    let winnerText = "Winner: ";
    
    for (let i = 0; i < winner.length; i++) {
        if (i > 0) {
            winnerText += ", ";
        }
        if (winner[i][0] === 1) {
            winnerText += "Player 1";
        } if (winner[i][0] === 2) {
            winnerText += "Player 2";
        } if (winner[i][0] === 3) {
            winnerText += "Player 3";
        } if (winner[i][0] === 4) {
            winnerText += "Player 4";
        }
    }
    winElement.textContent = winnerText;
}

function removeWinner(){
    let winElement = document.getElementById('winner');
    winElement.textContent="";
}


function foldCard(elementId) {
    let foldElement = document.getElementById(`player${elementId}-fold`);
    foldElement.textContent = "FOLD";
}

function unfoldCard() {
    for (let i=1;i<5;i++){
    let foldElement = document.getElementById(`player${i}-fold`);
    foldElement.textContent = "";
    }
}

function updateElementPositions() {
    console.log('update element');
    
    const positions = [
      "player1-button",
      "player2-button",
      "player3-button",
      "player4-button"
    ];
    let smallidx = Cookies.get('sb');
    let bigidx = Cookies.get('bb');
    let buttonidx = Cookies.get('button');
    // list = JSON.parse(list); // Parse the string into an array
    
    
  
    // Get the current positions of the elements
    const buttonElement = document.getElementById("button");
    const bigBlindElement = document.getElementById("bigblind");
    const smallBlindElement = document.getElementById("smallblind");
  
    // Update the positions of the elements
    buttonElement.className = "player"+buttonidx+"-button" // Index 2 represents the button position
    bigBlindElement.className = "player"+bigidx+"-button"  // Index 1 represents the big blind position
    smallBlindElement.className = "player"+smallidx+"-button"  // Index 0 represents the small blind position
  }
  

  function resetElementPositions() {
    document.getElementById("button").className = "player4-button";
    document.getElementById("bigblind").className = "player2-button";
    document.getElementById("smallblind").className = "player1-button";
  }
  
function oneAI(){
    msg = JSON.stringify({'playerCnt': 2});
    socket.emit('newTable', msg);
    // Hide player 3
    $('#community-cards').css('display', 'block');
    $('#player1').css('display', 'block');

    // Hide player 4
    $('#player2').css('display', 'block');
    //newTable();
    //return 1;
    hideOverlay();
    removeWinner();
    removePrompt()
    hideChips(remainChips);
    Cookies.set("oneAI",1);
    Cookies.set("twoAI",0);
    Cookies.set("threeAI",0);
    // document.getElementById('bigblind').style.display = 'block';
    // document.getElementById('smallblind').style.display = 'block';
    // document.getElementById('button').style.display = 'none';
    showNewGame();
    updateElementPositions();
}

function twoAI(){
    msg = JSON.stringify({'playerCnt': 3});
    socket.emit('newTable', msg);
    // updateElementPositions();
    $('#community-cards').css('display', 'block');
    $('#player1').css('display', 'block');

    // Hide player 4
    $('#player2').css('display', 'block');
    $('#player3').css('display', 'block');
    //newTable();
    // Hide player 3
    hideOverlay();
    removeWinner();
    removePrompt();
    hideChips(remainChips);
    Cookies.set("twoAI",1);
    Cookies.set("oneAI",0);
    Cookies.set("threeAI",0);
    // document.getElementById('bigblind').style.display = 'block';
    // document.getElementById('smallblind').style.display = 'block';
    // document.getElementById('button').style.display = 'block';
    showNewGame();
    updateElementPositions();

// Hide player 4
    // $('#player4').css('display', 'none');
    // return 2;
    }

function threeAI(){
    msg = JSON.stringify({'playerCnt': 4});
    socket.emit('newTable', msg);
    // updateElementPositions();
    $('#community-cards').css('display', 'block');
    $('#player1').css('display', 'block');

    // Hide player 4
    $('#player2').css('display', 'block');
    $('#player3').css('display', 'block');

    // Hide player 4
    $('#player4').css('display', 'block');
    //newTable();
    // return 3;
    hideOverlay();
    removeWinner();
    removePrompt();
    hideChips(remainChips);
    Cookies.set("twoAI",0);
    Cookies.set("oneAI",0);
    Cookies.set("threeAI",1);
    // document.getElementById('bigblind').style.display = 'block';
    // document.getElementById('smallblind').style.display = 'block';
    // document.getElementById('button').style.display = 'block';
    showNewGame();
    updateElementPositions();
}

function clearTable() {
    // Show player 1, player 2, player 3, and community cards
    Cookies.set("OneAI",0);
    Cookies.set("twoAI",0);
    Cookies.set("threeAI",0);
    $('#player1').css('display', 'none');
    $('#player2').css('display', 'none');
    $('#player3').css('display', 'none');
    $('#player4').css('display', 'none');
    $('#community-cards').css('display', 'none');
    document.getElementById('bigblind').style.display = 'none';
    document.getElementById('smallblind').style.display = 'none';
    document.getElementById('button').style.display = 'none';
}


function changeButtonText() {
    console.log("change button in ");
    var callButton = document.getElementById("call");
    // var toCallValue = $("#toCallValue").text();
    var toCallValue = Cookies.get('toCall');
    callButton.textContent = "Call: $"+toCallValue;
    console.log(toCallValue);
}
  

// function setupFormValidation() {
//     var form = document.getElementById('myForm');
//     var input = document.getElementById('myInput');
//     var errorMessage = document.getElementById('error-message');
  
//     form.addEventListener('submit', function(event) {
//       if (!input.checkValidity()) {
//         event.preventDefault();
//         showError('Please enter a value');
//       }
//     });
  
//     function showError(message) {
//       errorMessage.textContent = message;
//       errorMessage.style.display = 'block';
//     }
//   }
  


// 開設新局
function newGame() {
    currentStage = 0;
    // pot =0;
    // Cookies.set('potAmount', 0);
    
    // Cookies.set(potAmount,0);
    // removeAction();
    // updateElementPositions();
    unfoldCard();
    removeWinner();
    pot = 0;
    // displayCardBacks(["community-card1", "community-card2", "community-card3", "community-card4", "community-card5"]);
    // displayCardBacks(["player2-card1", "player2-card2"]);
    // displayCardBacks(["player3-card1", "player3-card2"]);
    // displayCardBacks(["player4-card1", "player4-card2"]);
    let x = Cookies.get("oneAI");
    let y = Cookies.get("twoAI");
    let z = Cookies.get("threeAI");
    if (x==="1"){
        document.getElementById('bigblind').style.display = 'block';
        document.getElementById('smallblind').style.display = 'block';
        document.getElementById('button').style.display = 'none';
        //Cookies.get("oneAI")
    }else if (y==="1"){
        document.getElementById('bigblind').style.display = 'block';
        document.getElementById('smallblind').style.display = 'block';
        document.getElementById('button').style.display = 'block';
    }else if (z === "1"){
        document.getElementById('bigblind').style.display = 'block';
        document.getElementById('smallblind').style.display = 'block';
        document.getElementById('button').style.display = 'block';
    }

    displayChips(remainChips);
    // displayPotString("potString");
    displayPot();
    socket.emit('newGame');
    // Call the setupFormValidation function to set up the form validation
    // setupFormValidation();
}

// new table
function newTable() {
    currentStage = 0;
    // pot =0;
     Cookies.set('potAmount', 0);
    // socket.emit('newTable', msg);
    pot=0;
    clearTable();
    showOverlay();
    // Cookies.set(potAmount,0);
    // removeAction();
    //updateElementPositions();
    unfoldCard();
    removeWinner();
    // pot = 0;
    // updateElementPositions();
    // displayCardBacks(["community-card1", "community-card2", "community-card3", "community-card4", "community-card5"]);
    // displayCardBacks(["player2-card1", "player2-card2"]);
    // displayCardBacks(["player3-card1", "player3-card2"]);
    // displayCardBacks(["player4-card1", "player4-card2"]);
    // // displayPotString("potString");
    // showNewGame();
    displayPot();
    // displayChips(remainChips);
    // setupFormValidation();
    // removeAction();
}

function rcvFlopCard() {
    msg = JSON.stringify({game_id: Cookies.get('gameId')});
    socket.emit('getFlopCard', msg); //emit front send to back
}

function rcvTurnCard() {
    msg = JSON.stringify({game_id: Cookies.get('gameId')});
    socket.emit('getTurnCard', msg);
}

function rcvRiverCard() {
    msg = JSON.stringify({game_id: Cookies.get('gameId')});
    socket.emit('getRiverCard', msg);
}

function rcvOpponentCard() {
    msg = JSON.stringify({game_id: Cookies.get('gameId'), player_id: Cookies.get('player1Id')});
    socket.emit('getOpponentPlayerHand', msg);
}

function displayFlop() {
    displayCards(flopCards, ["community-card1", "community-card2", "community-card3"]);
}

function displayTurn() {
    displayCards(turnCards, ["community-card4"]);
}

function displayRiver() {
    displayCards(riverCards, ["community-card5"]);
}

function showAllHands() {
    displayCards(player2Cards, ["player2-card1", "player2-card2"]);
    displayCards(player3Cards, ["player3-card1", "player3-card2"]);
    displayCards(player4Cards, ["player4-card1", "player4-card2"]);
}

function check() {
    msg = {
        game_id: Cookies.get('gameId'), 
        player_id: Cookies.get('player1Id'),
        action: {
            'action': 'check',
            'amount': 0
        }
    }
    // displayAction(player_id,'check');
    socket.emit('check', JSON.stringify(msg));
}

function raise() {
    console.log('in raise')
    let raiseValue = document.getElementById("input").value;
    console.log('value = ' + raiseValue)
    // Check if the input value is empty or not a number
    if (raiseValue === "" || isNaN(raiseValue)) {
        // document.getElementById("error-message").textContent = "Please enter a valid numeric value.";
        document.getElementById("error-message").textContent = "Please enter a valid numeric value.";
        document.getElementById("input").value = "";
        return;
    }
    // Clear the error message if the input is valid
    document.getElementById("error-message").textContent = "";
    // Clear the input box
    document.getElementById("input").value = "";
    msg = {
        game_id: Cookies.get('gameId'), 
        player_id: Cookies.get('player1Id'),
        action: {
            'action': 'raise',
            'amount': raiseValue
        }
    }
    socket.emit('raise', JSON.stringify(msg));
    // Clear the error message if the input is valid
    displayAction(player_id,'raise');
    
}

function fold() {
    msg = {
        game_id: Cookies.get('gameId'), 
        player_id: Cookies.get('player1Id'),
        action: {
            'action': 'fold',
            'amount': 0
        }
    }
    socket.emit('fold', JSON.stringify(msg));
    // displayAction(player_id,'fold');
}

//function allIn() {
    //console.log("allin in");
    // socket.emit('allIn')
    //let raiseValue = Cookies.get('player1Chips');
    //msg = {
        //game_id: Cookies.get('gameId'), 
        //player_id: Cookies.get('player1Id'),
        //action: {
            //'action': 'raise',
            //'amount': raiseValue
        //}
    //}
    //socket.emit('raise', JSON.stringify(msg));
//}

function call() {
    let toCallValue = Cookies.get('toCall');
    msg = {
        game_id: Cookies.get('gameId'), 
        player_id: Cookies.get('player1Id'),
        action: {
            'action': 'call',
            'amount': toCallValue
        }
    }
    socket.emit('call', JSON.stringify(msg));
    // displayAction(player_id,'call');
}

var socket = io.connect();
socket.on('status_response', function (msg) {
    // var date = new Date();
    // $('#new-game').append('<p> status: ' + msg.data + "Time: "+ date+ '</p>');
    console.log(msg.data);
    socket.send('message');
    // document.getElementById('status').textContent = msg
});

socket.on('message', function (msg) {
    console.log('msg=');
    console.log(msg);
    console.log(typeof msg);
    // console.log(document.cookie);
    Cookies.set('name', 'value');
    console.log(Cookies.get('name'));
    Cookies.remove('name');
    console.log(Cookies.get());
    document.getElementById('community-card5').textContent = 'hello world';
});

socket.on('logging', function (msg) {
    console.log(msg);
})

socket.on('newGameResponse', function (msg) {
    console.log('in newGameResponse');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    console.log(msg_json.order.length);
    let len = msg_json.order.length;
    Cookies.set('gameId', msg_json.game_id);
    Cookies.set('player1Id', msg_json.player_id);
    //Cookies.set('player2Id', msg_json.opponent_ids[0])
    //Cookies.set('player3Id', msg_json.opponent_ids[1])
    //Cookies.set('player4Id', msg_json.opponent_ids[2])
    Cookies.set('player2Id', 2)
    Cookies.set('player3Id', 3)
    Cookies.set('player4Id', 4)
    Cookies.set('sb',msg_json.order[0]);
    Cookies.set('bb',msg_json.order[1]);
    Cookies.set('button',msg_json.order[len-1]);
    console.log(msg_json.order[len-1]);
    socket.emit('getPlayerHand', msg);
    updateElementPositions();
})

socket.on('newTableResponse', function (msg) {
    console.log(msg);
    Cookies.set('player2Id', 2)
    Cookies.set('player3Id', 3)
    Cookies.set('player4Id', 4)
    updateElementPositions();
})

socket.on('rcvPlayerHand', function (msg) {
    console.log('in rcvPlayerHand');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    if (!msg_json.isCard) {
        console.log("can't reveal cards");
        return;
    }
    
    for (let i = 0; i < msg_json.card.length; i++) {
        player = msg_json.card[i];
        console.log("debug player: ", player);
        //console.log("debug player id: ", player.player_id);//order not include real plyer
        //console.log("debug player Id: ", player.player_Id);
        //console.log("debug player Id: ", player.player_Id);
        //Cookies.get('player2Id') == player.player_id
        
        if (player.player_id==1) {
            player1Cards = player.hand;
            displayCards(player1Cards, ["player1-card1", "player1-card2"]);
        } else if (Cookies.get('player2Id') == player.player_id) {
            player2Cards = player.hand;
            displayCards(player2Cards, ["player2-card1", "player2-card2"]);
        } else if (Cookies.get('player3Id') == player.player_id) {
            player3Cards = player.hand;
            displayCards(player3Cards, ["player3-card1", "player3-card2"]);
        } else {
            player4Cards = player.hand;
            displayCards(player4Cards, ["player4-card1", "player4-card2"]);
        }

    }
})















socket.on('promptMyMove', function (msg) {
    console.log('in promptMyMove');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    if (!msg_json.myMove) {
        return
    } else {
        console.log('my turn to move!')
        myMove = true
    }
    displayPrompt();
})

socket.on('rcvFlopCard', function (msg) {
    console.log('in rcvFlopCard');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    if (msg_json.isCard) {
        flopCards = msg_json.card;
        displayFlop();
    } else {
        console.log("can't show flop cards yet");
    }
    
})

socket.on('rcvTurnCard', function (msg) {
    console.log('in rcvTurnCard');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    if (msg_json.isCard) {
        turnCards = msg_json.card;
        displayTurn();
    } else {
        console.log("can't show turn cards yet");
    }
})

socket.on('rcvRiverCard', function (msg) {
    console.log('in rcvRiverCard');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    if (msg_json.isCard) {
        riverCards = msg_json.card;
        displayRiver();
    } else {
        console.log("can't show river cards yet");
    }
})

socket.on('rcvPot', function (msg) {
    // {"pot": pot_val}
    console.log('in rcvPot');
    console.log(msg);
    let msg_json = JSON.parse(msg);
    pot = msg_json.pot;
    Cookies.set('potAmount',pot);
    displayPot();
})

socket.on('notifyPlayerAction', function (msg) {
    console.log(msg);
    let msg_json = JSON.parse(msg);
    Cookies.set('toCall', msg_json.toCall);
    // console.log(msg_json.toCall);
    // Cookies.set('potAmount',potAmount+msg_json.toCall);
    let playerId = msg_json.actionTakerId;
    let action = msg_json.action;
    removePrompt();
    displayAction(playerId,action);
    $("#toCallValue").text(msg_json.toCall.toString());
    changeButtonText();
    return;
})

socket.on('notifyPlayerStatus', function (msg) {
    console.log(msg);
    let msg_json = JSON.parse(msg);
    console.log(msg_json);
    pot = msg_json.pot;
    Cookies.set('potAmount',pot);
    displayPot();
    remainChips = msg_json.remainingChips;
    displayChips(remainChips);
    /*if (action.action==='fold')
    {
        foldCard(playerId);
    }
    displayCards(player1Cards, ["player1-card1", "player1-card2"]);
    displayCards(player2Cards, ["player2-card1", "player2-card2"]);
    displayCards(player3Cards, ["player3-card1", "player3-card2"]);
    displayCards(player4Cards, ["player4-card1", "player4-card2"]);
    */
})

socket.on('rcvEndgameInfo', function (msg) {
    console.log(msg);
    let msg_json = JSON.parse(msg);
    console.log(msg_json);
    console.log(msg_json.winner);
    let win = msg_json.winner;
    displayWinner(win);
    showAllHands();
    //  newGame();
})

function showGameRules(){
    document.getElementById('gameRules').style.display = 'block';
}

function hideGameRules() {
    document.getElementById('gameRules').style.display = 'none';
  }


document.getElementById("1").addEventListener("click",oneAI);
document.getElementById("2").addEventListener("click",twoAI);
document.getElementById("3").addEventListener("click",threeAI);
document.getElementById("new-table").addEventListener("click", newTable);
document.getElementById("new-game").addEventListener("click", newGame);
document.getElementById("check").addEventListener("click", check);
document.getElementById("raise").addEventListener("click", raise);
document.getElementById("fold").addEventListener("click", fold);
//document.getElementById("allin").addEventListener("click", allIn);
document.getElementById("call").addEventListener("click", call);
document.getElementById('showRulesButton').addEventListener("click", showGameRules);
document.getElementById('closeRulesButton').addEventListener("click", hideGameRules);
// document.getElementById("rcvFlopCard").addEventListener("click", rcvFlopCard);
// document.getElementById("rcvTurnCard").addEventListener("click", rcvTurnCard);
// document.getElementById("rcvRiverCard").addEventListener("click", rcvRiverCard);
document.getElementById("rcvOpponentCard").addEventListener("click", rcvOpponentCard);