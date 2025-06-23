import networkx as nx


def get_lines_for_graph(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        return lines


def generate_nodes(lines):
    nodes = []
    for l in lines:
        l = l.rstrip("\n").split(" ")
        nodes = nodes + l
    nodes = list(set(nodes))
    return nodes


def generate_edges(lines):
    edges = []
    for l in lines:
        l = l.rstrip("\n").split(" ")
        if len(l) < 2:
            continue
        for counter, _ in enumerate(l):
            if counter < len(l) - 1:
                new_el = (l[counter], l[counter+1])
                if new_el not in edges:
                    edges.append(new_el)
    return edges


def build_graph(path):
    lines = get_lines_for_graph(path)
    nodes = generate_nodes(lines)
    edges = generate_edges(lines)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G, nodes
