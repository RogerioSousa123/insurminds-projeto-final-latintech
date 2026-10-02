from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ChatResult:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


class ChatProvider(Protocol):
    model_name: str

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult: ...

