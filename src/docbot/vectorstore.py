# -*- coding: utf-8 -*-
"""
    docbot.vectorstore
    ~~~~~~~~~~~~~~~~~~

    Vector store - Pinecone

    :copyright: © 2024 by Jiri
"""
import logging

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from docbot.config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
from docbot.constants import EMBEDDING_MODEL, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)


db_vcs = PineconeVectorStore(index_name=PINECONE_INDEX_NAME, pinecone_api_key=PINECONE_API_KEY, embedding=embeddings)

retriever = db_vcs.as_retriever()


if __name__ == '__main__':
    import pandas as pd
    df = pd.read_csv("/home/jirka/Downloads/Store_Public_Actor_Issues_for_AI_2024_11_28.csv")
    aggregated_issues = [row.values[1].replace("=>", "\n") for _, row in df.iterrows()]
    db_vcs.add_texts(aggregated_issues, embedding_chunk_size=2000)
