import os
import sys
import unittest
from unittest.mock import patch


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app


class FlaskRagAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("development")
        cls.client = cls.app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_stats_endpoint(self):
        response = self.client.get("/stats")
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("knowledge_rows", payload)
        self.assertIn("files", payload)

    def test_config_check_endpoint(self):
        response = self.client.get("/config-check")
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("openai_api_key_loaded", payload)
        self.assertIn("openai_chat_model", payload)

    def test_search_requires_query(self):
        response = self.client.get("/search")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing query parameter", response.get_json()["error"])

    def test_search_returns_results(self):
        with patch("app.services.assistant.generate_response", return_value="Dubai is a city in the United Arab Emirates."):
            response = self.client.get("/search?q=Dubai")
            payload = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertIn("results", payload)
            self.assertGreaterEqual(len(payload["results"]), 1)
            self.assertEqual(payload["mode"], "llm")

    def test_search_uses_llm_for_math(self):
        with patch("app.services.assistant.generate_response", return_value="225"):
            response = self.client.get("/search?q=15*15")
            payload = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(payload["mode"], "llm")
            self.assertGreaterEqual(len(payload["results"]), 1)
            self.assertIn("225", payload["results"][0]["text"])

    def test_chat_returns_structured_payload(self):
        with patch("app.services.assistant.generate_response", return_value="Dubai is a city in the United Arab Emirates."):
            response = self.client.post("/chat", json={"message": "What is Dubai?"})
            payload = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertIn("reply", payload)
            self.assertIn("citations", payload)
            self.assertIn("retrieval_mode", payload)

    def test_chat_uses_llm_for_math(self):
        with patch("app.services.assistant.generate_response", return_value="225"):
            response = self.client.post("/chat", json={"message": "15*15"})
            payload = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertIn("225", payload["reply"])
            self.assertEqual(payload["retrieval_mode"], "llm")


if __name__ == "__main__":
    unittest.main()
