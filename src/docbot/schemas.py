# -*- coding: utf-8 -*-
"""
    docbot.schema
    ~~~~~~~~~~~~~

    Models for internal data structures.

    :copyright: © 2024 by Jiri
"""
from typing import Literal

from pydantic import BaseModel, Field


class ConfigOpenAIModels(BaseModel):
    class_: Literal["OpenAI"]
    model_name: str = Field(..., alias="model")
    temperature: float = 0
    context_window_tokens: int
