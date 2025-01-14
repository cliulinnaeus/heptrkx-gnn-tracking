"""
convert hitgraphs to network-x and prepare graphs for graph-nets
"""
import numpy as np
from datasets.graph import load_graph
import networkx as nx

import os
import glob
import re

def calc_dphi(phi1, phi2):
    """Computes phi2-phi1 given in range [-pi,pi]"""
    dphi = phi2 - phi1
    if dphi > np.pi:
        dphi -= 2*np.pi
    if dphi < -np.pi:
        dphi += 2*np.pi
    return dphi

def get_edge_features(in_node, out_node):
    # input are the features of incoming and outgoing nodes
    # they are ordered as [r, phi, z]
    in_r, in_phi, in_z    = in_node
    out_r, out_phi, out_z = out_node

    in_r3 = np.sqrt(in_r**2 + in_z**2)
    out_r3 = np.sqrt(out_r**2 + out_z**2)

    in_theta = np.arccos(in_z/in_r3)
    in_eta = -np.log(np.tan(in_theta/2.0))
    out_theta = np.arccos(out_z/out_r3)
    out_eta = -np.log(np.tan(out_theta/2.0))
    deta = out_eta - in_eta
    dphi = calc_dphi(out_phi, in_phi)
    dR = np.sqrt(deta**2 + dphi**2)
    dZ = in_z - out_z
    return np.array([deta, dphi, dR, dZ])


def hitsgraph_to_networkx_graph(G):
    n_nodes, n_edges = G.Ri.shape

    graph = nx.DiGraph()

    ## add nodes
    for i in range(n_nodes):
        graph.add_node(i, pos=G.X[i], solution=0.0)

    for iedge in range(n_edges):
        in_node_id  = G.Ri[:, iedge].nonzero()[0][0]
        out_node_id = G.Ro[:, iedge].nonzero()[0][0]

        # distance as features
        in_node_features  = G.X[in_node_id]
        out_node_features = G.X[out_node_id]
        distance = get_edge_features(in_node_features, out_node_features)
        # add edges, bi-directions
        graph.add_edge(in_node_id, out_node_id, distance=distance, solution=G.y[iedge])
        graph.add_edge(out_node_id, in_node_id, distance=distance, solution=G.y[iedge])
        # add "solution" to nodes
        graph.node[in_node_id].update(solution=G.y[iedge])
        graph.node[out_node_id].update(solution=G.y[iedge])

    # add global features, not used for now
    graph.graph['features'] = np.array([0.])
    return graph


def graph_to_input_target(graph):
    def create_feature(attr, fields):
        return np.hstack([np.array(attr[field], dtype=float) for field in fields])

    input_node_fields = ("pos",)
    input_edge_fields = ("distance",)
    target_node_fields = ("solution",)
    target_edge_fields = ("solution",)

    input_graph = graph.copy()
    target_graph = graph.copy()

    for node_index, node_feature in graph.nodes(data=True):
        input_graph.add_node(
            node_index, features=create_feature(node_feature, input_node_fields)
        )
        target_graph.add_node(
            node_index, features=create_feature(node_feature, target_node_fields)
        )

    for receiver, sender, features in graph.edges(data=True):
        input_graph.add_edge(
            sender, receiver, features=create_feature(features, input_edge_fields)
        )
        target_graph.add_edge(
            sender, receiver, features=create_feature(features, target_edge_fields)
        )

    input_graph.graph['features'] = input_graph.graph['features'] = np.array([0.0])
    return input_graph, target_graph


def inputs_generator(base_dir_, n_train_fraction=-1):
    base_dir = base_dir_

    file_patten = base_dir.format(1000, 0).replace('1000', '*')
    all_files = glob.glob(file_patten)
    n_events = len(all_files)
    evt_ids = [int(re.search('event00000([0-9]*)_g000.npz', os.path.basename(x)).group(1))
               for x in all_files]

    section_patten = base_dir.format(1000, 0).replace('_g000', '_g[0-9]*[0-9]*[0-9]')
    n_sections = len(glob.glob(section_patten))
    n_total = n_events*n_sections

    n_tr_fr = n_train_fraction if n_train_fraction > 0 else 0.7
    n_max_evt_id_tr = int(n_events * n_tr_fr)
    n_test = n_events - n_max_evt_id_tr

    print("Total Events: {} with {} sections, total {} files ".format(
        n_events, n_sections, n_total))
    print("Training data: [{}, {}] events, total {} files".format(0, n_max_evt_id_tr-1, n_max_evt_id_tr*n_sections))
    print("Testing data:  [{}, {}] events, total {} files".format(n_max_evt_id_tr, n_events, n_test*n_sections))


    # keep track of training events
    global _evt_id_tr_
    _evt_id_tr_ = 0
    global _sec_id_tr_
    _sec_id_tr_ = 0
    ## keep track of testing events
    global _evt_id_te_
    _evt_id_te_ = n_max_evt_id_tr
    global _sec_id_te_
    _sec_id_te_ = 0

    def generate_input_target(n_graphs, is_train=True):
        global _evt_id_tr_
        global _sec_id_tr_
        global _evt_id_te_
        global _sec_id_te_
        input_graphs = []
        target_graphs = []
        igraphs = 0
        while igraphs < n_graphs:
            # determine while file to read
            if is_train:
                file_name = base_dir.format(evt_ids[_evt_id_tr_], _sec_id_tr_)
                _sec_id_tr_ += 1
                if _sec_id_tr_ == n_sections:
                    _evt_id_tr_ += 1
                    _sec_id_tr_ = 0
                    if _evt_id_tr_ >= n_max_evt_id_tr:
                        _evt_id_tr_ = 0
            else:
                file_name = base_dir.format(evt_ids[_evt_id_te_], _sec_id_te_)
                _sec_id_te_ += 1
                if _sec_id_te_ == n_sections:
                    _evt_id_te_ += 1
                    _sec_id_te_ = 0
                    if _evt_id_te_ >= n_events:
                        _evt_id_te_ = n_max_evt_id_tr


            graph = hitsgraph_to_networkx_graph(load_graph(file_name))
            input_graph, output_graph = graph_to_input_target(graph)
            input_graphs.append(input_graph)
            target_graphs.append(output_graph)
            igraphs += 1

        return input_graphs, target_graphs

    return generate_input_target
