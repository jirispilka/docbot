# -*- coding: utf-8 -*-
"""
    docbot.fe.main
    ~~~~~~~~~~~~~~

    Main Streamlit app file.

    :copyright: © 2024 by Jiri
"""

import importlib

import streamlit as st

from docbot.config import load_dotenv_validate
from docbot.fe.config import Tools

load_dotenv_validate()


TOOLS = [c.value for c in Tools]

# build the sidebar with settings
st.set_page_config(layout="wide", page_title="Docbot", page_icon="books")
selected_tool = st.sidebar.selectbox(label="Select a tool:", options=TOOLS, index=0)

# run the selected tool
try:
    i_tool = importlib.import_module(f"docbot.fe.{Tools.get_tool_by_value(selected_tool)}")
except ModuleNotFoundError as e:
    i_tool = None
    st.error(f"Please choose a valid tool. {e}")
    st.stop()

i_tool.main()
