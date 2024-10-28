import urllib.parse

from rdflib import RDF, Literal, Namespace, URIRef
from rdflib import Graph as RDFGraph
from rdflib.namespace import XSD

EX = Namespace("http://RH.org/")


def sanitize_for_uri(value):
    return urllib.parse.quote(
        value.replace(" ", "_").replace(",", "").replace(":", "").replace(".", "")
    )


def graph_to_turtle(input_graph, nodes_id, output_file="output.ttl"):
    rdf_graph = RDFGraph()
    rdf_graph.bind("ex", EX)
    for node, attributes in input_graph.nodes(data=True):
        if hasattr(attributes, "type") and attributes["type"] != "description":
            node_uri = URIRef(EX[sanitize_for_uri(node)])
            rdf_graph.add(
                (node_uri, EX[sanitize_for_uri("unique_id")], EX[sanitize_for_uri(nodes_id[node])])
            )
            if "type" in attributes:
                node_type = attributes["type"]
                rdf_graph.add((node_uri, RDF.type, EX[sanitize_for_uri(node_type)]))
            for attr_key, attr_value in attributes.items():
                if attr_key != "type":
                    rdf_graph.add(
                        (
                            node_uri,
                            EX[sanitize_for_uri(attr_key)],
                            Literal(attr_value, datatype=XSD.string),
                        )
                    )
    for node1, node2, attributes in input_graph.edges(data=True):
        node1_uri = URIRef(EX[sanitize_for_uri(node1)])
        node2_uri = URIRef(EX[sanitize_for_uri(node2)])
        for _, rel_value in attributes.items():
            rdf_graph.add((node1_uri, EX[sanitize_for_uri(rel_value)], node2_uri))
    rdf_graph.serialize(output_file, format="turtle")
    print(f"Turtle file '{output_file}' created successfully!")
