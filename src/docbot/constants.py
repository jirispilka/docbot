# -*- coding: utf-8 -*-
"""
    docbot.constants
    ~~~~~~~~~~~~~~~~

    Constants for the project.

    :copyright: © 2024 by Jiri
"""

from langchain_core.prompts import PromptTemplate

from docbot.schemas import ConfigOpenAIModels

# EMBEDDINGS / VECTOR STORE
VECTOR_STORE_DB_NAME = "apify-doc-platform"
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 500  # chunk_size in tokens, using max value (determined by sentence transformer model)
CHUNK_OVERLAP = 100  # chunk overlap in tokens

# UI
UI_SEARCH_DEFAULT_K = 5

# LOGGING
LOGGER_NAME = "docbot"
DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"

# LLM
LLM_MODEL_DEFAULT = ConfigOpenAIModels(class_="OpenAI", model="gpt-3.5-turbo", context_window_tokens=16385)

RETRIEVER_TOP_K = 5  # get top_k results from vector store
RETRIEVER_SEARCH_TYPE = "similarity"  # similarity or similarity_with_score
OPENAI_TIMEOUT = 10
CONTEXT_MAX_TOKENS = RETRIEVER_TOP_K * CHUNK_SIZE
CONTEXT_BUFFER_METADATA = CHUNK_SIZE

# We need to keep sufficient chat history, but it does not make sense to keep it extremely long because of $$$
# Short answer - 40 tokens, long answer 200 tokens -> support around 5 long message at max.
CHAT_HISTORY_MAX_TOKENS = 1200

# basic prompt for RAG (not used for the final application)
RAG_PROMPT_BASIC = PromptTemplate.from_template(
    template="""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences at maximum and keep the answer short and concise.

    {context}

    Question: {question}

    Helpful Answer:"""
)

# prompt without source citation
RAG_PROMPT_0 = PromptTemplate.from_template(
    template="""
    You are smart and helpful assistant for the Apify Platform Documentation (referred as documentation).
    You have great knowledge about Apify and always answer as helpfully as possible.
    Given the chat history and the following pieces of context, answer the question at the end.
    Your answers should not include any harmful content.
    You can only answer questions about the Apify and Apify platform documentation.
    If a question does not make any sense ask for clarification.
    If you don't know the answer to a question do not answer it.

    Chat history: {chat_history}

    Context: {context}

    Question: {question}

    Helpful Answer:
    """
)

# prompt with source citation
RAG_PROMPT = PromptTemplate.from_template(
    template="""
    You are smart and helpful assistant for the Apify Platform Documentation (referred as documentation).
    You have extensive knowledge about Apify and always answer questions as helpfully as possible.

    Given the following context, answer the question at the end.
    Your responses should adhere to clarity and readability standards and must be devoid of any harmful content.
    You are limited to answering questions about the Apify and Apify's platform documentation.
    If a question is unclear or beyond the documentation scope yet relevant to Apify, offer general guidance where feasible.
    For questions beyond your knowledge, recommend next steps or resources rather than leaving the query unanswered.

    Remember, always include an URL to the source of the context in your responses, formatted in markdown as [Page title](url).

    Context: {context}

    Question: {question}

    Helpful Answer:
    """
)

PROMPT_STANDALONE_QUESTION = PromptTemplate.from_template(
    template="""Given the following conversation, decide whether the user utterance is a statement, standalone
    question, or a follow up question.
    If the utterance is statement or standalone question, just repeat it.
    If the question is a follow up, rephrase it as a standalone question, in its original
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:
"""
)

PROMPT_WELCOME = """**Welcome to the Apify's Platform documentation Assistant!** Just type your question below for detailed support on
the Apify Platform. \nWhat can I help you with?"""

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
    template="Page title: {title}, url: {url}, snippet: {page_content}"
)
RESPONSE_ERROR = "We are sorry, we are encountering difficulties providing an appropriate response. Please try again."
