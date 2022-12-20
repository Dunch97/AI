import random
import math
import itertools
from copy import deepcopy

from pyparsing import actions

ids = ["111111111", "222222222"]


class OptimalTaxiAgent:
    def __init__(self, initial):
        initial_copy = deepcopy(initial)

    def act(self, state):
        raise NotImplemented


class TaxiAgent:
    def __init__(self, initial):
        initial_copy = deepcopy(initial)

        self.turns_init = initial_copy["turns to go"]
        self.board = initial_copy.pop('map')

    def taxi_action(self, state, taxi):
        # drop off
        taxi_location = state[taxi]['location']
        for passenger in state["passengers"]:
            if taxi == state['passengers'][passenger]['location']:
                if taxi_location == state['passengers'][passenger]['destination']:
                    return "drop off", taxi, passenger

        # pick up
        if state['taxis'][taxi]['capacity'] > 0:
           for passenger in state["passengers"]:
               if taxi_location == state['passengers'][passenger]['location'] and state['passengers'][passenger]['destination'] != state['passengers'][passenger]['location']:
                  return "pick up", taxi, passenger

        #refuel
        if state['taxis'][taxi]['location'] == 'G':
            return "refuel", taxi

        # move
        #check best move - if we have someone in the taxi we want to get them to destination
        #if we don't have someone, check who is best to pick up
        #consider the fuel - check if we have enough for this move, and think if it is worth it because we have penalty -10 for fuel


        locations = get_valid_locations(state['taxis'][taxi]['location'])
        location_to_destination_distance = {location: float('inf') for location in locations}
        unpicked_passengers = unpicked_delivered_inside(state)
        capacity = state['taxis'][taxi]['capacity']

        if len(unpicked_passengers) > 0 and capacity > 0:
            for location in location_to_destination_distance:
                for passenger in unpicked_passengers:
                    location_to_destination_distance[location] = min(calc_manhattan_distance(location, state['passengers'][passenger]['location']))
            best_location = min(location_to_destination_distance, key=location_to_destination_distance.get)
            return "move", taxi, best_location

        return "wait", taxi

    def act(self, state):
        new_state = translate_state(state)



        actions = {taxi: ("wait", taxi) for taxi in new_state["taxis"]}
        taxi_chosen = new_state["taxis"][0]
        action_taxi = self.taxi_action(new_state, taxi_chosen)
        actions[0] = action_taxi

        return actions.values()


def calc_manhattan_distance(loc1, loc2):
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])


def translate_state(state):
    state_copy = state.copy()
    new_state = {'taxis': {}, 'passengers': {}}

    for taxi in state_copy['taxis']:
        new_state['taxis'][taxi] = {}
        location = state_copy['taxis'][taxi]['location']
        fuel = state_copy['taxis'][taxi]['fuel']
        capacity = state_copy['taxis'][taxi]['capacity']

        new_state['taxis'][taxi] = {'location': location, 'fuel': fuel, 'capacity': capacity}
        # check if to enter the passengers in the taxi here or not

    for passenger in state_copy['passengers']:
        new_state['passengers'][passenger] = {}
        location = state_copy['passengers'][passenger]['location']
        destination = state_copy['passengers'][passenger]['destination']
        possible_goals = [goal for goal in state_copy['passengers'][passenger]['possible_goals']]

        new_state['passengers'][passenger] = {'location': location, 'destination': destination,
                                              'possible_goals': possible_goals}


def get_valid_locations(self, current_loc):
    x, y = current_loc
    max_x = len(self.board)
    max_y = len(self.board[0])
    locations = []
    for i in [-1, 1]:
        if (0 <= x + i) and ((x + i) < max_x) and ((self.board[x + i][y] == 'P') or (self.board[x + i][y] == 'G')):
            locations.append((x + i, y))
        if (0 <= y + i) and (y + i < max_y) and ((self.board[x][y + i] == 'P') or (self.board[x][y + i] == 'G')):
            locations.append((x, y + i))
    return locations

def unpicked_delivered_inside(state):

    passenger_list = []
    delivered_passenger = []
    delivered = 0
    picked_but_undelivered = []

    for passenger in state["passengers"]:
        passenger_list.append(passenger)
        if state["passengers"][passenger]["location"] == state["passengers"][passenger]["destination"]:
            delivered = delivered + 1
            delivered_passenger.append(passenger)

    for taxi in state["taxis"]:
        for passenger in passenger_list:
            for i in range(len(state["taxis"][taxi]["passengers"])):
                if state["taxis"][taxi]["passengers"][i] == passenger:
                    picked_but_undelivered.append(passenger)
                    if passenger in delivered_passenger:
                        delivered_passenger.remove(passenger)

    unpicked = passenger_list
    for passenger in passenger_list:
        if (passenger in picked_but_undelivered) or state["passengers"][passenger]["location"] == \
                state["passengers"][passenger]["destination"]:
            unpicked.remove(passenger)

    return unpicked


