import copy

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from ...utils import generate_sha256_hash

useless_semantic_features = ["first_name", "last_name", "email", "phone"]


def create_node(data, nodes_types):
    """
    Format nodes in the required format to create
    links with label in networkx
    Args:
        data (dict): candidates data
        nodes_types (dict): dictionary {node:node_type}

    Returns:
        tuple: list of nodes name,dictionary {node:node_type}
    """
    try:
        person = f"{data["first_name"]}_{data["last_name"]}"
        nodes_types.update({person: "person"})
        for key, val in data.items():
            if key not in useless_semantic_features:
                if key == "description":
                    nodes_types.update({str(generate_sha256_hash(val)): str(key)})
                elif isinstance(val, str) or isinstance(val, int):
                    nodes_types.update({str(val): str(key)})
                elif key == "skills":
                    for skill in val:
                        nodes_types.update({str(skill): str(key)})
                else:
                    for experiences in val:
                        for key, val in experiences.items():
                            nodes_types.update({str(val): str(key)})
    except Exception as e:
        print(data, e)
    return nodes_types.keys(), nodes_types


def create_networkx_graph(nodes_types, nodes_attributes, data, text_df):
    """
    Create networkx graph with labeled links

    Args:
        nodes_types (dict): _description_
        nodes_attributes (dict): _description_
        data (dict): candidates data
        text_df (pandas Dataframe): dataframe of Candidates description chuncks

    Returns:
        Direct Networkx graph: Candidate Graph
    """

    G = nx.DiGraph()
    G.add_nodes_from(nodes_types.keys())
    nx.set_node_attributes(G, nodes_attributes)
    for candidate_id, candidate in enumerate(data):
        try:
            person = f"{candidate["first_name"]}_{candidate["last_name"]}"
            G.add_edge(person, str(candidate["age"]), relation="isAged")
            G.add_edge(person, candidate["address"], relation="livesAt")
            for deg in candidate["education"]:
                G.add_edge(person, deg["degree"], relation="holdsDegree")
                G.add_edge(person, deg["institution"], relation="gradutedFrom")
                G.add_edge(person, str(deg["year_of_graduation"]), relation="graduated in")
            for exp in candidate["experiences"]:
                G.add_edge(person, exp["company"], relation="workedAt")
                G.add_edge(person, exp["role"], relation="workedAs")
            for skill in candidate["skills"]:
                G.add_edge(person, skill, relation="expertiseIn")
        except Exception as e:
            print(e, candidate)
    for i, row in text_df.iterrows():
        ids = row["unique_id"].split("_")
        person = f"{ids[0]}_{ids[1]}"
        G.add_edge(person, row["chunck_id"], relation="description")
    return G


def plot_graph(G):

    pos = nx.spring_layout(G, iterations=20)

    pos_shadow = copy.deepcopy(pos)
    shift_amount = 0.006
    for idx in pos_shadow:
        pos_shadow[idx][0] += shift_amount
        pos_shadow[idx][1] -= shift_amount

        edges = G.edges(data=True)
    labels = {(u, v): d["relation"] for u, v, d in edges}

    node_types = nx.get_node_attributes(G, "type")
    unique_types = set(node_types.values())
    color_map = {
        node_type: plt.cm.get_cmap("Set3")(i / len(unique_types))
        for i, node_type in enumerate(unique_types)
    }

    default_color = "lightgray"
    node_colors = [
        color_map[node_types[node]] if node in node_types else default_color for node in G.nodes()
    ]

    fig = plt.figure(figsize=(20, 20), frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    nx.draw(
        G,
        pos,
        with_labels=False,
        node_color=node_colors,
        font_size=8,
        node_size=500,
        edge_color="gray",
    )

    nx.draw_networkx_labels(G, pos_shadow, font_color="blue")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color="red")
    legend_patches = [
        Patch(color=color_map[node_type], label=node_type) for node_type in unique_types
    ]
    plt.legend(handles=legend_patches, title="Node Types", loc="upper right")
    plt.show()
