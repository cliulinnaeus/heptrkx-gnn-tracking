from heptrkx import master
from heptrkx.preprocess.utils_mldata import read
from heptrkx.nx_graph.utils_data import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from pandas import DataFrame
from collections import namedtuple
import numpy as np
import networkx as nx
from heptrkx.nx_graph.utils_plot import *
# from graph_nets import utils_np
# import graph_nets as gn

dir = '../sample_data'
evtid = 21000



hits, particles, truth, cells = read(dir, evtid)



table = merge_truth_info_to_hits(hits, particles, truth)


tracks = []
for i in table['particle_id'][0:10]:
    track = table.loc[table['particle_id'] == i]
    tracks.append(track)
# print(tracks)               # tracks is an array of particles, which is an array containing different hits

# sort by r:
for track in tracks:
    track.sort_values(by=['r'])

# build graph:
G = nx.Graph()
for track in tracks:
    start = True            # a flag to indicate the start of a track
    for row in track.iterrows():
        


        # add node from the graph to 
        hit_id = row[1]['hit_id']
        r = row[1]['r']
        phi = row[1]['phi']
        z = row[1]['z']
        p_id = row[1]['particle_id']
        G.add_node(row[1]['hit_id'], pos=[r, phi, z], particld_id=p_id)

        if start:
            start = False
            # print('hi')
        else:
            G.add_edge(prevnode, hit_id, solution=[1])
        prevnode = hit_id

# plot_networkx(G)

# print(G.number_of_nodes())
# print(G.number_of_edges())

# split into four phi bins:

# print(G.nodes(data=True))
phi1_nodes = [node[0] for node in G.nodes(data=True) if node[1]['pos'][1] >= 0 and node[1]['pos'][1] < np.pi/2]
phi2_nodes = [node[0] for node in G.nodes(data=True) if node[1]['pos'][1] >= np.pi/2 and node[1]['pos'][1] < np.pi]
phi3_nodes = [node[0] for node in G.nodes(data=True) if node[1]['pos'][1] >= -np.pi/2 and node[1]['pos'][1] < 0]
phi4_nodes = [node[0] for node in G.nodes(data=True) if node[1]['pos'][1] >= -np.pi and node[1]['pos'][1] < -np.pi/2]
print(phi1_nodes)
G_phi1 = nx.subgraph(G, phi1_nodes)
G_phi2 = nx.subgraph(G, phi2_nodes)
G_phi3 = nx.subgraph(G, phi3_nodes)
G_phi4 = nx.subgraph(G, phi4_nodes)


# every track should have some
# print(G_phi1.number_of_nodes() + G_phi2.number_of_nodes() + G_phi3.number_of_nodes() + G_phi4.number_of_nodes())

# G1 and G2 must be tracks
def from_same_track(G1, G2):
    n1 = 0
    n2 = 0
    for node in G1.nodes(data=True):
        n1 = node
        break
    for node in G2.nodes(data=True):
        n2 = node
        break
    
    return n1[0] == n2[0]



# track_segments is a list of list of graph segments that should be connected together
# G1, G2 are graphs:
def find_connected_components(G1, G2):
    track_segments = []
    for i in nx.connected_components(G1):
        ts = [i]
    
        for j in nx.connected_components(G2):
            if from_same_track(i, j):
                ts.append(j)
        track_segments.append(ts)
    return track_segments

graph_list = [G_phi1, G_phi2, G_phi3, G_phi4]

every_segmented_components = []
i = 0
while i < 4:
    j = i
    while j < 4:
        t = find_connected_components(graph_list[i], graph_list[j])
        every_segmented_components.extend(t)
        j += 1
    i += 1

print(every_segmented_components)


