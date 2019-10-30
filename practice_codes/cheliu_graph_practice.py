import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

G = nx.Graph()
G.add_node(1)
G.add_node(2)
G.add_node(3)
H = nx.DiGraph(G)
# G.add_nodes_from(H)
# G.add_edge(0,2)
G.add_edges_from(H.edges)
G.add_nodes_from("heii")
# print(G.degree)
print(G.degree([2, 0]))


plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
nx.draw(H, with_labels=True, font_weight='bold')
# plt.subplot(122)
# nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')

plt.show()

# file_path = '../../event000021000-particles.csv.gz'
# data = pd.read_csv(file_path, nrows=100, compression='gzip',
#                    error_bad_lines=False)
# print(data)