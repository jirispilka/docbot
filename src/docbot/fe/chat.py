# -*- coding: utf-8 -*-
"""
    docbot.fe.chat
    ~~~~~~~~~~~~~~

    Chat with documentation.

    :copyright: © 2024 by Jiri
"""
import logging

import streamlit as st
from langchain.memory import StreamlitChatMessageHistory
from langchain_core.documents import Document

from docbot.chains import RagChainHelper
from docbot.constants import (
    LLM_MODEL_DEFAULT,
    LOGGER_NAME,
    PROMPT_WELCOME,
    RESPONSE_ERROR,
)
from docbot.vectorstore import db_vcs

logger = logging.getLogger(LOGGER_NAME)


def init_app(model_name: str, temperature: float, max_token_limit: int):
    if not all(x in st.session_state for x in ("rag", "st_memory", "debug_info")):
        rag = RagChainHelper(model_name, temperature, max_token_limit, db_vcs)
        st.session_state.rag = rag

        st.session_state.rag.memory.chat_memory.add_ai_message(PROMPT_WELCOME)

        # We are using two types of memory, one RAG internal for LLM and one for ST.
        st.session_state.st_memory = StreamlitChatMessageHistory(key="langchain_messages")
        st.session_state.st_memory.add_ai_message(PROMPT_WELCOME)

        st.session_state.max_query_tokens = rag.get_max_query_tokens()
        st.session_state.debug_info = []


def clear_app_session(clear: bool = False):
    if clear:
        st.session_state.rag.memory.clear()
        st.session_state.st_memory.clear()
        st.session_state.rag.memory.chat_memory.add_ai_message(PROMPT_WELCOME)
        st.session_state.st_memory.add_ai_message(PROMPT_WELCOME)
        st.session_state.debug_info = []


def ui_settings():
    with st.expander("Settings"):
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.selectbox("System prompt", options=["Default"])
        with c2:
            m = st.text_input("Model name", value=LLM_MODEL_DEFAULT.model_name)
        with c3:
            temperature = st.number_input("Temperature", value=0.0, step=0.1, min_value=0.0, max_value=2.0)
        with c4:
            max_token_limit = st.number_input("Context window", value=LLM_MODEL_DEFAULT.context_window_tokens)

        show_prompt = st.checkbox("Show prompt")
        debug_context = st.checkbox("Show debug window with context", value=True)

        return m, temperature, max_token_limit, show_prompt, debug_context


def main():
    st.title("Chat with Apify's documentation")
    model_name, temperature, max_token_limit, show_prompt, debug_enabled = ui_settings()

    init_app(model_name, temperature, max_token_limit)
    if st.button("Clear session"):
        clear_app_session(clear=True)

    show_prompt and st.write(st.session_state.rag.chain.get_prompts())

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Chatbot")
        for message in st.session_state.st_memory.messages:
            with st.chat_message(message.type):
                st.markdown(message.content)

    if query := st.chat_input("Type your message"):
        with c1:
            context, response = handle_chat_message(query)

        if debug_enabled:
            with c2:
                ui_debug(query, response, context)


def handle_chat_message(query: str):
    """Check that query is valid and call RAG chain."""

    memory_st = st.session_state.st_memory
    rag: RagChainHelper = st.session_state.rag

    with st.chat_message("user"):
        if rag.llm.get_num_tokens(query) > st.session_state.max_query_tokens:
            st.error("Your query is too long, exceeding LLM context window limit, please rephrase")
            st.stop()
        memory_st.add_user_message(query)
        st.markdown(query)
    with st.chat_message("assistant"):
        context: list[dict] = []
        response: str = ""
        msg_placeholder = st.empty()
        # noinspection PyBroadException
        try:
            inputs = {"question": query}
            response = msg_placeholder.write_stream(rag.stream_with_debug(inputs, context))
            memory_st.add_ai_message(response)
            rag.memory.save_context(inputs, {"answer": response})
        except Exception as e:
            logger.error("Error occurred when calling chain: %s", e)
            msg_placeholder.markdown(f"{response} \n\n {RESPONSE_ERROR}")
    return context, response


def ui_debug(query: str, answer: str, context: list[Document] | list[dict]) -> None:
    """Debug component showing retrieved chunks."""

    if not context:
        return

    md = "\n\n".join(
        f"**title**: {d.metadata.get('title')}\n\n"
        f"**url**:{d.metadata.get('url')}\n\n"
        f"**content**:{d.page_content}"
        f"\n\n--------------------------------\n\n"
        for d in context
        if isinstance(d, Document)
    )

    standalone_question = "".join(
        d.get("standalone_question") for d in context if isinstance(d, dict) and d.get("standalone_question")
    )
    st.session_state.debug_info.append(
        {
            "user": query,
            "assistant": answer,
            "context_md": md,
            "standalone_question": standalone_question,
        }
    )

    for i, msg in enumerate(st.session_state.debug_info):
        expanded = i == len(st.session_state.debug_info)
        with st.expander(
            label=f"{msg.get('user')} / {msg.get('standalone_question')}",
            expanded=expanded,
        ):
            st.write(msg.get("context_md"))
