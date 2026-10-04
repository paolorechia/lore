from typing import Protocol

class ProviderProtocol(Protocol):
    def generate(self, prompt: str) -> str:
        ...
