# -*- coding: utf-8 -*-
"""
    docbot.fe.config
    ~~~~~~~~~~~~~~~~

    Streamlit app config.

    :copyright: © 2024 by Jiri
"""

from enum import Enum

UI_SEARCH_DEFAULT_K = 5


class Config(str, Enum):
    selected_tool = "selected_tool"


class Tools(Enum):
    chat = "Chat"
    retrival = "Search"

    @staticmethod
    def get_tool_by_value(val: str) -> str | None:
        return next((x.name for x in Tools if x.value == val), None)
