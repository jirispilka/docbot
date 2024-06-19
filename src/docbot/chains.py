# -*- coding: utf-8 -*-
"""
    docbot.chains
    ~~~~~~~~~~~~~

    LLM chains and utilities.

    :copyright: © 2024 by Jiri
"""
from operator import itemgetter
from typing import Generator

from dotenv import load_dotenv
from langchain.memory import ConversationTokenBufferMemory
from langchain_core.documents import Document
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, format_document
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI

from docbot.constants import (
    CHAT_HISTORY_MAX_TOKENS,
    CONTEXT_BUFFER_METADATA,
    CONTEXT_MAX_TOKENS,
    DEFAULT_DOCUMENT_PROMPT,
    LLM_MODEL_DEFAULT,
    OPENAI_TIMEOUT,
    PROMPT_STANDALONE_QUESTION,
    RAG_PROMPT,
    RETRIEVER_SEARCH_TYPE,
    RETRIEVER_TOP_K,
)


class RagChainHelper:

    """RAG chain with memory."""

    def __init__(
        self,
        model_name: str,
        temperature: float,
        max_token_limit: int,
        db: VectorStore,
        retriever_top_k: int = RETRIEVER_TOP_K,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_token_limit = max_token_limit

        self.llm = ChatOpenAI(
            streaming=True,
            model_name=model_name,
            temperature=temperature,
            request_timeout=OPENAI_TIMEOUT,
        )

        self.memory = ConversationTokenBufferMemory(
            llm=self.llm,
            return_messages=True,
            output_key="answer",
            input_key="question",
            max_token_limit=max_token_limit,
        )

        self.retriever = db.as_retriever(search_type=RETRIEVER_SEARCH_TYPE, search_kwargs={"k": retriever_top_k})
        self.chain = self.create_chain()

    @staticmethod
    def format_docs(
        docs: list[Document],
        document_prompt: PromptTemplate = DEFAULT_DOCUMENT_PROMPT,
        document_separator: str = "\n\n",
    ) -> str:
        """Format documents to str with fields as defined in the document prompt.

        For example: Page title, url, content.
        """
        doc_strings = [format_document(doc, document_prompt) for doc in docs]
        return document_separator.join(doc_strings)

    def get_prompt_tokens(self) -> int:
        return self.llm.get_num_tokens(self.chain.get_prompts().__str__())

    def get_max_query_tokens(self) -> int:
        """Calculates the maximum number of tokens for the user's query within LLM's context window.

        Compute the available token space by considering the LLM's input structure, which includes the system's prompt,
        user's query, chat history, and external context (Page content (chunk) Page titles and URL).
        To accommodate potential oversizing due to metadata, a buffer of N tokens is subtracted
        from the total available space. This ensures the overall input does not exceed the LLM's context window limit.
        """
        return (
            self.max_token_limit
            - CONTEXT_MAX_TOKENS
            - CHAT_HISTORY_MAX_TOKENS
            - self.get_prompt_tokens()
            - CONTEXT_BUFFER_METADATA
        )

    def create_chain(self) -> Runnable:
        """Setup and return RAG chain with memory.

        Source: Langchain doc: https://python.langchain.com/docs/expression_language/cookbook/retrieval
        """

        # This adds a "memory" key to the input object
        loaded_memory = RunnablePassthrough.assign(
            chat_history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"),
        )

        standalone_question = {
            "standalone_question": {
                "question": lambda x: x["question"],
                "chat_history": lambda x: get_buffer_string(x["chat_history"]),
            }
            | PROMPT_STANDALONE_QUESTION
            | self.llm
            | StrOutputParser(),
        }

        retrieved_documents = {
            "docs": itemgetter("standalone_question") | self.retriever,
            "question": lambda x: x["standalone_question"],
        }

        # construct the inputs for the final prompt
        final_inputs = {
            "context": lambda x: self.format_docs(x["docs"]),
            "question": itemgetter("question"),
            "chat_history": lambda x: get_buffer_string(x["chat_history"]),
        }

        answer = {
            "answer": final_inputs | RAG_PROMPT | self.llm,
            "docs": itemgetter("docs"),
            "standalone_question": itemgetter("question"),
        }
        # Put it all together
        return loaded_memory | standalone_question | retrieved_documents | loaded_memory | answer

    def stream_with_debug(self, q: str | dict, ctx: list) -> Generator:
        """Call chain and return generator for streaming purposes.

        The ctx is only for debugging purposes. It saves docs and standalone question for debugging.
        """
        for c in self.chain.stream(q):
            ctx.extend(c.get("docs")) if c.get("docs") else None
            ctx.append(c) if c.get("standalone_question") else None
            if s := c.get("answer"):
                yield s


if __name__ == "__main__":
    from langchain.globals import set_debug
    from docbot.vectorstore import db_vcs

    set_debug(True)
    load_dotenv()

    m = LLM_MODEL_DEFAULT
    rag = RagChainHelper(model_name=m.model_name, temperature=0, max_token_limit=m.context_window_tokens, db=db_vcs)
    inputs = {"question": "What is an Actor?"}
    result = rag.chain.invoke(inputs)
    print(result["answer"])
    rag.memory.save_context(inputs, {"answer": result["answer"].content})
    inputs = {"question": "How can I use it?"}
    result = rag.chain.invoke(inputs)
    print(result["answer"])
