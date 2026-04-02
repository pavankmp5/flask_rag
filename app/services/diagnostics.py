import os


def get_runtime_stats():
    return {
        "mode": "llm_only",
        "knowledge_rows": 0,
        "indexed_chunks": 0,
        "files": {
            "llm_only": True,
        },
        "features": {
            "chat": True,
            "search": True,
            "citations": False,
            "vector_index": False,
            "local_knowledge_base": False,
        },
        "provider": {
            "base_url": os.getenv("OPENAI_BASE_URL", ""),
            "chat_model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        },
    }
