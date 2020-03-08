import json
import os
import random

import bottle
from bottle import HTTPResponse

import math


"""
CONSTANTS:
    /ping
    /start
    /move
    /end
"""

# GLOBAL Variable
is_there_an_alternate_future = False
universal_future_seed = []
future_change = []
best_snek_move = ""


# Good snek kiss no_snek... or wall
# i.e check to make sure there will be no collision
def snek_no_kiss(snek_x, snek_y, where_is_snek, height, width):
    snek_body = []
    for body in where_is_snek:
        x = body["x"]
        y = body["y"]
        snek_body.append([x, y])

    possible_movements = ["up", "left", "down", "right"]
    y = snek_y - 1
    if [snek_x, y] in snek_body or y < 0:
        possible_movements.remove("up")
    y = snek_y + 1
    if [snek_x, y] in snek_body or y >= height:
        possible_movements.remove("down")
    x = snek_x - 1
    if [snek_x - 1, snek_y] in snek_body or x < 0:
        possible_movements.remove("left")
    x = snek_x + 1
    if [snek_x + 1, snek_y] in snek_body or x >= width:
        possible_movements.remove("right")

    return possible_movements


# Snek lass seeks the nearest food
def hungry_snek_want_food(snek_x, snek_y, gimme_food):
    nearest_food = 100
    nearest_food_x = 0 # left right
    nearest_food_y = 0 # up down
    for but_food_tho in gimme_food:
        food_x = but_food_tho["x"]
        food_y = but_food_tho["y"]

        x = food_x - snek_x
        y = food_y - snek_y
        food = math.sqrt( pow(x, 2) + pow(y, 2))
        if food < nearest_food:
            nearest_food = food
            nearest_food_x = x
            nearest_food_y = y


    if nearest_food_y < 0 and nearest_food_x < 0:
        if nearest_food_y > nearest_food_x:  # i.e the absolute smallest
            return ["up", "left"]
        else:
            return ["left", "up"]

    elif nearest_food_y > 0 and nearest_food_x > 0:
        if nearest_food_x > nearest_food_y:
            return ["right", "down"]
        else:
            return ["down", "right"]
    elif nearest_food_y > 0 and nearest_food_x < 0:
        return ["left"]
    elif nearest_food_x > 0 and nearest_food_y < 0:
        return ["right"]
    elif nearest_food_y is 0:
        if nearest_food_x < 0:
            return ["left", "right"]
        else:
            return ["right", "left"]
    elif nearest_food_x is 0:
        if nearest_food_y < 0:
            return ["up", "down"]
        else:
            return ["down", "up"]


# Compares both for similarity
def where_will_snek_go(give_snek_food, single_snek):
    snek_food = []
    for give_food in give_snek_food:
        if give_food in single_snek:
            snek_food.append(give_food)
    if not snek_food:
        return single_snek
    else:
        return snek_food


# Look for the best future
# Modelling the possible future as a stream
# if a future point is null []
# go back to the past and look for an alternative route
# if alternate position does not have any alternative route
# keep going back to it finds an alternative
# and then change the possible future
def future_vision(snek_x, snek_y, where_is_snek, gimme_food, height, width, future_seed_points=4):
    print('NEW VISION')
    future_possible_movements = []  # stores [ [and_away_with_snek], [and_away_with_snek], ... [] ]

    itr_future = 0
    while itr_future < future_seed_points:
        # Snake is Hungry
        give_snek_food = hungry_snek_want_food(snek_x, snek_y, gimme_food)
        print('Default Path', give_snek_food)
        # Thou shall not collide with snek or wall
        single_snek = snek_no_kiss(snek_x, snek_y, where_is_snek, height, width)
        print('Anti-Collision', single_snek)
        # Final decision
        and_away_with_snek = where_will_snek_go(give_snek_food, single_snek)
        print('Possible Movements', and_away_with_snek)
#        print('Alternate Possibilities', future_possible_movements, '\n')

        # Try to go back to the previous points
        if not and_away_with_snek:
            itr_future_alt = itr_future - 1
            while itr_future_alt > 0:
                print('Go Back!')
                and_away_with_snek = future_possible_movements[itr_future_alt]
                and_away_with_snek = and_away_with_snek
                future_possible_movements.pop(itr_future_alt)
                and_away_with_snek.pop(0)
                if not and_away_with_snek: # if and_away_with_snek becomes empty go back even further
                    itr_future_alt = itr_future_alt - 1
                else:
                    future_possible_movements.append(and_away_with_snek)
                    global is_there_an_alternate_future
                    global universal_future_seed
                    global future_change
                    is_there_an_alternate_future = True
                    universal_future_seed.append(itr_future_alt)
                    future_change.append(and_away_with_snek)
                    break
            itr_future = itr_future_alt
        else:
            future_possible_movements.append(and_away_with_snek)

        print('Alternate Possibilities', future_possible_movements)
        print(snek_x, ' ', snek_y, '\n')
        if and_away_with_snek[0] is "up":
            snek_y = snek_y - 1
        elif and_away_with_snek[0] is "down":
            snek_y = snek_y + 1
        elif and_away_with_snek[0] is "left":
            snek_x = snek_x - 1
        elif and_away_with_snek[0] is "right":
            snek_x = snek_x + 1

        itr_future = itr_future + 1

#    print('Alternate Possibilities', future_possible_movements, '\n')
    print('Decision', '\n')
    return future_possible_movements[0]


@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return HTTPResponse(status=200)


@bottle.post("/start")
def start():
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    data = bottle.request.json
    print("START:", json.dumps(data), '\n')

    response = {"color": "#736CCB",
                "headType": "evil",
                "tailType": "bwc-flake"}

    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    data = bottle.request.json
    print("MOVE:", json.dumps(data), '\n')

    # The MARESHAE Implementation
    battle_board = data["board"]
    height = battle_board['height']  # Board Height
    width = battle_board['width']  # Board Width
    gimme_food = battle_board["food"]  # Where all the food at? list
    me_snek = data["you"]  # All about Evil Snek muhehehehe

    where_is_snek = me_snek["body"] # Where snek at? list
    snek_head = where_is_snek[0]
    snek_x = snek_head["x"]
    snek_y = snek_head["y"]

    global best_snek_move
    global is_there_an_alternate_future

    if is_there_an_alternate_future is True:
        future_seed = universal_future_seed[0]
        if future_seed is not 0:
            universal_future_seed[0] = future_seed - 1
        else:
            best_snek_move = future_change[0]
            print('Change the future')
            future_change.pop(0)
            universal_future_seed.pop(0)
            if len(universal_future_seed) is 0:
                is_there_an_alternate_future = False
    else:
        # of the form [ "", "", ""]
        best_snek_move = future_vision(snek_x, snek_y, where_is_snek, gimme_food, height, width, 100)
        # of the form ""
        best_snek_move = best_snek_move[0]


    # Choose a random direction to move in

    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": best_snek_move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data), '\n')
    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
