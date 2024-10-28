import json

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from core.databases.kb.graph import create_networkx_graph, create_node
from core.databases.kb.ontology_utils import graph_to_turtle
from core.databases.vector_db.embeddings import embbed_description
from core.utils import generate_sha256_hash


def load_embeddings_model(lang):
    if lang == "en":
        emb_model = SentenceTransformer("all-mpnet-base-v2")
    else:
        raise NotImplementedError
    return emb_model


def create_vector_database(emb_model, text_df):
    chroma_client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="candidates_db",
        )
    )
    collection = chroma_client.create_collection(
        name="candidates_db", metadata={"hnsw:space": "cosine"}
    )
    embeddings = emb_model.encode(text_df.chunck.values)
    collection.add(
        embeddings=[list(x.astype("float")) for x in embeddings],
        ids=list(text_df.chunck_id.values),
        documents=list(text_df.chunck.values),
    )


def run(candidates_file_path="candidates.json", lang="en"):
    with open(candidates_file_path, "r") as file:
        data = json.load(file)

    emb_model = load_embeddings_model(lang)
    nodes_types = {}
    for candidate_data in data:
        _, nodes_types = create_node(candidate_data, nodes_types)
    nodes_attributes = {str(node): {"type": node_type} for node, node_type in nodes_types.items()}
    nodes_id = {x: generate_sha256_hash(x) for x, v in nodes_types.items() if v != "description"}
    description_nodes = {
        f"{data[i]["first_name"]}_{data[i]["last_name"]}": data[i]["description"]
        for i in range(len(data))
        if "description" in data[i].keys()
    }
    text_df = embbed_description(description_nodes)
    create_vector_database(emb_model, text_df)
    G = create_networkx_graph(nodes_types, nodes_attributes, data, text_df)
    graph_to_turtle(G, nodes_id, output_file="candidates_turtles.ttl")
    return 1


if __name__ == "__main__":
    output_code = run("candidates.json")
    if output_code == 1:
        print("[DEV] - End preprocessing, Databases created")
