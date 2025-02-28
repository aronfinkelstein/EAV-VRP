import models.road_network.create_graph as cg
import models.vehicle_models.energy_consumption as ec
import models.weighting.weight_integration as wi
import json
import math
import pandas as pd
import random
from pprint import pprint

def find_random_route(map_data:dict, road_df:dict, graph, plot = False, weights_type = 'default'):
    '''
    Takes in a overall map, road and graph, simulates a random route and returns data for that route.
    '''
    G = wi.add_weights_to_graph(graph, weights_type)
    nodes = road_df["u"].to_list()
    random_values = random.sample(nodes, 2)
    route = cg.dijkstra(G, random_values[0], random_values[1])

    route_dict = {}
    i = 0
    for i in range(len(route)-1):
        path = cg.find_path_with_nodes(map_data, route[i], route [i + 1])
        route_dict.update(path)
    if plot:
        fig, ax = cg.plot_graph_with_routes(graph,route)
    else:
        pass

    return route_dict

def find_route(map_data:dict, road_df:dict, graph, start_node: int, end_node: int, plot = False, weights_type = 'default'):
    '''
    Takes in a overall map, road and graph, simulates a specific route and returns data for that route.
    '''

    G = wi.add_weights_to_graph(graph, weights_type)

    route = cg.dijkstra(G, start_node, end_node)

    route_dict = {}
    i = 0
    for i in range(len(route)-1):
        path = cg.find_path_with_nodes(map_data, route[i], route [i + 1])
        route_dict.update(path)

    if plot:
        fig, ax = cg.plot_graph_with_routes(graph,route)
    else:
        pass

    return route_dict

def return_route_data(route_dict:dict, vehicle_data:dict, static_data:dict, motor_eff:float)->float:
    '''
    Analyses a route and returns consumption, distance, and climb data. 
    '''
    consumptions = []
    distances = []
    climbs = []
    for path, pathdata in route_dict.items():
        for section, data in pathdata.items():
            if "section" in section: 
                data["velocity"] = 8.9408
                data["acceleration"] = 0
                tract_power = ec.physical_model(vehicle_data, static_data, data)
                batt_power = ec.battery_power_model(tract_power, motor_eff)

                energy = ec.get_edge_consumption(batt_power, data)

                distances.append(data['distance'])
                consumptions.append(energy)
                climbs.append(data['climb'])

    total_distance = sum(distances)
    total_consumption = sum(consumptions)
    total_climb = sum(climbs)

    return total_distance,total_consumption,total_climb
