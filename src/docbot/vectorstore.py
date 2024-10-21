# -*- coding: utf-8 -*-
"""
    docbot.vectorstore
    ~~~~~~~~~~~~~~~~~~

    Vector store - Pinecone

    :copyright: © 2024 by Jiri
"""
import logging

from langchain_openai.embeddings import OpenAIEmbeddings

from docbot.config import OPENAI_API_KEY, _config
from docbot.constants import EMBEDDING_MODEL, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)

if _config.DATABASE == "PINECONE":
    from langchain_pinecone import PineconeVectorStore

    db_vcs = PineconeVectorStore(index_name=_config.PINECONE_INDEX_NAME, pinecone_api_key=_config.PINECONE_API_KEY, embedding=embeddings)

elif _config.DATABASE == "OPENSEARCH":
    from langchain_community.vectorstores import OpenSearchVectorSearch
    from opensearchpy import RequestsHttpConnection
    from requests_aws4auth import AWS4Auth  # type: ignore

    name = _config.AWS_SERVICE_NAME
    name = name if isinstance(name, str) else name.value

    if _config.AWS4_AUTH:
        awsauth = AWS4Auth(
            _config.AWS_ACCESS_KEY_ID.get_secret_value(),
            _config.AWS_SECRET_ACCESS_KEY.get_secret_value(),
            _config.AWS_REGION,
            _config.AWS_SERVICE_NAME
        )
    else:
        awsauth = None

    db_vcs = OpenSearchVectorSearch(
        connection_class=RequestsHttpConnection,
        embedding_function=embeddings,
        http_auth=awsauth,
        http_compress=True,
        index_name=_config.OPENSEARCH_INDEX_NAME,
        opensearch_url=_config.OPENSEARCH_URL,
        use_ssl=_config.AWS_USE_SSL,
        verify_certs=_config.AWS_VERIFY_CERTS,
    )
else:
    raise ValueError("Unsupported database type")

retriever = db_vcs.as_retriever()
