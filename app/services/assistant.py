import re

from app.services.llm import generate_response

GREETINGS = {"hi", "hello", "hey", "hiya", "namaste"}
UNSUPPORTED_REPLY = "I don't know."


def normalize_words(text):
    return re.findall(r"[a-zA-Z]+", text.lower())


def is_greeting(query):
    words = set(normalize_words(query))
    return bool(words & GREETINGS)


def build_messages(user_input):
    return [
        {
            "role": "system",
            "content": (
                "You are a concise assistant for a Flask app. "
                "Answer direct questions clearly and briefly. "
                "If the input is nonsensical, incomplete, or you are not confident the answer is correct, "
                "reply exactly with: \"I don't know.\" "
                "For simple math, return only the final answer."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]


def generate_llm_reply(user_input):
    if not user_input or not user_input.strip():
        return UNSUPPORTED_REPLY

    if is_greeting(user_input):
        return "Hi! Ask me a question and I'll keep it concise."

    reply = generate_response(build_messages(user_input))
    reply = (reply or "").strip()
    return reply or UNSUPPORTED_REPLY


def search_answers(query, top_k=3):
    del top_k

    reply = generate_llm_reply(query)
    if reply == UNSUPPORTED_REPLY:
        return {"mode": "none", "results": []}

    return {
        "mode": "llm",
        "results": [
            {
                "title": "LLM Response",
                "subject": query,
                "text": reply,
                "source": "llm",
                "category": "generated",
            }
        ],
    }


def handle_query(user_input):
    reply = generate_llm_reply(user_input)
    return {
        "reply": reply,
        "citations": [],
        "response_mode": "llm" if reply != UNSUPPORTED_REPLY else "none",
    }
