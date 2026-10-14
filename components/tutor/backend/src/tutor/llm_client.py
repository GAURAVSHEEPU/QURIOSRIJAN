"""
LLM Provider Abstraction Layer for Quantum Algorithm Learning Platform.

Provides a unified interface for generative AI tutor and critic calls, supporting:
- Configurable environment providers (Groq / Google Gemini / OpenAI / REST API)
- Deterministic Mock Mode for testing and offline verification
- Safe error handling, JSON parsing safeguards, and zero secret leakage.
"""

import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Ensure .env in backend directory is always loaded even if executed from repo root
_backend_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
if os.path.exists(_backend_env):
    load_dotenv(_backend_env)
else:
    load_dotenv()

from src.tutor.mock_llm import MockLLMClient


class LLMClient:
    """Configurable LLM Provider Client supporting Groq, Gemini, OpenAI, and offline Mock Mode."""

    def __init__(self, provider: str = None, model: str = None, api_key: str = None, use_mock: bool = False):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "mock")).lower()
        
        # Provider-specific API key resolution and default models
        resolved_key = api_key if api_key is not None else (os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY", ""))
        if self.provider == "groq":
            self.api_key = resolved_key
            default_model = "llama-3.3-70b-versatile"
        elif self.provider == "openai":
            self.api_key = resolved_key
            default_model = "gpt-4o-mini"
        else:  # gemini / google / mock / default
            self.api_key = resolved_key
            default_model = "gemini-1.5-flash"

        self.model = model or os.getenv("LLM_MODEL", default_model)
        self.use_mock = use_mock or (self.provider == "mock") or not self.api_key
        
        self.mock_client = MockLLMClient()

    def generate_completion(self, system_prompt: str, user_prompt: str, context: dict = None) -> str:
        """
        Generates completion from configured LLM provider (Groq, Gemini, OpenAI) or Mock client.
        
        Args:
            system_prompt: System prompt instructions.
            user_prompt: User query and context prompt.
            context: Context dictionary.
            
        Returns:
            JSON string or raw response text.
        """
        if context is None:
            context = {}
            
        if self.use_mock or self.provider == "mock" or not self.api_key:
            return self.mock_client.generate_response(system_prompt, user_prompt, context)

        try:
            # Groq & OpenAI REST API Integration (OpenAI-compatible chat completions schema)
            if self.provider in ("groq", "openai"):
                url = "https://api.groq.com/openai/v1/chat/completions" if self.provider == "groq" else "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "QURIO-QuantumTutor/1.0"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.25,
                    "response_format": {"type": "json_object"}
                }
                
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    text = res_data["choices"][0]["message"]["content"]
                    return text

            # Production Google Gemini REST API Integration
            elif self.provider in ("gemini", "google"):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "contents": [
                        {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"}]}
                    ],
                    "generationConfig": {
                        "temperature": 0.25,
                        "responseMimeType": "application/json"
                    }
                }
                
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return text
                    
            # Fallback to Mock Client if unsupported provider specified
            return self.mock_client.generate_response(system_prompt, user_prompt, context)
            
        except Exception:
            # Safe Fallback: Return Mock Client response on API errors without exposing keys
            return self.mock_client.generate_response(system_prompt, user_prompt, context)

    def evaluate_critique(self, system_prompt: str, user_prompt: str, candidate_response: dict, context: dict = None) -> str:
        """
        Evaluates candidate response via LLM Critic call or Mock Critic.
        """
        if context is None:
            context = {}
            
        if self.use_mock or self.provider == "mock" or not self.api_key:
            return self.mock_client.critique_response(system_prompt, user_prompt, candidate_response, context)

        try:
            full_user_prompt = f"{user_prompt}\n\nCANDIDATE RESPONSE TO CRITIQUE:\n{json.dumps(candidate_response, indent=2)}"
            return self.generate_completion(system_prompt, full_user_prompt, context)
        except Exception:
            return self.mock_client.critique_response(system_prompt, user_prompt, candidate_response, context)
