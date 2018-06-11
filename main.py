from graphviz import Digraph


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

            dict_data[token] = frequency

    return dict_data


dict_data = read_dict()


example = "王小明在北京的清华大学读书"

dot = Digraph(comment='The Round Table')

start_node_id = '<s>'
end_node_id = '</s>'

# setup node instance
dot.node(start_node_id)
dot.node(end_node_id)

processed_working_str = dict()


def create_node_from_string(working_str, previous_node_id, offset):
    if working_str in processed_working_str:  # this working str have been processed already
        for next_node_id in processed_working_str[working_str]:
            dot.edge(previous_node_id, next_node_id)

        return  # end of the execution

    if working_str == "":  # if no more working str, add current node to the end node.
        dot.edge(previous_node_id, end_node_id)
        return  # end of the execution

    used_token = set()  # used to trace what token used for this working str
    head_token_id_set = set()  # used to trace what token id used for this working str as a head
    for token in dict_data.keys():
        if working_str.startswith(token):  # find a symbol starts with this char
            used_token.add(token)

            next_node_id = setup_node_edge_relationship(working_str, previous_node_id, offset, token)
            head_token_id_set.add(next_node_id)

    single_symbol_token = working_str[0]

    if single_symbol_token not in used_token:
        token = single_symbol_token
        next_node_id = setup_node_edge_relationship(working_str, previous_node_id, offset, token)
        head_token_id_set.add(next_node_id)

    processed_working_str[working_str] = head_token_id_set


def setup_node_edge_relationship(working_str, previous_node_id, offset, token):
    len_of_token = len(token)

    next_offset = offset + len_of_token
    next_working_str = working_str[len_of_token:]

    # always treat single char as symbol
    current_node_id = "{}-{}".format(offset, next_offset)
    dot.node(current_node_id, token)
    dot.edge(previous_node_id, current_node_id)

    # continue process remained string
    create_node_from_string(next_working_str, current_node_id, next_offset)
    return current_node_id


create_node_from_string(example, start_node_id, 0)

dot.render('test-output/round-table.gv', view=True)
