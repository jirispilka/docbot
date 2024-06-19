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
