# -*- coding: utf-8 -*-
"""
    docbot.fe.retrival
    ~~~~~~~~~~~~~~~~~~

    Retrieve documents (vector search, BM25 search, filtering)

    :copyright: © 2024 by Jiri
"""

import pandas as pd
import streamlit as st
from langchain_core.documents import Document

from docbot.chains import RagChainHelper
from docbot.constants import LLM_MODEL_DEFAULT
from docbot.fe.config import UI_SEARCH_DEFAULT_K
from docbot.vectorstore import db_vcs, retriever


def main():
    st.title("Search")

    k, query = ui_search()
    generate_answer = st.checkbox("Generate answer")
    st.button("Search")

    st.subheader("Answer")
    answer_placeholder = st.empty()
    if generate_answer:
        try:
            m = LLM_MODEL_DEFAULT
            rag = RagChainHelper(
                model_name=m.model_name,
                temperature=0,
                max_token_limit=m.context_window_tokens,
                db=db_vcs,
                retriever_top_k=k,
            )
            v = rag.chain.invoke({"question": query})
            result = [(r, 0) for r in v.get("docs")]
            answer_placeholder.markdown(v["answer"].content)
        except Exception as e:
            st.error(e)
            st.stop()
    else:
        try:
            result: list[tuple[Document, float]] = retriever.vectorstore.similarity_search_with_relevance_scores(
                query, k=k
            )
        except Exception as e:
            st.error(e)
            st.stop()

    results = [
        {
            "content": r.page_content,
            "title": r.metadata.get("title"),
            "url": r.metadata.get("url"),
            "score": score,
        }
        for r, score in result
    ]

    st.subheader("Search results", help="Note that score is not available when `Generate answer` is enabled")
    if results:
        df = pd.DataFrame().from_records(results)
        st.table(df)


def ui_search():
    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Query", value="What is an Actor?")
    with c2:
        k = st.number_input("k", value=UI_SEARCH_DEFAULT_K)
    return k, query


if __name__ == "__main__":
    retriever_ = db_vcs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    res_: list[Document] = retriever_.invoke("What is an Actor?")
    print(res_)
