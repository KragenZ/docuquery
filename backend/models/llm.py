import os
from langchain_openai import ChatOpenAI


def get_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        streaming=streaming,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
