import pandas as pd
from langchain_text_splitters import TokenTextSplitter

from ...utils import generate_sha256_hash


def embbed_description(description_nodes):
    text_splitter = TokenTextSplitter(chunk_size=50, chunk_overlap=5)
    sub_df_list = []
    for name, text in description_nodes.items():
        texts = text_splitter.split_text(text)
        text_ids = [f"{name}_{i}" for i in range(len(texts))]
        chunk_ids = [generate_sha256_hash(x) for x in texts]
        sub_df_list.append(
            pd.DataFrame(
                zip(text_ids, texts, chunk_ids), columns=["unique_id", "chunck", "chunck_id"]
            )
        )
    text_df = pd.concat(sub_df_list)
    return text_df
