import os
from openai import OpenAI
from openai import APIConnectionError, APIError, AuthenticationError


class OpenAIServiceError(RuntimeError):
    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.status_code = status_code

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIServiceError("OPENAI_API_KEY is not set.", status_code=500)

    base_url = os.getenv("OPENAI_BASE_URL")
    default_headers = {}

    if os.getenv("OPENROUTER_SITE_URL"):
        default_headers["HTTP-Referer"] = os.getenv("OPENROUTER_SITE_URL")
    if os.getenv("OPENROUTER_APP_NAME"):
        default_headers["X-Title"] = os.getenv("OPENROUTER_APP_NAME")

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    if default_headers:
        client_kwargs["default_headers"] = default_headers

    return OpenAI(**client_kwargs)

def generate_response(messages):
    try:
        response = get_client().chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=messages
        )
        return response.choices[0].message.content
    except AuthenticationError as exc:
        raise OpenAIServiceError(
            "OpenAI authentication failed. Check whether the API key is valid, active, and loaded from .env.",
            status_code=401,
        ) from exc
    except APIConnectionError as exc:
        raise OpenAIServiceError(
            "Could not reach OpenAI. Check your internet connection, firewall, VPN, or proxy settings."
        ) from exc
    except APIError as exc:
        raise OpenAIServiceError(f"OpenAI API error: {exc}", status_code=502) from exc
