"""
Targeted Test Suite for AI Tutor Relevance Gate, Dynamic Suggestions, Anti-Hallucination,
and Existing Functionality Preservation.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.tutor.quantum_tutor import tutor, is_quantum_or_learning_query, generate_dynamic_suggestions, clear_conversation_store
from src.tutor.llm_client import LLMClient


class TestTutorRelevanceAndSuggestions(unittest.TestCase):

    def setUp(self):
        clear_conversation_store()

    def test_1_what_is_quantum_computing(self):
        """TEST 1: 'What is quantum computing?' → discusses quantum computing (not superposition)."""
        res = tutor("What is quantum computing?", mode="explain", use_mock=True)
        self.assertNotIn("That's outside the scope", res["answer"])
        self.assertEqual(res["concept"], "Quantum Computing")
        self.assertFalse(res.get("is_off_topic", False))

    def test_2_what_are_applications_of_quantum_computing(self):
        """TEST 2: 'What are applications of quantum computing?' → discusses applications."""
        res = tutor("What are applications of quantum computing?", mode="explain", use_mock=True)
        self.assertNotIn("That's outside the scope", res["answer"])
        self.assertEqual(res["concept"], "Applications of Quantum Computing")
        self.assertFalse(res.get("is_off_topic", False))

    def test_3_explain_superposition(self):
        """TEST 3: 'Explain superposition.' → discusses superposition."""
        res = tutor("Explain superposition.", mode="explain", use_mock=True)
        self.assertNotIn("That's outside the scope", res["answer"])
        self.assertEqual(res["concept"], "Quantum Superposition")
        self.assertFalse(res.get("is_off_topic", False))

    def test_4_conversation_superposition_then_quantum_computing(self):
        """TEST 4: ('What is superposition?' -> 'What is quantum computing?') -> 2nd answer discusses quantum computing."""
        res1 = tutor("What is superposition?", mode="explain", use_mock=True)
        self.assertEqual(res1["concept"], "Quantum Superposition")

        res2 = tutor("What is quantum computing?", mode="explain", extra_context={"previous_topic": res1["concept"]}, use_mock=True)
        self.assertEqual(res2["concept"], "Quantum Computing")
        self.assertIn("quantum computing", res2["answer"].lower())
        self.assertNotIn("allows quantum systems to exist in linear combinations", res2["answer"].lower())

    def test_5_referential_follow_up_applications(self):
        """TEST 5: ('What is quantum computing?' -> 'What are its applications?') -> 2nd answer resolves referent and discusses applications."""
        res1 = tutor("What is quantum computing?", mode="explain", use_mock=True)
        self.assertEqual(res1["concept"], "Quantum Computing")

        res2 = tutor("What are its applications?", mode="explain", extra_context={"previous_topic": res1["concept"]}, use_mock=True)
        self.assertEqual(res2["concept"], "Applications of Quantum Computing")

    def test_6_conversation_superposition_then_qubit(self):
        """TEST 6: ('What is superposition?' -> 'What is a qubit?') -> 2nd answer discusses qubits."""
        res1 = tutor("What is superposition?", mode="explain", use_mock=True)
        self.assertEqual(res1["concept"], "Quantum Superposition")

        res2 = tutor("What is a qubit?", mode="explain", extra_context={"previous_topic": res1["concept"]}, use_mock=True)
        self.assertEqual(res2["concept"], "Qubits")

    def test_7_suggestion_click_processed_as_new_query(self):
        """TEST 7: Suggestion click ('What is a qubit?') -> processed as new query about qubits."""
        res = tutor("What is a qubit?", mode="explain", use_mock=True)
        self.assertEqual(res["concept"], "Qubits")
        self.assertNotIn("That's outside the scope", res["answer"])

    def test_8_unrelated_question_capital_of_france(self):
        """TEST 8: Unrelated question ('What is the capital of France?') -> returns outside scope response."""
        res = tutor("What is the capital of France?", mode="explain", use_mock=True)
        self.assertTrue(res.get("is_off_topic"))
        self.assertIn("outside the scope of the Quantum Tutor", res["answer"])
        self.assertIn("QURIO specializes in quantum computing", res["answer"])
        self.assertIn("For example", res["answer"])

    def test_9_dynamic_suggestions_per_topic(self):
        """TEST 9: Suggestions after two different topics reflect CURRENT topic and do not repeat previous set."""
        res_qc = tutor("What is quantum computing?", mode="explain", use_mock=True)
        res_qubit = tutor("What is a qubit?", mode="explain", use_mock=True)

        sug_qc = res_qc.get("suggestions", [])
        sug_qubit = res_qubit.get("suggestions", [])

        self.assertGreater(len(sug_qc), 0)
        self.assertGreater(len(sug_qubit), 0)
        self.assertNotEqual(sug_qc, sug_qubit)

    def test_10_missing_learner_information_no_hallucination(self):
        """10. Missing learner information → AI does not invent it."""
        res = tutor("What is my performance score?", mode="explain", learner_profile=None, use_mock=True)
        self.assertNotIn("Alice", res["answer"])
        self.assertNotIn("Bob", res["answer"])

    def test_11_existing_circuit_assistant_still_works(self):
        """11. Existing circuit assistant still works."""
        extra_ctx = {
            "circuit": {
                "qubits": 2,
                "gates": [
                    {"gate": "h", "target": 0},
                    {"gate": "cx", "control": 0, "target": 1}
                ],
                "intended_goal": "bell_state"
            }
        }
        res = tutor("Check my Bell state circuit", mode="circuit_assistant", extra_context=extra_ctx, use_mock=True)
        self.assertIn("circuit_validation", res)
        self.assertTrue(res["circuit_validation"]["valid"])
        self.assertIn("Circuit Verified", res["answer"])

    def test_12_existing_quiz_analysis_still_works(self):
        """12. Existing quiz analysis still works."""
        extra_ctx = {
            "quiz": {
                "quiz_id": "q_foundations",
                "responses": [
                    {"question_id": "q1", "topic": "qubits", "user_answer": "A", "correct_answer": "A"},
                    {"question_id": "q2", "topic": "superposition", "user_answer": "B", "correct_answer": "C"}
                ]
            }
        }
        res = tutor("Analyze my quiz results", mode="quiz_analysis", extra_context=extra_ctx, use_mock=True)
        self.assertIn("quiz_analysis", res)
        self.assertEqual(res["quiz_analysis"]["score_pct"], 50.0)

    def test_13_groq_provider_integration(self):
        """13. Groq provider still works (via LLMClient initialization and mocked response)."""
        import os
        client = LLMClient(provider="groq", api_key="gsk_test_key_12345")
        self.assertEqual(client.provider, "groq")
        expected_default = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.assertEqual(client.model, expected_default)
        
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"choices": [{"message": {"content": "{\\"answer\\": \\"Groq test response\\", \\"concept\\": \\"Qubits\\", \\"difficulty\\": \\"Intermediate\\", \\"mode\\": \\"explain\\", \\"hint\\": \\"Hint\\", \\"next_step\\": \\"Next\\", \\"confidence\\": 0.95, \\"suggestions\\": [\\"S1\\", \\"S2\\"]}"}}]}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            resp = client.generate_completion("System prompt", "User prompt", {})
            self.assertIn("Groq test response", resp)

    def test_14_mock_fallback_still_works(self):
        """14. Mock fallback still works when API fails or provider is mock."""
        client = LLMClient(use_mock=True)
        res = tutor("Explain qubit superposition", mode="explain", llm_client=client)
        self.assertIn("answer", res)
        self.assertGreaterEqual(res["quality_score"], 85.0)

    def test_15_semantic_qubit_explanation(self):
        """15. Semantic check for 'What is a qubit?' → Must explain qubit concepts, not generic template."""
        res = tutor("What is a qubit?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("qubit", ans.lower())
        self.assertIn("|0>", ans)
        self.assertNotIn("allows quantum systems to exist in linear combinations", ans.lower())

    def test_16_semantic_shor_algorithm_explanation(self):
        """16. Semantic check for 'What is Shor's algorithm?' → Must explain factoring & period finding."""
        res = tutor("What is Shor's algorithm?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("factor", ans.lower())
        self.assertIn("shor", ans.lower())
        self.assertNotIn("allows quantum systems to exist in linear combinations", ans.lower())

    def test_17_semantic_quantum_computing_and_applications(self):
        """17. Semantic check for multi-part 'What is quantum computing and its applications?' → Addresses both parts."""
        res = tutor("What is quantum computing and its applications?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("quantum computing", ans.lower())
        self.assertIn("application", ans.lower())
        self.assertNotIn("allows quantum systems to exist in linear combinations", ans.lower())

    def test_18_semantic_measurement_collapse_explanation(self):
        """18. Semantic check for 'What is measurement collapse and how does it happen?' → Discusses collapse mechanism."""
        res = tutor("What is measurement collapse and how does it happen?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("measurement", ans.lower())
        self.assertIn("collapse", ans.lower())
        self.assertNotIn("allows quantum systems to exist in linear combinations", ans.lower())

    def test_19_semantic_hadamard_gate_explanation(self):
        """19. Semantic check for 'What is a Hadamard gate?' → Explains H gate transformation."""
        res = tutor("What is a Hadamard gate?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("hadamard", ans.lower())
        self.assertIn("|0>", ans)
        self.assertNotIn("allows quantum systems to exist in linear combinations", ans.lower())

    def test_20_semantic_entanglement_explanation(self):
        """20. Semantic check for 'What is quantum entanglement?' → Explains joint qubit correlation without FTL claim."""
        res = tutor("What is quantum entanglement?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("entanglement", ans.lower())
        self.assertNotIn("faster than light", ans.lower())

    def test_21_semantic_applications_explanation(self):
        """21. Semantic check for 'What are applications of quantum computing?' → Discusses applications specifically."""
        res = tutor("What are applications of quantum computing?", mode="explain", use_mock=True)
        ans = res["answer"]
        self.assertIn("application", ans.lower())

    def test_22_conversation_a_qubit_followup_classical_bit(self):
        """Conversation A: 'What is a qubit?' -> 'Why is it different from a classical bit?'"""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "SESS_A"}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))
        self.assertEqual(res1["concept"], "Qubits")

        res2 = tutor("Why is it different from a classical bit?", mode="explain", learner_profile={"learner_id": "SESS_A"}, use_mock=True)
        self.assertFalse(res2.get("is_off_topic", False))
        self.assertNotIn("outside the scope", res2["answer"])
        self.assertEqual(res2["concept"], "Qubits")

    def test_23_conversation_b_superposition_example(self):
        """Conversation B: 'What is quantum superposition?' -> 'Can you give me an example?'"""
        res1 = tutor("What is quantum superposition?", mode="explain", learner_profile={"learner_id": "SESS_B"}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))
        self.assertEqual(res1["concept"], "Quantum Superposition")

        res2 = tutor("Can you give me an example?", mode="explain", learner_profile={"learner_id": "SESS_B"}, use_mock=True)
        self.assertFalse(res2.get("is_off_topic", False))
        self.assertNotIn("outside the scope", res2["answer"])

    def test_24_conversation_c_shor_break_rsa(self):
        """Conversation C: 'What is Shor's algorithm?' -> 'Does it break RSA?'"""
        res1 = tutor("What is Shor's algorithm?", mode="explain", learner_profile={"learner_id": "SESS_C"}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))
        self.assertEqual(res1["concept"], "Shor's Algorithm")

        res2 = tutor("Does it break RSA?", mode="explain", learner_profile={"learner_id": "SESS_C"}, use_mock=True)
        self.assertFalse(res2.get("is_off_topic", False))
        self.assertNotIn("outside the scope", res2["answer"])

    def test_25_conversation_d_entanglement_superposition_useful(self):
        """Conversation D: 'Explain quantum entanglement.' -> 'Why is superposition useful here?'"""
        res1 = tutor("Explain quantum entanglement.", mode="explain", learner_profile={"learner_id": "SESS_D"}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))

        res2 = tutor("Why is superposition useful here?", mode="explain", learner_profile={"learner_id": "SESS_D"}, use_mock=True)
        self.assertFalse(res2.get("is_off_topic", False))
        self.assertNotIn("outside the scope", res2["answer"])

    def test_26_conversation_e_qubit_offtopic_capital_of_france(self):
        """Conversation E: 'What is a qubit?' -> 'What is the capital of France?' → 2nd is rejected as off-topic."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "SESS_E"}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))

        res2 = tutor("What is the capital of France?", mode="explain", learner_profile={"learner_id": "SESS_E"}, use_mock=True)
        self.assertTrue(res2.get("is_off_topic", False))
        self.assertIn("outside the scope", res2["answer"])

    def test_27_conversation_f_quantum_computing_applications(self):
        """Conversation F: 'What is quantum computing?' -> 'What are its applications?'"""
        res1 = tutor("What is quantum computing?", mode="explain", learner_profile={"learner_id": "SESS_F"}, use_mock=True)
        self.assertFalse(res1.get("is_off_topic", False))
        self.assertEqual(res1["concept"], "Quantum Computing")

        res2 = tutor("What are its applications?", mode="explain", learner_profile={"learner_id": "SESS_F"}, use_mock=True)
        self.assertFalse(res2.get("is_off_topic", False))
        self.assertEqual(res2["concept"], "Applications of Quantum Computing")

    def test_28_stale_response_prevention_qubit_vs_classical_bit(self):
        """Regression Test 28: Consecutive questions must not return stale identical responses."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "REG_SESS_1"}, use_mock=True)
        res2 = tutor("Why is it different from a classical bit?", mode="explain", learner_profile={"learner_id": "REG_SESS_1"}, use_mock=True)

        self.assertNotEqual(res1["answer"], res2["answer"])
        self.assertIn("classical bit", res2["answer"].lower())

    def test_29_stale_response_prevention_bloch_sphere(self):
        """Regression Test 29: Q1='What is a qubit?' -> Q2='What is the Bloch sphere?' must return Bloch sphere response."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "REG_SESS_2"}, use_mock=True)
        res2 = tutor("What is the Bloch sphere?", mode="explain", learner_profile={"learner_id": "REG_SESS_2"}, use_mock=True)

        self.assertNotEqual(res1["answer"], res2["answer"])
        self.assertEqual(res2["concept"], "Bloch Sphere")
        self.assertIn("bloch", res2["answer"].lower())

    def test_30_stale_response_prevention_hadamard_gate(self):
        """Regression Test 30: Q1='What is a qubit?' -> Q2='What does the Hadamard gate do?' must return Hadamard gate response."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "REG_SESS_3"}, use_mock=True)
        res2 = tutor("What does the Hadamard gate do?", mode="explain", learner_profile={"learner_id": "REG_SESS_3"}, use_mock=True)

        self.assertNotEqual(res1["answer"], res2["answer"])
        self.assertEqual(res2["concept"], "Hadamard Gate")
        self.assertIn("hadamard", res2["answer"].lower())

    def test_31_test_case_a_shor_then_rsa(self):
        """Test Case A: Shor's Algorithm -> 'RSA' → resolves concept to RSA Encryption."""
        res1 = tutor("What is Shor's algorithm?", mode="explain", learner_profile={"learner_id": "TEST_A"}, use_mock=True)
        self.assertEqual(res1["concept"], "Shor's Algorithm")

        res2 = tutor("RSA", mode="explain", learner_profile={"learner_id": "TEST_A"}, use_mock=True)
        self.assertEqual(res2["concept"], "RSA Encryption")
        self.assertIn("rsa", res2["answer"].lower())

    def test_32_test_case_b_shor_then_why_is_rsa_vulnerable(self):
        """Test Case B: Shor's Algorithm -> 'Why is RSA vulnerable?' → resolves concept to RSA Encryption."""
        res1 = tutor("What is Shor's algorithm?", mode="explain", learner_profile={"learner_id": "TEST_B"}, use_mock=True)
        res2 = tutor("Why is RSA vulnerable?", mode="explain", learner_profile={"learner_id": "TEST_B"}, use_mock=True)

        self.assertEqual(res2["concept"], "RSA Encryption")
        self.assertIn("rsa", res2["answer"].lower())

    def test_33_test_case_c_qubit_then_different_from_classical_bit(self):
        """Test Case C: Qubit -> 'Why is it different from a classical bit?' → resolves concept to Qubits."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "TEST_C"}, use_mock=True)
        res2 = tutor("Why is it different from a classical bit?", mode="explain", learner_profile={"learner_id": "TEST_C"}, use_mock=True)

        self.assertEqual(res2["concept"], "Qubits")
        self.assertIn("classical bit", res2["answer"].lower())

    def test_34_test_case_d_qubit_then_bloch_sphere(self):
        """Test Case D: Qubit -> 'Bloch sphere' → resolves concept to Bloch Sphere."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "TEST_D"}, use_mock=True)
        res2 = tutor("Bloch sphere", mode="explain", learner_profile={"learner_id": "TEST_D"}, use_mock=True)

        self.assertEqual(res2["concept"], "Bloch Sphere")
        self.assertIn("bloch", res2["answer"].lower())

    def test_35_test_case_e_grover_then_rsa(self):
        """Test Case E: Grover's Algorithm -> 'RSA' → resolves concept to RSA Encryption (not Grover)."""
        res1 = tutor("What is Grover's algorithm?", mode="explain", learner_profile={"learner_id": "TEST_E"}, use_mock=True)
        self.assertEqual(res1["concept"], "Grover's Algorithm")

        res2 = tutor("RSA", mode="explain", learner_profile={"learner_id": "TEST_E"}, use_mock=True)
        self.assertEqual(res2["concept"], "RSA Encryption")
        self.assertIn("rsa", res2["answer"].lower())

    def test_36_test_case_f_rsa_then_relate_to_shor(self):
        """Test Case F: RSA -> 'How does it relate to Shor's algorithm?' → answers relation to Shor."""
        res1 = tutor("What is RSA?", mode="explain", learner_profile={"learner_id": "TEST_F"}, use_mock=True)
        res2 = tutor("How does it relate to Shor's algorithm?", mode="explain", learner_profile={"learner_id": "TEST_F"}, use_mock=True)

        self.assertNotIn("outside the scope", res2["answer"])
        self.assertIn("shor", res2["answer"].lower())

    def test_37_test_case_g_rsa_then_why_vulnerable(self):
        """Test Case G: RSA -> 'Why is it vulnerable?' → answers RSA vulnerability."""
        res1 = tutor("What is RSA?", mode="explain", learner_profile={"learner_id": "TEST_G"}, use_mock=True)
        res2 = tutor("Why is it vulnerable?", mode="explain", learner_profile={"learner_id": "TEST_G"}, use_mock=True)

        self.assertNotIn("outside the scope", res2["answer"])

    def test_38_test_case_h_shor_then_qft(self):
        """Test Case H: Shor's Algorithm -> 'QFT' → resolves concept to Quantum Fourier Transform."""
        res1 = tutor("What is Shor's algorithm?", mode="explain", learner_profile={"learner_id": "TEST_H"}, use_mock=True)
        res2 = tutor("QFT", mode="explain", learner_profile={"learner_id": "TEST_H"}, use_mock=True)

        self.assertEqual(res2["concept"], "Quantum Fourier Transform")
        self.assertIn("fourier", res2["answer"].lower())

    def test_39_test_case_i_qubit_then_example(self):
        """Test Case I: Qubit -> 'can you give me an example?' → answers with concrete qubit example."""
        res1 = tutor("What is a qubit?", mode="explain", learner_profile={"learner_id": "TEST_I"}, use_mock=True)
        res2 = tutor("can you give me an example?", mode="explain", learner_profile={"learner_id": "TEST_I"}, use_mock=True)

        self.assertNotIn("outside the scope", res2["answer"])
        self.assertIn("example", res2["answer"].lower())

    def test_40_test_case_j_multi_part_quantum_computing_and_applications(self):
        """Test Case J: 'What is quantum computing and what are its applications?' → addresses both parts."""
        res = tutor("What is quantum computing and what are its applications?", mode="explain", use_mock=True)

        self.assertIn("quantum computing", res["answer"].lower())
        self.assertIn("application", res["answer"].lower())

    def test_41_test_case_k_off_topic_rejection(self):
        """Test Case K: 'What is the capital of France?' → returns outside scope response."""
        res = tutor("What is the capital of France?", mode="explain", use_mock=True)

        self.assertTrue(res.get("is_off_topic"))
        self.assertIn("outside the scope of the Quantum Tutor", res["answer"])


if __name__ == "__main__":
    unittest.main()


