import os

from flask import Blueprint, request, jsonify, render_template
from app.services.diagnostics import get_runtime_stats
from app.services.llm import OpenAIServiceError
from app.services.assistant import handle_query, search_answers

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@main.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@main.route("/stats", methods=["GET"])
def stats():
    return jsonify(get_runtime_stats()), 200


@main.route("/config-check", methods=["GET"])
def config_check():
    api_key = os.getenv("OPENAI_API_KEY", "")
    return jsonify(
        {
            "app_env": os.getenv("APP_ENV", "development"),
            "openai_api_key_loaded": bool(api_key),
            "openai_api_key_prefix": api_key[:10] if api_key else "",
            "openai_base_url": os.getenv("OPENAI_BASE_URL", ""),
            "openai_chat_model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        }
    ), 200


@main.route("/search", methods=["GET"])
def search():
    query = (request.args.get("q") or "").strip()
    top_k = request.args.get("top_k", default=3, type=int)

    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    top_k = max(1, min(top_k, 10))
    payload = search_answers(query, top_k=top_k)
    return jsonify({"query": query, **payload}), 200

@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = handle_query(user_input)
    except OpenAIServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Unexpected server error"}), 500

    return jsonify(response)
