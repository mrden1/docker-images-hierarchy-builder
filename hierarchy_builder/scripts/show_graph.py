import matplotlib.pyplot as plt
import networkx as nx
from bokeh.palettes import Spectral


def visualize_graphs(graph, node_count):
    pos = nx.circular_layout(graph)
    options = {
        'node_color': Spectral[node_count],
        'node_size': 3000,
        'width': 1,
        'arrowstyle': '-|>',
        'arrowsize': 30,
        'edge_color': 'gray',
        'node_shape': 'o'
    }
    nx.draw(graph, pos, with_labels=True, **options)
    ax = plt.gca()
    ax.collections[0].set_edgecolor("#3E3838")
    plt.show()
