# -*- coding: utf-8 -*-

import math

import matplotlib.pyplot as plt
import networkx as nx


def read_dict():
    dict_data = {}

    with open('dict.txt') as fd:
        for line in fd:
            splited_line = line.split(' ')
            data = dict(enumerate(splited_line))

            token = data[0]
            frequency = data[1].strip()  # using strip to clean tailing newline symbol
            part_of_speech = data.get(2, '').strip()  # using strip to clean tailing newline symbol

            print(token, frequency)

            dict_data[token] = int(frequency)

    return dict_data


dict_data = read_dict()

# get total weight count for compute possibility
total_weight = sum(dict_data.values())

# recompute the weight
for k, v in dict_data.items():

    # possibility = count / total_count
    # reciprocal of possibility can turn max value to min value, which can be
    # used for search max value path by search shortest path
    # log function can turn multiplication to addition: log(A * B) = log(A) + log(B)
    dict_data[k] = math.log(total_weight / v)


example = "王小明在北京的清华大学读书"

G = nx.DiGraph()

node_labels = dict()

start_node_id = '<s>'
end_node_id = '</s>'

# setup node instance
G.add_node(start_node_id, label=start_node_id)
node_labels[start_node_id] = start_node_id

G.add_node(end_node_id, label=end_node_id)
node_labels[end_node_id] = end_node_id

processed_working_str = dict()


def create_node_from_string(working_str, previous_node_id, offset, previous_node_weight):
    if working_str in processed_working_str:  # this working str have been processed already
        for next_node_id in processed_working_str[working_str]:
            G.add_edge(previous_node_id, next_node_id, weight=previous_node_weight)

        return  # end of the execution

    if working_str == "":  # if no more working str, add current node to the end node.
        G.add_edge(previous_node_id, end_node_id, weight=previous_node_weight)
        return  # end of the execution

    used_token = set()  # used to trace what token used for this working str
    head_token_id_set = set()  # used to trace what token id used for this working str as a head
    for token in dict_data.keys():
        if working_str.startswith(token):  # find a symbol starts with this char
            used_token.add(token)

            next_node_id = setup_node_edge_relationship(working_str, previous_node_id, offset, previous_node_weight, token)
            head_token_id_set.add(next_node_id)

    single_symbol_token = working_str[0]

    if single_symbol_token not in used_token:
        token = single_symbol_token
        next_node_id = setup_node_edge_relationship(working_str, previous_node_id, offset, token)
        head_token_id_set.add(next_node_id)

    processed_working_str[working_str] = head_token_id_set


def setup_node_edge_relationship(working_str, previous_node_id, offset, previous_node_weight, token):
    len_of_token = len(token)

    next_offset = offset + len_of_token
    next_working_str = working_str[len_of_token:]

    # always treat single char as symbol
    current_node_id = "{}-{}".format(offset, next_offset)
    current_node_weight = dict_data[token]

    G.add_node(current_node_id, label=token)

    # add lables info, this method is wired in networkx
    node_labels[current_node_id] = token

    G.add_edge(previous_node_id, current_node_id, weight=previous_node_weight)

    # continue process remained string
    create_node_from_string(next_working_str, current_node_id, next_offset, current_node_weight)
    return current_node_id


create_node_from_string(
    example,
    start_node_id,
    0,
    0.0  # using 0.0 than 0, used to fix bug that graphml file have two weight attributes
)

nx.draw_kamada_kawai(G, with_labels=True, labels=node_labels)

plt.show()


nx.write_graphml(
    G,
    'main.graphml',

    # Determine if numeric types should be generalized. For example,
    # if edges have both int and float 'weight' attributes,
    # we infer in GraphML that both are floats.
    infer_numeric_types=True
)

shortest_path = nx.shortest_path(G, source=start_node_id, target=end_node_id)

tokenize_result = [node_labels[i] for i in shortest_path]

print(" ".join(tokenize_result))
