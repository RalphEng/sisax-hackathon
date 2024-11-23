import openai

# Sehr sehr rudimentärer und extrem gehackter Prototyp für die Interaktion mit OpenAI API (GPT4) um Skat zu spielen.
#
# Der Prototyp spielt derzeit nur Farbspiele mit Trumpf Karro und immer als einer der zwei Gegenspieler.
# (Das ist aber nur bedingt durch die Zeit den Propmpt an den richtigen Stellen dynamisch anzupassen.)
#
# TODO (sehr viel):
# - Spielart und Reizen dynamisch einbinden (Reizen war nicht Teil des Prototyps) aber man kann das Ergebnis der Reizung als Input verwenden
# - Dynamische Information über den Skat (wenn die KI Alleinspieler ist)
# -- Abhänig von der Spielart die Regelhinweise für die KI anpassen
# - Historie der gespielten Karten einbauen
# - Prompt wer den Stich gewonnen hat
# - Fehlerbehandlung
# -- Fehleeingaben
# -- Wenn die KI eine Karte spielt, die nicht in der Hand ist bzw die nicht gespielt werden darf
# - Testing
# - JSON als Outputformat der API verwenden
#
# Lessons Lerned:
# - Im Prompt zuerst fragen nach:
# Analyse der Situation.
# Welche "Vermutung" das LLM Vermutungen hast über die Karten der anderen Spieler anstellt
# und welche Optionen (spielbare Karten) die KI hat.
# Erst danach nach der Karte fragen die gespielt werden soll. - Führt zu deutlich besseren und korrekteren (spielbaren) Antworten.

# Set your OpenAI API key
openai.api_key = "<ENTER YOUR KEY HERE>"


def chat_with_openai(prompt):
    print("Prompt:")
    print(prompt)
    try:
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the appropriate model
            # TODO System prompt
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extract and print the response
        print("AI Response:")
        print(response['choices'][0]['message']['content'])
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"An error occurred: {e}")

# Propmpt OpenAI to play a card
# hand: List of cards in the hand
# stich: List of players and cards played in the current round
# Returns the card played by the AI: "Pik 10", "Karo Bube"
#
# TODO: replace fixed "Spielerinformation" über das Reizen with dynamic information
# TODO: replace fixed "Spielart" with dynamic information
# TODO: replace fixed "Parteinenstellung" with dynamic information
# TODO: add history of played cards (see prompt template file)
# TODO: repeat prompt until the result is parsed correctly
def play(hand, stich):
    prompt =  f"""
        Du spielst Skat nach der internationale Skatordnung.
        Gespielt wird mit französischem Blatt.

        ## Spielerinformation
        - Spieler 1: (Klaus) Vorderhand: raus bei 18
        - Spieler 2: (Svent) Mittelhand: gereitz bis 18
        - Spieler 3: (DU) Hinterhand: raus bei 18

        ## Spielart
        - Farbspiel, Trumpf ist Karo.
        - keine weiteren Besonderheiten:
        -- kein Hand angesagt
        -- nicht Overt
        -- kein Null

        ## Parteinenstellung
        - Du bist Alleinspieler
        - Spieler 1 (Klaus) und Spieler 2 (Peter) sind deine Gegenspieler

        - Spieler 2 (Peter) ist Alleinspieler
        - Du spielt mit Spieler 1 (Klaus) zusammen als Gegenenspieler


        ## Aktueller Stich
        - Vorhand: {stich[0]['player']} {stich[0]['card']}
        - Mittelhand: {stich[1]['player']} {stich[1]['card']}
        - Hinterhand: {stich[2]['player']} {stich[2]['card']}

        ## Auf der Hand hällst du die Karten:
        - {', '.join(hand)}

        ## Hinweis:
        - Versuche, den Stich zu gewinnen, wenn es strategisch sinnvoll ist.
        - Priorisiere das Behalten von Trumpfkarten für spätere Stiche. //??

        ## Hinweis:
        - Versuche, den Stich zu gewinnen, wenn es strategisch sinnvoll ist.
        - Beachte die Regeln des Skatspiels
        -- Du musst bedienen wenn du eine Karte der Farbe hast die Vorhand ausgespielt hat
        -- Wenn du keine passende Karte hast musst du entscheiden ob du mit einem Trumpf stichst oder eine andere Karte Abwirfst
        --- Du kannst nur Abwerfen oder Stechen wenn due keine passende Karte hast!
        -- Beachte bei Tümpfen sind die Höchsten Tümpfe (in dieser Reihenfolge): Kreutz Bube, Pik Bube, Herz Bube, Karo Bube und dann kommen erst die Trümpfe des Farbspiels 


        ## Deine Entscheidung
        1. Analyse der Situation.
        2. Welche Vermutungen hast du über die Karten der anderen Spieler
        3. Welche Optionen (spielbare Karten) hast du?
        4. Wähle eine Option aus: WELCHE KARTE SPIELST DU? (Beantworte Punkt 4 im Format: ´**ENTSCHEIDUNG: <Name der Karte>** schreibe die Zahlen dabei als Nummer: 7, 8, 9 z.B. "**Entscheidung: Pik 10**" oder "**Entscheidung: Karo Bube**")
    """

    result = chat_with_openai(prompt)
    return result.split("**Entscheidung: ")[1].split("**")[0]


