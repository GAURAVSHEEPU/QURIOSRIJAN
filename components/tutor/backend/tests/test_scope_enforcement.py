"""
Offline regression test suite for Phase 2E: Robust Quantum-Domain Scope Enforcement.

Verifies:
1. Clearly unrelated requests are rejected with polite domain redirect:
   - "Write a romantic birthday message."
   - "Who will win tomorrow's cricket match?"
   - "Explain photosynthesis."
   - "Help me choose a phone."
2. Relevant quantum questions are accepted (qubits, gates, circuits, superposition,
   entanglement, measurement, algorithms, Qiskit, error correction, research).
3. Classical mathematics, physics, and programming connected to quantum computing are accepted:
   - "Explain linear algebra for quantum computing"
   - "How to simulate a quantum circuit with NumPy?"
   - "Matrix multiplication for quantum gates"
   While unconnected classical requests are redirected:
   - "What is linear algebra?"
   - "How to use NumPy in Python?"
4. Generic words ("explain", "help", "debug", "code", "study") and short queries alone
   do not automatically bypass the guard.
5. Mock mode obeys the same deterministic scope decision.
6. The critic/refinement loop cannot turn an off-topic redirect into an unrelated answer.
7. Existing tutor response schema remains fully intact on redirects.
8. Explicitly quantum-related follow-ups remain supported.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.tutor.quantum_tutor import (
    tutor,
    is_quantum_or_learning_query,
    clear_conversation_store,
    add_conversation_turn
)
from src.tutor.llm_client import LLMClient


class TestQuantumDomainScopeEnforcement(unittest.TestCase):

    def setUp(self):
        clear_conversation_store()

    def test_clearly_unrelated_requests_rejected(self):
        """1. Rejects clearly unrelated requests specified in Phase 2E requirements."""
        unrelated_queries = [
            "Write a romantic birthday message.",
            "Who will win tomorrow's cricket match?",
            "Explain photosynthesis.",
            "Help me choose a phone."
        ]
        for query in unrelated_queries:
            self.assertFalse(
                is_quantum_or_learning_query(query),
                f"Expected query '{query}' to be classified as off-topic"
            )
            res = tutor(query, mode="explain", use_mock=True)
            self.assertTrue(res.get("is_off_topic"), f"Query '{query}' should return is_off_topic=True")
            self.assertIn("outside the scope of the Quantum Tutor", res["answer"])
            self.assertIn("QURIO specializes in quantum computing and quantum algorithms", res["answer"])
            self.assertIn("For example", res["answer"])

    def test_relevant_quantum_requests_accepted(self):
        """2. Accepts core quantum computing queries across domains."""
        quantum_queries = [
            "What is a qubit?",
            "How do quantum gates work?",
            "Explain the Hadamard gate and phase flip.",
            "How does quantum superposition work?",
            "What is quantum entanglement?",
            "Why does quantum measurement collapse the state?",
            "Explain Shor's algorithm for prime factorization.",
            "Explain Grover's search algorithm and amplitude amplification.",
            "How to build a Bell state circuit in Qiskit?",
            "What is quantum error correction and the surface code?",
            "Tell me about recent quantum computing research."
        ]
        for query in quantum_queries:
            self.assertTrue(
                is_quantum_or_learning_query(query),
                f"Expected quantum query '{query}' to be accepted"
            )
            res = tutor(query, mode="explain", use_mock=True)
            self.assertFalse(res.get("is_off_topic", False))
            self.assertNotIn("outside the scope of the Quantum Tutor", res["answer"])

    def test_connected_classical_math_programming_accepted(self):
        """3. Accepts classical mathematics or programming explicitly connected to quantum computing."""
        connected_queries = [
            "Explain linear algebra for quantum computing",
            "How to simulate a quantum circuit with NumPy?",
            "Matrix multiplication for quantum gates",
            "Tensor products in multi-qubit quantum states",
            "Hilbert space representation of quantum states"
        ]
        for query in connected_queries:
            self.assertTrue(
                is_quantum_or_learning_query(query),
                f"Expected connected query '{query}' to be accepted"
            )
            res = tutor(query, mode="explain", use_mock=True)
            self.assertFalse(res.get("is_off_topic", False))
            self.assertNotIn("outside the scope of the Quantum Tutor", res["answer"])

    def test_unconnected_classical_requests_rejected(self):
        """4. Rejects classical math/programming questions when unconnected to quantum computing."""
        unconnected_queries = [
            "What is linear algebra?",
            "How to use NumPy in Python?",
            "Matrix multiplication in C++",
            "How does Python garbage collection work?"
        ]
        for query in unconnected_queries:
            self.assertFalse(
                is_quantum_or_learning_query(query),
                f"Expected unconnected query '{query}' to be rejected"
            )
            res = tutor(query, mode="explain", use_mock=True)
            self.assertTrue(res.get("is_off_topic"))
            self.assertIn("outside the scope of the Quantum Tutor", res["answer"])

    def test_generic_words_alone_do_not_bypass_guard(self):
        """5. Verifies generic words alone or short generic queries do not bypass the guard."""
        generic_queries = [
            "explain",
            "help",
            "debug",
            "code",
            "study",
            "explain please",
            "help me",
            "why?",
            "how?"
        ]
        for q in generic_queries:
            self.assertFalse(
                is_quantum_or_learning_query(q),
                f"Expected generic query '{q}' alone to be rejected without quantum context"
            )
            res = tutor(q, mode="explain", use_mock=True)
            self.assertTrue(res.get("is_off_topic"), f"Expected '{q}' to return off-topic redirect")

    def test_mock_mode_obeys_same_scope_decision(self):
        """6. Mock mode and live LLM client mode both obey deterministic scope decision."""
        query = "Explain photosynthesis."
        res_mock = tutor(query, mode="explain", use_mock=True)
        self.assertTrue(res_mock.get("is_off_topic"))

        client = LLMClient(use_mock=True)
        res_client = tutor(query, mode="explain", llm_client=client)
        self.assertTrue(res_client.get("is_off_topic"))
        self.assertEqual(res_mock["answer"], res_client["answer"])

    def test_critic_refinement_loop_cannot_override_redirect(self):
        """7. Verifies generator/critic refinement loop cannot turn an off-topic redirect into an answer."""
        query = "Who will win tomorrow's cricket match?"

        # Mock LLMClient generate_completion to ensure it is NEVER called when scope guard rejects
        with patch.object(LLMClient, "generate_completion") as mock_generate:
            res = tutor(query, mode="explain", use_mock=False)
            mock_generate.assert_not_called()
            self.assertTrue(res.get("is_off_topic"))
            self.assertEqual(res["iterations"], 1)
            self.assertEqual(res["quality_score"], 100.0)

    def test_response_schema_preserved_on_redirect(self):
        """8. Verifies existing response schema is intact on domain redirects."""
        res = tutor("Help me choose a phone.", mode="explain", use_mock=True)
        expected_fields = [
            "answer", "concept", "difficulty", "mode", "hint",
            "next_step", "confidence", "quality_score", "iterations",
            "is_off_topic", "suggestions"
        ]
        for field in expected_fields:
            self.assertIn(field, res, f"Field '{field}' missing from redirect response")

        self.assertEqual(res["concept"], "General")
        self.assertEqual(res["mode"], "explain")
        self.assertIsInstance(res["suggestions"], list)
        self.assertGreater(len(res["suggestions"]), 0)

    def test_quantum_follow_ups_remain_supported(self):
        """9. Multi-turn follow-ups to valid quantum topics remain supported."""
        session_id = "scope_test_session"
        res1 = tutor("What is a qubit?", mode="explain", extra_context={"session_id": session_id}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))

        # Follow-up referencing qubit
        res2 = tutor("Why is it different from a classical bit?", mode="explain", extra_context={"session_id": session_id}, use_mock=True)
        self.assertFalse(res2.get("is_off_topic", False))
        self.assertEqual(res2["concept"], "Qubits")

        # Concrete example follow-up
        res3 = tutor("Can you give me an example?", mode="explain", extra_context={"session_id": session_id}, use_mock=True)
        self.assertFalse(res3.get("is_off_topic", False))
        self.assertIn("example", res3["answer"].lower())


if __name__ == "__main__":
    unittest.main()

