"""
Regression tests for Phase 2C: AI Tutor Response Conciseness & Lightweight Structure.

Verifies:
1. System prompt instructs concise responses (80-150 words normally, ~180 words max).
2. System prompt uses lightweight structure rather than rigid multi-heading 6-step templates.
3. System prompt allows longer detailed responses when explicitly requested or required.
4. AI Critic prompt supports conciseness without penalizing brevity.
5. Simple questions receive concise answers (word count <= 180 words).
6. Technical questions can still include necessary equations or examples (e.g. Bloch sphere, Hadamard).
7. Explicit requests for detailed explanations preserve thorough explanations.
8. Existing JSON schema / TutorResponse fields and fallback contracts remain intact.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

from src.tutor.quantum_tutor import (
    tutor,
    build_context,
    build_system_prompt,
    build_critic_system_prompt,
    fallback_critic
)
from src.tutor.llm_client import LLMClient


class TestTutorResponseConcisenessAndStructure(unittest.TestCase):

    def test_system_prompt_conciseness_instructions(self):
        """Verifies system prompt sets 80-150 word guideline and ~180 word maximum for normal questions."""
        ctx = build_context("What is a qubit?", mode="explain")
        prompt = build_system_prompt(ctx)
        
        self.assertIn("80–150 words", prompt)
        self.assertIn("180 words maximum", prompt)
        self.assertIn("Lightweight Structure", prompt)
        # Verify rigid 6-step mandatory structure is removed
        self.assertNotIn("Preferred explanation sequence", prompt)

    def test_system_prompt_allows_detail_when_explicitly_requested(self):
        """Verifies system prompt explicitly permits longer responses when in-depth detail is requested."""
        ctx = build_context("Explain Shor's algorithm in detail step by step", mode="explain")
        prompt = build_system_prompt(ctx)
        
        self.assertIn("in detail", prompt)
        self.assertIn("Multi-part questions", prompt)

    def test_critic_prompt_supports_conciseness(self):
        """Verifies AI Critic does not penalize concise answers for brevity."""
        critic_prompt = build_critic_system_prompt()
        self.assertIn("80–150 words", critic_prompt)
        self.assertIn("Do NOT penalize a response for brevity", critic_prompt)

    def test_simple_question_word_count_within_concise_bounds(self):
        """Verifies standard conceptual questions (e.g. qubit, superposition, hadamard) stay within concise bounds (<= 180 words)."""
        simple_queries = [
            "What is a qubit?",
            "What is quantum superposition?",
            "What is a Hadamard gate?",
            "What is quantum entanglement?",
            "What is the Bloch sphere?"
        ]
        for q in simple_queries:
            res = tutor(q, mode="explain", use_mock=True)
            word_count = len(res["answer"].split())
            self.assertLessEqual(
                word_count,
                180,
                f"Query '{q}' produced {word_count} words, which exceeds the 180-word ceiling."
            )
            self.assertGreaterEqual(
                word_count,
                25,
                f"Query '{q}' produced {word_count} words, which is excessively brief."
            )

    def test_technical_question_preserves_equations_and_math(self):
        """Verifies technical explanations preserve exact mathematical notation and state formulas."""
        res_qubit = tutor("What is a qubit?", mode="explain", use_mock=True)
        # Check Dirac notation and amplitude equation preserved
        self.assertIn("|0>", res_qubit["answer"])
        self.assertIn("|1>", res_qubit["answer"])
        self.assertIn("|alpha|^2 + |beta|^2 = 1", res_qubit["answer"])

        res_bloch = tutor("What is the Bloch sphere?", mode="explain", use_mock=True)
        self.assertIn("theta", res_bloch["answer"])
        self.assertIn("phi", res_bloch["answer"])

        res_h = tutor("What is a Hadamard gate?", mode="explain", use_mock=True)
        self.assertIn("H|0>", res_h["answer"])

    def test_explicit_detail_or_multipart_preserves_thorough_answer(self):
        """Verifies multi-part questions preserve full thorough coverage with headings."""
        res = tutor("What is quantum computing and what are its applications?", mode="explain", use_mock=True)
        self.assertIn("## What is Quantum Computing?", res["answer"])
        self.assertIn("## Applications of Quantum Computing", res["answer"])
        self.assertIn("Cryptography", res["answer"])
        self.assertIn("Optimization", res["answer"])

    def test_response_schema_and_contracts_preserved(self):
        """Verifies required response schema keys, quality score, iterations, and suggestions remain intact."""
        res = tutor("Explain quantum superposition", mode="explain", use_mock=True)
        required_keys = ["answer", "concept", "difficulty", "mode", "hint", "next_step", "confidence", "quality_score", "iterations", "suggestions"]
        for key in required_keys:
            self.assertIn(key, res, f"Missing required response key: {key}")
        self.assertGreaterEqual(res["quality_score"], 85.0)
        self.assertLessEqual(res["iterations"], 3)
        self.assertIsInstance(res["suggestions"], list)

    def test_mock_fallback_and_critic_scoring_on_concise_response(self):
        """Verifies fallback critic scores concise candidate responses >= 85.0 without false penalties."""
        candidate = {
            "answer": "A qubit is the fundamental unit of quantum information. Unlike a classical bit which is strictly 0 or 1, a qubit state |psi> = alpha|0> + beta|1> is in superposition until measured.",
            "concept": "Qubits",
            "difficulty": "Intermediate",
            "mode": "explain"
        }
        ctx = build_context("What is a qubit?", mode="explain")
        critic_res = fallback_critic(candidate, ctx)
        self.assertGreaterEqual(critic_res["score"], 85.0)
        self.assertFalse(critic_res["should_improve"])


if __name__ == "__main__":
    unittest.main()

