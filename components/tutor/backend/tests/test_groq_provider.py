"""
Offline Unit Test Suite for Groq Provider Integration.

Tests Groq client configuration, API mocking, fallback behavior, error handling,
and loop engineering integration without calling live network services.
"""

import json
import os
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import URLError, HTTPError

from src.tutor.llm_client import LLMClient
from src.tutor.quantum_tutor import tutor


class TestGroqProviderOffline(unittest.TestCase):

    def test_1_successful_groq_response(self):
        """1. Test successful Groq JSON completion response parsing."""
        mock_response_payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "answer": "Groq Llama-3.3 explanation of Superposition.",
                            "concept": "Superposition",
                            "difficulty": "Intermediate",
                            "mode": "explain",
                            "hint": "Think about linear combinations of states.",
                            "next_step": "Try a Hadamard gate simulation.",
                            "confidence": 0.98
                        })
                    }
                }
            ]
        }

        mock_http_response = MagicMock()
        mock_http_response.read.return_value = json.dumps(mock_response_payload).encode("utf-8")
        mock_http_response.__enter__.return_value = mock_http_response

        with patch("urllib.request.urlopen", return_value=mock_http_response):
            client = LLMClient(provider="groq", model="llama-3.3-70b-versatile", api_key="gsk_test_mock_key")
            response = client.generate_completion("System prompt", "User query")
            
            parsed = json.loads(response)
            self.assertEqual(parsed["concept"], "Superposition")
            self.assertEqual(parsed["confidence"], 0.98)

    def test_2_api_error_handling(self):
        """2. Test graceful fallback to Mock client on HTTP 500 API error."""
        with patch("urllib.request.urlopen", side_effect=HTTPError("https://api.groq.com", 500, "Internal Server Error", {}, None)):
            client = LLMClient(provider="groq", api_key="gsk_test_key")
            response = client.generate_completion("System prompt", "User query")
            
            self.assertTrue(isinstance(response, str))
            parsed = json.loads(response)
            self.assertIn("answer", parsed)

    def test_3_timeout_network_failure(self):
        """3. Test graceful fallback to Mock client on network timeout or connection refused."""
        with patch("urllib.request.urlopen", side_effect=URLError("Connection refused")):
            client = LLMClient(provider="groq", api_key="gsk_test_key")
            response = client.generate_completion("System prompt", "User query")
            
            parsed = json.loads(response)
            self.assertIn("answer", parsed)

    def test_4_malformed_response(self):
        """4. Test graceful fallback on malformed JSON payload returned by API."""
        mock_http_response = MagicMock()
        mock_http_response.read.return_value = b"Not valid json payload"
        mock_http_response.__enter__.return_value = mock_http_response

        with patch("urllib.request.urlopen", return_value=mock_http_response):
            client = LLMClient(provider="groq", api_key="gsk_test_key")
            response = client.generate_completion("System prompt", "User query")
            
            parsed = json.loads(response)
            self.assertIn("answer", parsed)

    def test_5_empty_response(self):
        """5. Test graceful fallback on empty response string from API."""
        mock_response_payload = {"choices": [{"message": {"content": ""}}]}
        mock_http_response = MagicMock()
        mock_http_response.read.return_value = json.dumps(mock_response_payload).encode("utf-8")
        mock_http_response.__enter__.return_value = mock_http_response

        with patch("urllib.request.urlopen", return_value=mock_http_response):
            client = LLMClient(provider="groq", api_key="gsk_test_key")
            res = client.generate_completion("System prompt", "User query")
            self.assertEqual(res, "")

    def test_6_missing_api_key(self):
        """6. Test automatic fallback to Mock Mode when GROQ_API_KEY is empty."""
        client = LLMClient(provider="groq", api_key="")
        self.assertTrue(client.use_mock)
        
        response = client.generate_completion("System prompt", "User query")
        parsed = json.loads(response)
        self.assertIn("answer", parsed)

    def test_7_invalid_model_configuration(self):
        """7. Test client instantiation with custom model name or default Groq model."""
        client = LLMClient(provider="groq", api_key="gsk_test_key")
        expected_default = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.assertEqual(client.model, expected_default)
        
        custom_client = LLMClient(provider="groq", model="mixtral-8x7b-32768", api_key="gsk_test_key")
        self.assertEqual(custom_client.model, "mixtral-8x7b-32768")

    def test_8_tutor_loop_with_groq_mock(self):
        """8. Test full tutor loop engineering execution using Groq client configuration."""
        client = LLMClient(provider="groq", api_key="gsk_test_key", use_mock=True)
        res = tutor("Explain Grover algorithm", mode="explain", llm_client=client)
        
        self.assertIn("answer", res)
        self.assertGreaterEqual(res["quality_score"], 85.0)
        self.assertLessEqual(res["iterations"], 3)

    def test_9_user_agent_header(self):
        """9. Test that outgoing Groq request includes QURIO-QuantumTutor/1.0 User-Agent header."""
        captured_request = None

        def fake_urlopen(req, timeout=15):
            nonlocal captured_request
            captured_request = req
            mock_res = MagicMock()
            mock_res.read.return_value = json.dumps({
                "choices": [{"message": {"content": json.dumps({"answer": "Qubit test"})}}]
            }).encode("utf-8")
            mock_res.__enter__.return_value = mock_res
            return mock_res

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            client = LLMClient(provider="groq", api_key="gsk_mock_key")
            client.generate_completion("System prompt", "User prompt")

        self.assertIsNotNone(captured_request)
        user_agent = captured_request.get_header("User-agent")
        self.assertEqual(user_agent, "QURIO-QuantumTutor/1.0")


if __name__ == "__main__":
    unittest.main()