# parse short card names to long card names
# Input: first letter color, second (+third) letter for number example "PK" -> Output: "Pik König"
# use color "S" for "Schellen" instead of "K" for "Karo" because of the same starting letter as "Kreuz"
# TODO: error handling for invalid card names
def parseCard(card):
    card_colors = {
        'K': 'Keuz',
        'P': 'Pik',
        'H': 'Herz',
        'S': 'Karo'
    }
    card_numbers = {
        'A': 'Ass',
        'K': 'König',
        'D': 'Dame',
        'B': 'Bube',
        '10': 'Zehn',
        '9': 'Neun',
        '8': 'Acht',
        '7': 'Sieben'
    }

    card_color = card.strip()[0]
    card_number = card.strip()[1:]

    # Übersetze die Farbe und die Nummer
    translated_color = card_colors[card_color.upper()]
    translated_number = card_numbers[card_number.upper()]

    # Füge die übersetzte Karte zur Liste hinzu
    return translated_color + " " + translated_number

# parse short player names to long player names
def parsePlayer(player):
    players = {
        '1': 'Spieler 1: (Klaus)',
        '2': 'Spieler 2: (Sven)',
        'D': 'DU'
    }
    return players[player.upper()]


# parse several short colon (,) separated card names to a list of long card names
# example: "P10, KB" -> ["Pik 10", "Kreuz Bube"] 
def card_names_translator(cards_input):
    # Teile die Eingabe an Kommas
    cards = cards_input.split(",")

    print(cards)
    translated_cards = []

    # Gehe durch jede Karte und übersetze sie
    for card in cards:
        translated_cards.append(parseCard(card))

    return translated_cards

# ask the user for the current "Stich" and return the list of played cards in order "Vorhand", "Mittelhand", "Hinterhand" with a single input string
# Example retun value (for input "1:K10, D:?, 2:?"):
# [
#    {"player": "Spieler 1: (Klaus)", "card": "spielt Pik 10"},
#    {"player": "DU", "card": [DEINE ENTSCHEIDUNG]}
#    {"player": "Spieler 2: (Sven)", "card": "hat noch nicht gespielt"},
# ]
def stich():
    #Input Format: <Vorhand>,<Mittelhand>,<Hinterhand>
    #round_input = "1:K10, D:?, 2:?"
    round_input = input("Bitte geben Sie den aktuellen Stich ein in der Reihenfolge Vorhand, Mittelhand, Hinterhand - 1,2=Spieler 1,2, D=DU (KI), ?=noch nicht gespielt: <Player(1,2,D)>:K10, D:? ...: ")

    # Teile die Eingabe an Kommas
    hands = round_input.split(",")

    stich_list = []
    # Gehe durch jede Hand und übersetze sie
    for hand in hands:
        # Input Format: <Spieler>:<Karte>
        playerKey, cardKey = hand.strip().split(":")
        player = parsePlayer(playerKey.strip())
        # "?" means the player has not played yet
        # requires different text for DU/KI and other players
        if cardKey.strip() == "?":
            if(playerKey.strip() == "D"):
                card = "[DEINE ENTSCHEIDUNG]"
            else:
                card = "hat noch nicht gespielt"
        else:
            card = "spielt " + parseCard(cardKey.strip())
        stich_list.append({"player" : player, "card": card})
        
    return stich_list



def main ():
    cards_input = input("Die Hand Karten der KI (z.B. K10, PB für Kreuz 10, Pik Bube): ")
    #cards_input = "SB,S10,S7,H10,PK,H7,HD,S8,P7,P9" # fixed
    hand = card_names_translator(cards_input)
    print(hand)
    # chat_with_openai()

    for i in range(10):
        print("Hand ", hand)
        stichCards = stich()
        playedCard = play(hand, stichCards)
        hand.remove(playedCard)
    

main()