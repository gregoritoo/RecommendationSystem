import json

import pandas as pd
import streamlit as st
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from core.databases.kb.query_factory import (
    generate_skills_requirement_request,
    load_ontology,
    query_graph,
)
from core.streamlit.utils import (
    add_line,
    format_request,
    format_text,
    main_page_streamlit,
)
from core.utils import flatten_list

PAGES = {
    "Jobs": 1,
}

PATH_DATASET = "candidates_db"

COLORS = ["green", "blue", "grey"]


@st.cache_resource
def load_vector_db():
    chroma_client = Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="candidates_db",
        )
    )
    collection = chroma_client.get_collection(name="candidates_db")
    emb_model = SentenceTransformer("all-mpnet-base-v2")
    return collection, emb_model


def query(req, relation="expertiseIn"):
    skill_request = generate_skills_requirement_request([req], relation=relation)
    out_req = flatten_list(query_graph(rdf_graph, skill_request))
    return out_req


def get_top_candidates_by_skill(dic_person_skill, skill):
    out_req = query(skill)
    for person in out_req:
        if person in dic_person_skill.keys():
            dic_person_skill[person]["skills"] += [skill]
        else:
            dic_person_skill.update({person: {"skills": [skill]}})
    return dic_person_skill


def get_top_candidates_by_job_requirements(dic_person_skill, job):
    out_jobs = query(job, relation="workedAs")
    for person in out_jobs:
        if person in dic_person_skill.keys() and "jobs" in dic_person_skill[person]:
            dic_person_skill[person]["jobs"] += [job]
        elif person in person in dic_person_skill.keys():
            dic_person_skill[person].update({"jobs": [job]})
        else:
            dic_person_skill.update({person: {"jobs": [job]}})
    return dic_person_skill


def get_top_candidates_by_chunck(dic_person_skill, chunck, doc):
    out_jobs = query(chunck, relation="description")
    for person in out_jobs:
        if person in dic_person_skill.keys() and "description" in dic_person_skill[person]:
            dic_person_skill[person]["description"] += [doc]
        elif person in person in dic_person_skill.keys():
            dic_person_skill[person].update({"description": [doc]})
        else:
            dic_person_skill.update({person: {"description": [doc]}})
    return dic_person_skill


if __name__ == "__main__":
    with open("job.json", "r") as file:
        data = json.load(file)
    rdf_graph = load_ontology("candidates_turtles.ttl")
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    collection, emb_model = load_vector_db()

    if page == 1:
        options_skill, options_skill_more, options_exp, options_exp_add, options_text = (
            main_page_streamlit(data)
        )
        if st.button("Send request", use_container_width=True):
            dic_person_skill = {}
            for skill in format_request(options_skill, options_skill_more):
                dic_person_skill = get_top_candidates_by_skill(dic_person_skill, skill)

            for job in format_request(options_exp, options_exp_add):
                if len(job) > 0:
                    dic_person_skill = get_top_candidates_by_job_requirements(dic_person_skill, job)
            dic_person_skill = {
                k: v
                for k, v in sorted(dic_person_skill.items(), key=lambda x: len(x[1]), reverse=True)
            }

            results = collection.query(
                query_embeddings=emb_model.encode(options_text).reshape(-1).tolist(),
                n_results=10,
            )
            output_df = pd.DataFrame(
                zip(results["ids"][0], results["distances"][0], results["documents"][0]),
                columns=["chunck_id", "Distance", "Documents"],
            )
            output_df = output_df[output_df["Distance"] < 0.5]
            for chunck, doc in zip(output_df.chunck_id.values, output_df.Documents.values):
                dic_person_skill = get_top_candidates_by_chunck(dic_person_skill, chunck, doc)

            st.title("Best Candidates")
            for person in dic_person_skill.keys():
                st.write("#### " + person.replace("http://RH.org/", "").replace("_", " "))
                string_skills = ""
                for i, property in enumerate(["skills", "jobs", "description"]):
                    if property in dic_person_skill[person].keys():
                        string_skills = format_text(
                            dic_person_skill,
                            string_skills,
                            key=property,
                            color=COLORS[i],
                            person=person,
                        )
                st.markdown(string_skills)

                add_line()
