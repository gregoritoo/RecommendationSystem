from rdflib import Graph


def load_ontology(turtle_file):
    """
    Load ontology graph

    Args:
        turtle_file (str): path to turtle file

    Returns:
        rdf graph: ontology graph
    """
    rdf_graph = Graph()
    rdf_graph.parse(turtle_file, format="turtle")
    return rdf_graph


def query_graph(rdf_graph, query):
    """
    Query rdf graph according to request

    Args:
        rdf_graph (rdf graph): ontology graph
        query (str): query

    Returns:
        list: list of matches
    """
    results = rdf_graph.query(query)
    results_ = []
    for row in results:
        string_to_print = ""
        interm_line = []
        for key in row.labels:
            string_to_print += f"  {key}: {row[key]}"
            interm_line.append(row[key])
        results_.append(interm_line)
    return results_


def generate_job_requirement_request(jobs):
    job_generator = "\n".join([f"?person ex:workedAs ?job_{i} ." for i in range(len(jobs))])
    filter_clause = " && ".join(
        [
            f'CONTAINS(LCASE(STRAFTER(STR(?job_{i}), "/")), "{job.lower().replace(" ", "_")}")'
            for i, job in enumerate(jobs)
        ]
    )

    query_previous_jobs = f"""
    PREFIX ex: <http://RH.org/>

    SELECT DISTINCT ?person
    WHERE {{
        ?person a ex:person .
        {job_generator}
        FILTER({filter_clause})
    }}
    """  # {' '.join([f'?job_{i}' for i in range(len(jobs))])}
    return query_previous_jobs


def generate_skills_requirement_request(skills, relation="expertiseIn"):
    job_generator = "\n".join(
        [f"?person ex:{relation} ?skill_{i} .".format(relation) for i in range(len(skills))]
    )

    filter_clause = " && ".join(
        [
            f'STRENDS(LCASE(STR(?skill_{i})), "{job.lower().replace(" ", "_")}")'  # f'CONTAINS(LCASE(STRAFTER(STR(?skill_{i}), "/")), "{job.lower().replace(" ", "_")}")'
            for i, job in enumerate(skills)
        ]
    )

    query_previous_jobs = f"""
    PREFIX ex: <http://RH.org/>

    SELECT DISTINCT ?person 
    WHERE {{
        {job_generator}
        FILTER({filter_clause})
    }}
    """
    # {' '.join([f'?skill_{i}' for i in range(len(skills))])}
    return query_previous_jobs
