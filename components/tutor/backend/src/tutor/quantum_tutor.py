"""
AI Quantum Tutor & Loop Engineering Engine for Quantum Algorithm Learning Platform.

Implements the bounded, multi-pass AI tutoring loop:
CONTEXT -> EXECUTION -> CRITIC -> EXIT CONDITION -> IMPROVE / DELIVER

BOUNDS:
- QUALITY_THRESHOLD = 85.0
- MAX_ITERATIONS = 3
- SUPPORTED MODES = [
    "explain", "hint", "debug", "code_explain", "circuit_explain",
    "practice", "chat", "circuit_assistant", "quiz_analysis"
  ]
"""

import os
import re
import json
import threading
from typing import Dict, Any, Optional, Tuple, List

from src.tutor.llm_client import LLMClient
from src.tutor.circuit_validator import CircuitValidator
from src.tutor.quiz_analyzer import QuizAnalyzer

QUALITY_THRESHOLD = 85.0
MAX_ITERATIONS = 3
SUPPORTED_MODES = [
    "explain", "hint", "debug", "code_explain", "circuit_explain",
    "practice", "chat", "circuit_assistant", "quiz_analysis"
]

_CONVERSATION_STORE: Dict[str, List[dict]] = {}
_CONVERSATION_LOCK = threading.Lock()


def get_session_key(learner_profile: Optional[dict] = None, extra_context: Optional[dict] = None) -> str:
    """Derives a consistent session identifier key from learner_profile or extra_context."""
    if extra_context:
        if extra_context.get("session_id"):
            return str(extra_context["session_id"])
        if extra_context.get("learner_id"):
            return str(extra_context["learner_id"])
    if learner_profile and learner_profile.get("learner_id"):
        return str(learner_profile["learner_id"])
    return "default"


def get_conversation_history(session_key: str) -> List[dict]:
    """Retrieves recent conversation history turns for a session key."""
    with _CONVERSATION_LOCK:
        return list(_CONVERSATION_STORE.get(session_key, []))


def add_conversation_turn(session_key: str, query: str, concept: str, answer: str):
    """Appends a completed conversation turn to the session history."""
    with _CONVERSATION_LOCK:
        if session_key not in _CONVERSATION_STORE:
            _CONVERSATION_STORE[session_key] = []
        _CONVERSATION_STORE[session_key].append({
            "query": query,
            "concept": concept,
            "answer": answer
        })
        if len(_CONVERSATION_STORE[session_key]) > 10:
            _CONVERSATION_STORE[session_key] = _CONVERSATION_STORE[session_key][-10:]


def clear_conversation_store(session_key: Optional[str] = None):
    """Clears conversation history (all sessions if key is None)."""
    with _CONVERSATION_LOCK:
        if session_key:
            _CONVERSATION_STORE.pop(session_key, None)
        else:
            _CONVERSATION_STORE.clear()


def get_previous_topic(session_key: str, extra_context: Optional[dict] = None) -> Optional[str]:
    """Retrieves the previous quantum topic focus from extra_context or conversation store history."""
    if extra_context:
        if extra_context.get("previous_topic"):
            return extra_context["previous_topic"]
        if extra_context.get("conversation_topic"):
            return extra_context["conversation_topic"]

    history = get_conversation_history(session_key)
    if history:
        for turn in reversed(history):
            c = turn.get("concept")
            if c and c != "General":
                return c
    return None


def load_curriculum_topics(project_root: str = None) -> list[dict]:
    """Loads curriculum topic metadata from quantum_topics.json."""
    if project_root is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    curr_path = os.path.join(project_root, "data/curriculum/quantum_topics.json")
    if os.path.exists(curr_path):
        try:
            with open(curr_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _matches_domain_term(term: str, text: str) -> bool:
    """Matches a domain keyword or phrase with word-boundary awareness."""
    if not term or not text:
        return False
    # If the term consists solely of alphanumeric characters and underscores, use boundary lookarounds
    if re.search(r'^[a-z0-9_]+$', term):
        pattern = rf'(?<![a-zA-Z0-9]){re.escape(term)}(?![a-zA-Z0-9])'
    else:
        pattern = re.escape(term)
    return bool(re.search(pattern, text, re.IGNORECASE))


def is_quantum_or_learning_query(
    query: str,
    mode: str = "explain",
    extra_context: Optional[dict] = None,
    curriculum: Optional[list] = None,
    session_key: Optional[str] = None
) -> bool:
    """
    Determines whether a user query is related to quantum computing or quantum learning support.
    Executed BEFORE normal tutor answer-generation logic. Context-aware for multi-turn conversations.
    """
    query_lower = query.strip().lower() if query else ""
    if not query_lower:
        return False

    # Generic words alone (e.g. "explain", "help", "debug", "code", "study") or trivial tokens
    # do NOT automatically bypass the domain guard
    tokens = re.findall(r'[a-zA-Z0-9]+', query_lower)
    generic_words = {"explain", "help", "debug", "code", "study", "why", "how", "hi", "hello", "hey", "test", "please"}
    if not tokens or (len(tokens) <= 2 and all(tok in generic_words for tok in tokens)):
        # Check if structured context or previous topic provides an explicit quantum context
        s_key = session_key or get_session_key(extra_context=extra_context)
        prev_topic = get_previous_topic(s_key, extra_context=extra_context)
        has_struct_ctx = bool(extra_context and any(k in extra_context for k in ("circuit", "circuit_data", "quiz", "quiz_data", "responses")))
        if not prev_topic and not has_struct_ctx:
            return False

    # Explicit off-topic phrases across trivia, sports, personal life, general cooking/shopping/tech
    off_topic_exact = {
        "what is my name", "what's my name", "who am i", "tell me my name", "what is my name?",
        "what is my age", "where do i live", "who is the president", "capital of france", "what is the capital of france?",
        "tell me a joke about cats", "how to cook pasta", "what is the weather today",
        "explain photosynthesis", "help me choose a phone", "who will win tomorrow's cricket match?",
        "write a romantic birthday message", "write a romantic birthday message."
    }
    if query_lower in off_topic_exact or "capital of france" in query_lower:
        return False

    off_topic_indicators = [
        "what is my name", "what's my name", "who am i", "tell me my name",
        "capital of france", "capital of", "cook pasta", "recipe for",
        "weather today", "forecast", "movie recommendation",
        "tell me a joke", "football score", "world cup", "cricket match",
        "stock market", "photosynthesis", "romantic birthday", "choose a phone",
        "buy a phone", "best smartphone", "dating advice", "horoscope"
    ]
    quantum_explicit = (
        "quantum", "qubit", "qubits", "gate", "gates", "superposition", "entanglement",
        "circuit", "circuits", "hadamard", "shor", "grover", "bell state", "bloch",
        "measurement", "collapse", "qiskit"
    )
    for indicator in off_topic_indicators:
        if indicator in query_lower and not any(_matches_domain_term(q_term, query_lower) for q_term in quantum_explicit):
            return False

    # Structured context checks (circuit or quiz actively loaded)
    if extra_context and any(k in extra_context for k in ("circuit", "circuit_data", "quiz", "quiz_data", "responses")):
        return True

    # Mode-based check for circuit and quiz assistants
    if mode in ("circuit_assistant", "circuit_explain", "quiz_analysis"):
        return True

    # Primary Quantum Concepts & Terminology (full domain vocabulary with word-boundary awareness)
    quantum_terms = [
        "quantum", "qubit", "qubits", "superposition", "entanglement", "measurement",
        "collapse", "hadamard", "cnot", "pauli", "gate", "gates", "bloch", "bloch sphere", "qiskit",
        "bell state", "bell states", "bell", "grover", "shor", "phase", "circuit", "circuits",
        "decoherence", "bra", "ket", "wavefunction", "statevector", "hamiltonian",
        "unitary", "fidelity", "teleportation", "fourier", "qft", "vqe", "qaoa",
        "deutsch", "bernstein", "simon", "amplitude", "oracle", "register", "qasm",
        "aer", "ibmq", "spin", "photon", "eigenstate", "eigenvalue", "schrodinger",
        "dirac", "rsa", "no-cloning", "error correction", "surface code", "transmon",
        "ion trap", "neutral atom", "quantum anneal", "quantum walk", "quantum key",
        "qkd", "bb84", "phase kickback", "density matrix", "pure state", "mixed state",
        "quantum algorithm", "quantum algorithms", "quantum computer", "quantum computers",
        "quantum computing", "quantum error correction", "quantum teleportation", "quantum walk"
    ]

    for term in quantum_terms:
        if _matches_domain_term(term, query_lower):
            return True

    if curriculum:
        for topic_dict in curriculum:
            topic_name = topic_dict.get("name", "").lower()
            topic_id = topic_dict.get("topic_id", "").lower()
            if topic_name and _matches_domain_term(topic_name, query_lower):
                return True
            if topic_id and _matches_domain_term(topic_id, query_lower):
                return True

    # Classical Math, Physics, and Programming CONNECTED to Quantum Computing
    # Matches classical terms only when query mentions simulation, quantum concepts, or gate representations
    math_programming_terms = [
        "complex number", "complex numbers", "probability amplitude", "linear algebra", "tensor product",
        "hermitian", "matrix multiplication", "inner product", "outer product",
        "norm", "orthogonal", "vector space", "hilbert space", "unitary matrix",
        "pauli matrix", "matrix exponential", "python", "numpy", "scipy", "matrix", "matrices"
    ]
    quantum_connection_indicators = [
        "quantum", "qubit", "qubits", "gate", "gates", "state", "states",
        "superposition", "circuit", "circuits", "bloch", "qiskit"
    ]
    for m_term in math_programming_terms:
        if _matches_domain_term(m_term, query_lower):
            # If the query also mentions a quantum connection indicator
            if any(_matches_domain_term(conn, query_lower) for conn in quantum_connection_indicators):
                return True

    # Quantum Learning Platform Terms (only when explicitly referencing the platform, tutor, or quantum learning)
    quantum_learning_phrases = [
        "how do i learn quantum", "quantum learning", "quantum tutor", "help me with quantum",
        "practice quantum", "study quantum", "quantum curriculum", "quantum path",
        "learn quantum computing", "quantum roadmap"
    ]
    for ql_phrase in quantum_learning_phrases:
        if _matches_domain_term(ql_phrase, query_lower):
            return True

    # Context-aware follow-up check:
    # Only if there is an active previous quantum topic in the conversation session
    s_key = session_key or get_session_key(extra_context=extra_context)
    prev_topic = get_previous_topic(s_key, extra_context=extra_context)

    if prev_topic and prev_topic != "General":
        # Follow-up conversational pronouns and referential phrases directly referencing previous exchange
        referential_triggers = [
            "it", "its", "that", "this", "they", "them", "why", "how", "example",
            "different", "classical bit", "difference", "useful", "break rsa", "what about",
            "how does", "why is", "can you", "is it", "what happens", "explain", "implement",
            "show me", "give me an example", "why is it different"
        ]
        if any(_matches_domain_term(trig, query_lower) for trig in referential_triggers):
            return True

    return False


def resolve_topic(
    query: str,
    history: Optional[List[dict]] = None,
    extra_context: Optional[dict] = None,
    curriculum: Optional[list] = None,
    session_key: Optional[str] = None
) -> dict:
    """
    Resolves topic, intent, follow-up status, and topic relationships for the current user query.
    Differentiates short concept fragments (e.g. "RSA", "QFT", "Grover", "Bloch Sphere") from
    ambiguous follow-ups ("why?", "how?", "example", "why is it different?").
    """
    if not query:
        return {
            "topic": "Quantum Computing",
            "intent": "general",
            "is_follow_up": False,
            "previous_topic": None,
            "relationship": None
        }

    s_key = session_key or get_session_key(extra_context=extra_context)
    prev_topic = get_previous_topic(s_key, extra_context=extra_context)

    query_lower = query.strip().lower()

    # Define explicit concept maps
    explicit_concept = None
    intent = "explanation"

    if "application" in query_lower or "applications" in query_lower or "used for" in query_lower or "where is" in query_lower:
        if prev_topic and any(p in query_lower for p in ["its", "that", "this", "it"]):
            explicit_concept = f"Applications of {prev_topic}"
        else:
            explicit_concept = "Applications of Quantum Computing"
    elif "quantum computing" in query_lower or query_lower == "what is quantum computing":
        explicit_concept = "Quantum Computing"
    elif "rsa" in query_lower:
        explicit_concept = "RSA Encryption"
    elif "qft" in query_lower or "fourier" in query_lower:
        explicit_concept = "Quantum Fourier Transform"
    elif "shor" in query_lower:
        explicit_concept = "Shor's Algorithm"
    elif "grover" in query_lower:
        explicit_concept = "Grover's Algorithm"
    elif "bloch" in query_lower:
        explicit_concept = "Bloch Sphere"
    elif "hadamard" in query_lower or "h gate" in query_lower:
        explicit_concept = "Hadamard Gate"
    elif "bell" in query_lower:
        explicit_concept = "Bell States"
    elif "superposition" in query_lower:
        if prev_topic == "Quantum Entanglement" and any(k in query_lower for k in ["useful", "here", "relation", "how", "why"]):
            explicit_concept = "Quantum Entanglement"
        else:
            explicit_concept = "Quantum Superposition"
    elif "entanglement" in query_lower:
        explicit_concept = "Quantum Entanglement"
    elif "measurement" in query_lower or "collapse" in query_lower:
        explicit_concept = "Quantum Measurement"
    elif "qubit" in query_lower or "qubits" in query_lower:
        explicit_concept = "Qubits"
    elif "gate" in query_lower or "gates" in query_lower:
        explicit_concept = "Quantum Gates"
    elif "circuit" in query_lower or "circuits" in query_lower:
        explicit_concept = "Quantum Circuits"
    elif curriculum:
        for topic_dict in curriculum:
            topic_name = topic_dict.get("name", "").lower()
            topic_id = topic_dict.get("topic_id", "").lower()
            topic_name_clean = topic_name.replace("'s", "").replace("’s", "")
            topic_id_clean = topic_id.replace("_", " ").replace("s algorithm", "").replace("algorithm", "").strip()

            if (topic_name in query_lower or topic_id in query_lower or
                (topic_name_clean and topic_name_clean in query_lower) or
                (topic_id_clean and len(topic_id_clean) > 3 and topic_id_clean in query_lower)):
                explicit_concept = topic_dict["name"]
                break

    if explicit_concept:
        # Check if query expresses a relation to previous topic
        # NOTE: Only actual relationship words, NOT algorithm names like "shor"/"grover"
        referential_rel_triggers = ["relate", "relation", "vulnerable", "break", "differ", "difference", "useful", "connect", "why"]
        has_relation_trigger = prev_topic and any(trig in query_lower for trig in referential_rel_triggers)

        # Short fragments like "RSA", "QFT", "Grover" introducing a concept
        is_short_fragment = len(query_lower.split()) <= 3

        if has_relation_trigger and prev_topic and prev_topic.lower() != explicit_concept.lower():
            is_follow_up = True
            relationship = f"{explicit_concept} in relation to {prev_topic}"
        elif is_short_fragment:
            is_follow_up = False
            relationship = None
        else:
            is_follow_up = bool(prev_topic and any(p in query_lower for p in ["it", "its", "that", "this", "here", "why", "how"]))
            relationship = f"{explicit_concept}" if is_follow_up else None

        return {
            "topic": explicit_concept,
            "intent": intent,
            "is_follow_up": is_follow_up,
            "previous_topic": prev_topic,
            "relationship": relationship
        }

    # If NO explicit new concept matched:
    if prev_topic:
        if "difference" in query_lower or "different" in query_lower or "classical bit" in query_lower or "vs" in query_lower:
            intent = "comparison"
            relationship = "comparison to classical bit"
        elif "example" in query_lower or "instance" in query_lower:
            intent = "example"
            relationship = "concrete example"
        elif "vulnerable" in query_lower or "break" in query_lower:
            intent = "explanation"
            relationship = f"vulnerability of {prev_topic}"
        else:
            intent = "follow_up"
            relationship = "referential follow-up"

        return {
            "topic": prev_topic,
            "intent": intent,
            "is_follow_up": True,
            "previous_topic": prev_topic,
            "relationship": relationship
        }

    return {
        "topic": "Quantum Computing",
        "intent": "explanation",
        "is_follow_up": False,
        "previous_topic": None,
        "relationship": None
    }


def extract_topic_and_intent(
    query: str,
    extra_context: Optional[dict] = None,
    curriculum: Optional[list] = None,
    session_key: Optional[str] = None
) -> Tuple[str, str]:
    """
    Extracts detected topic and intent from the CURRENT user query with highest priority.
    Uses conversational context and referential resolution when pronouns or implicit follow-ups are used.
    """
    resolved = resolve_topic(
        query=query,
        history=None,
        extra_context=extra_context,
        curriculum=curriculum,
        session_key=session_key
    )
    return resolved["topic"], resolved["intent"]


def check_topic_drift(
    query: str,
    answer: str,
    current_topic: str,
    previous_topic: Optional[str] = None,
    is_follow_up: bool = False
) -> dict:
    """
    Checks if generated response addresses current topic vs previous topic.
    Heavily penalizes (< 60) wrong-topic answers to force LLM loop regeneration.
    """
    if not answer or not current_topic:
        return {"drift": False, "score": 100.0, "issue": None}

    ans_lower = answer.lower()
    curr_topic_lower = current_topic.lower()
    query_lower = query.lower()

    # Topic keyword expectations
    topic_keywords = {
        "rsa encryption": ["rsa", "factorization", "factoring", "public-key", "cryptography", "encryption", "prime"],
        "quantum fourier transform": ["qft", "fourier", "phase", "frequency"],
        "grover's algorithm": ["grover", "search", "oracle", "diffuser", "speedup", "quadratic"],
        "shor's algorithm": ["shor", "factor", "period", "modular"],
        "bloch sphere": ["bloch", "sphere", "axes", "vector", "polar", "azimuthal", "rotation"],
        "qubits": ["qubit", "qubits", "bit", "superposition", "state"],
        "hadamard gate": ["hadamard", "h gate", "superposition"],
        "quantum measurement": ["measurement", "collapse", "born rule", "eigenstate"],
        "quantum entanglement": ["entanglement", "entangled", "bell state", "cnot"],
        "quantum superposition": ["superposition", "linear combination", "amplitude"]
    }

    # Determine keywords for current topic
    expected_kw = None
    for top_k, kw_list in topic_keywords.items():
        if top_k in curr_topic_lower or curr_topic_lower in top_k:
            expected_kw = kw_list
            break

    if expected_kw:
        kw_found = any(kw in ans_lower for kw in expected_kw)
        if not kw_found:
            issue = f"Topic drift detected: Generated answer fails to discuss target topic '{current_topic}'."
            return {"drift": True, "score": 40.0, "issue": issue}

    if previous_topic and previous_topic.lower() != current_topic.lower() and not is_follow_up:
        prev_topic_lower = previous_topic.lower()
        if "shor" in prev_topic_lower and "rsa" in curr_topic_lower:
            if "rsa" not in ans_lower:
                issue = f"Topic drift detected: User asked about '{current_topic}', but response focused on previous topic '{previous_topic}'."
                return {"drift": True, "score": 40.0, "issue": issue}

    return {"drift": False, "score": 100.0, "issue": None}


def generate_dynamic_suggestions(
    query: str,
    concept: str,
    mode: str = "explain",
    learner_profile: Optional[dict] = None,
    extra_context: Optional[dict] = None,
    is_off_topic: bool = False
) -> List[str]:
    """
    Generates dynamic, context-aware suggested follow-up questions based primarily on the CURRENT topic.
    """
    if is_off_topic:
        return [
            "What is quantum computing?",
            "What is a qubit?",
            "What is quantum superposition?",
            "How do quantum gates work?"
        ]

    query_lower = query.lower() if query else ""
    concept_lower = concept.lower() if concept else ""

    if mode in ("circuit_assistant", "circuit_explain") or (extra_context and "circuit" in extra_context):
        return [
            "Why is the Hadamard (H) gate applied first in state preparation?",
            "How does CNOT create entanglement between control and target qubits?",
            "How do I simulate this circuit using AerSimulator in Qiskit?",
            "What is the statevector output of this circuit?"
        ]

    if mode == "quiz_analysis" or (extra_context and ("quiz" in extra_context or "responses" in extra_context)):
        return [
            "Explain the concepts behind my incorrect quiz answers.",
            "Give me a targeted practice problem to reinforce my weak topics.",
            "How do I prepare for advanced quantum algorithm quizzes?",
            "Quiz me again on quantum measurement and gates."
        ]

    elif "rsa" in query_lower or "rsa" in concept_lower:
        base_suggestions = [
            "Why is RSA vulnerable to Shor's algorithm?",
            "How does integer factorization break RSA encryption?",
            "What is Post-Quantum Cryptography (PQC)?",
            "What key size makes RSA vulnerable to quantum attack?"
        ]
    elif "qft" in query_lower or "fourier" in query_lower or "qft" in concept_lower:
        base_suggestions = [
            "How does QFT perform period finding in Shor's algorithm?",
            "What is the circuit representation of the Quantum Fourier Transform?",
            "How does QFT achieve an exponential speedup over classical FFT?",
            "What is the difference between QFT and QPE (Quantum Phase Estimation)?"
        ]
    elif "shor" in query_lower or "shor" in concept_lower:
        base_suggestions = [
            "How does period finding work?",
            "Why does Shor threaten RSA?",
            "What role does the QFT play?",
            "What hardware requirements are needed to run Shor's algorithm?"
        ]
    elif "bloch" in query_lower or "bloch" in concept_lower:
        base_suggestions = [
            "How does the Hadamard gate rotate the state?",
            "What do the X, Y and Z axes represent?",
            "How do RX, RY and RZ change the state?",
            "How is a pure qubit state represented on the Bloch sphere?"
        ]
    elif "measurement" in query_lower or "measurement" in concept_lower or "collapse" in query_lower:
        base_suggestions = [
            "What is the Born rule?",
            "Why does measurement destroy the original superposition?",
            "Can a qubit be measured in another basis?",
            "How do measurement operations work in Qiskit?"
        ]
    elif "grover" in query_lower or "grover" in concept_lower:
        base_suggestions = [
            "How does phase inversion amplify target state probability?",
            "What is the quadratic speedup of Grover's search?",
            "What is the role of the quantum oracle in Grover's algorithm?",
            "How is the diffuser operator constructed?"
        ]
    elif "entanglement" in query_lower or "entanglement" in concept_lower or "bell" in query_lower or "bell" in concept_lower:
        base_suggestions = [
            "How do you create a Bell state using H and CNOT gates?",
            "Can entanglement be used for faster-than-light communication?",
            "What is quantum teleportation?",
            "What happens when you measure one entangled qubit?"
        ]
    elif "superposition" in query_lower or "superposition" in concept_lower:
        base_suggestions = [
            "How does the Hadamard gate create superposition?",
            "Why does measurement collapse superposition?",
            "What is state vector normalization?",
            "Show me a 2-qubit superposition circuit example."
        ]
    elif "qubit" in query_lower or "qubits" in concept_lower:
        base_suggestions = [
            "How does a qubit differ from a classical bit?",
            "What is the Bloch sphere representation of a qubit?",
            "How do single-qubit gates change qubit states?",
            "What are state vector probability amplitudes?"
        ]
    elif "gate" in query_lower or "gates" in concept_lower or "hadamard" in query_lower:
        base_suggestions = [
            "What is the matrix representation of the Hadamard gate?",
            "How does the CNOT (Controlled-NOT) gate operate?",
            "What is the difference between Pauli-X, Y, and Z gates?",
            "How do gate rotations work on the Bloch sphere?"
        ]
    elif "applications" in concept_lower or "application" in query_lower:
        base_suggestions = [
            "How is quantum computing used in drug discovery?",
            "What is quantum optimization?",
            "Can quantum computers improve cryptography?",
            "What problems are quantum computers good at?"
        ]
    elif "quantum computing" in concept_lower or "quantum computing" in query_lower:
        base_suggestions = [
            "How is quantum computing different from classical computing?",
            "What is a qubit?",
            "Where is quantum computing used?",
            "What is quantum advantage?"
        ]
    else:
        topic_name = concept if concept else "quantum concepts"
        base_suggestions = [
            f"Why is {topic_name} fundamental to quantum computing?",
            f"Show me a Qiskit code example for {topic_name}.",
            f"Quiz me on {topic_name}.",
            f"What are the prerequisites for {topic_name}?"
        ]

    if learner_profile and learner_profile.get("topic_weaknesses"):
        weak_topic = learner_profile["topic_weaknesses"][0].replace("_", " ").title()
        if len(base_suggestions) >= 4:
            base_suggestions[3] = f"Practice my weak topic: {weak_topic}"

    return base_suggestions


def build_context(
    query: str,
    mode: str = "explain",
    learner_profile: Optional[dict] = None,
    recommendation_context: Optional[dict] = None,
    curriculum: Optional[list] = None,
    project_root: Optional[str] = None,
    extra_context: Optional[dict] = None
) -> dict:
    """
    Constructs a structured, grounded educational context object for the LLM prompt.
    Integrates Phase 3 Learner Profiles, Phase 4 Recommendations, deterministic Circuit Validation,
    and deterministic Quiz Analysis.
    """
    if curriculum is None:
        curriculum = load_curriculum_topics(project_root)
        
    if extra_context is None:
        extra_context = {}

    s_key = get_session_key(learner_profile, extra_context)
    history = get_conversation_history(s_key)

    target_mode = mode if mode in SUPPORTED_MODES else "explain"

    resolved = resolve_topic(
        query=query,
        history=history,
        extra_context=extra_context,
        curriculum=curriculum,
        session_key=s_key
    )
    detected_topic = resolved["topic"]
    detected_intent = resolved["intent"]
        
    context = {
        "query": query,
        "mode": target_mode,
        "skill_level": "Intermediate",
        "performance_band": "Unavailable",
        "risk_status": "Unavailable",
        "predicted_performance": None,
        "weak_topics": [],
        "developing_topics": [],
        "strong_topics": [],
        "current_topic": detected_topic,
        "intent": detected_intent,
        "is_follow_up": resolved["is_follow_up"],
        "previous_topic": resolved["previous_topic"],
        "relationship": resolved["relationship"],
        "current_recommendation": None,
        "curriculum_grounding": None,
        "circuit_validation": None,
        "quiz_analysis": None,
        "learner_id": None,
        "session_key": s_key,
        "history": history
    }
    
    # 1. Integrate Phase 3 Learner Profile context (strictly grounded)
    if learner_profile:
        context["skill_level"] = learner_profile.get("skill_level", "Intermediate")
        context["performance_band"] = learner_profile.get("performance_band", "Moderate")
        context["risk_status"] = learner_profile.get("risk_status", "Low Risk")
        context["predicted_performance"] = learner_profile.get("predicted_performance")
        context["weak_topics"] = learner_profile.get("topic_weaknesses", [])
        context["developing_topics"] = learner_profile.get("topic_developing", [])
        context["strong_topics"] = learner_profile.get("topic_strengths", [])
        context["learner_id"] = learner_profile.get("learner_id")
        
    # 2. Integrate Phase 4 Recommendation context
    if recommendation_context:
        nba = recommendation_context.get("next_best_action")
        if nba:
            context["current_recommendation"] = nba.get("action")
            
    # 3. Match query to curriculum topic grounding
    query_lower = query.lower()
    for topic_dict in curriculum:
        topic_name = topic_dict.get("name", "").lower()
        topic_id = topic_dict.get("topic_id", "").lower()
        topic_name_clean = topic_name.replace("'s", "").replace("’s", "")
        topic_id_clean = topic_id.replace("_", " ").replace("s algorithm", "").replace("algorithm", "").strip()

        if (topic_name in query_lower or topic_id in query_lower or
            (topic_name_clean and topic_name_clean in query_lower) or
            (topic_id_clean and len(topic_id_clean) > 3 and topic_id_clean in query_lower)):
            context["curriculum_grounding"] = {
                "name": topic_dict["name"],
                "difficulty": topic_dict.get("difficulty", "Intermediate"),
                "prerequisites": topic_dict.get("prerequisites", []),
                "description": topic_dict.get("description", "")
            }
            break

    # 4. Deterministic Circuit Validation Grounding
    circuit_data = extra_context.get("circuit") or extra_context.get("circuit_data")
    if target_mode in ("circuit_assistant", "circuit_explain") or circuit_data:
        goal = extra_context.get("intended_goal") or extra_context.get("goal", "general")
        validator = CircuitValidator()
        validation_input = circuit_data if circuit_data else query
        context["circuit_validation"] = validator.validate_circuit(validation_input, intended_goal=goal)

    # 5. Deterministic Quiz Analysis Grounding
    quiz_data = extra_context.get("quiz") or extra_context.get("quiz_data") or extra_context.get("responses")
    if target_mode == "quiz_analysis" or quiz_data:
        analyzer = QuizAnalyzer()
        quiz_input = quiz_data if quiz_data else extra_context
        context["quiz_analysis"] = analyzer.analyze_quiz(quiz_input)
            
    return context


def build_system_prompt(context: dict) -> str:
    """Constructs system prompt instructions for the generative tutor LLM."""
    mode = context["mode"]
    skill_level = context["skill_level"]
    query = context.get("query", "")
    history = context.get("history", [])
    is_follow_up = context.get("is_follow_up", False)
    relationship = context.get("relationship")

    prompt = f"""You are an expert AI Quantum Computing Tutor.

Your job is to teach quantum computing clearly, accurately, and conversationally.
You should behave like an excellent human tutor rather than a search engine or a rigid question-answer template.
You can explain concepts from beginner to advanced levels, answer follow-up questions, compare concepts, provide examples, explain mathematics, walk through algorithms, explain quantum circuits and gates, help with Qiskit/code, provide hints, and analyze learner mistakes.
Always answer the user's actual question.
Never force an unrelated quantum concept into an answer simply because it is a quantum topic.

CRITICAL CONTEXT HANDLING:
- If the current question is about a NEW quantum topic (NOT a follow-up to the previous message),
  disregard all previous conversation history and answer ONLY based on the current question.
- Use previous history only when the current question directly references, compares to, or asks about
  something from the immediately previous exchange.
- Never let unrelated earlier conversation contaminate your answer about a new topic.

VERIFIED LEARNER GROUNDED CONTEXT:
- Learner ID: {context.get('learner_id', 'Unavailable')}
- Skill Level: {skill_level}
- Risk Status: {context['risk_status']}
- Predicted Performance: {context['predicted_performance'] if context['predicted_performance'] is not None else 'Unavailable'}
- Weak Topics: {', '.join(context['weak_topics']) if context['weak_topics'] else 'None'}
- Strong Topics: {', '.join(context['strong_topics']) if context['strong_topics'] else 'None'}
- Current Topic Focus: {context['current_topic']}
- User Query: "{query}"
"""

    # GATE: Only include conversation history for genuine follow-ups
    if history and is_follow_up:
        history_formatted = []
        # Include only last 2 most relevant turns (not 5) to reduce context noise
        for turn in history[-2:]:
            ans_snippet = turn['answer'][:250].replace('\n', ' ')
            history_formatted.append(f"User: {turn['query']}\nTutor ({turn['concept']}): {ans_snippet}...")
        prompt += f"\nRECENT CONVERSATION CONTEXT (follow-up to: {relationship}):\n" + "\n".join(history_formatted) + "\n"
    elif history and not is_follow_up:
        # Explicitly remind model that this is a new topic
        prompt += f"\nNOTE: Current question starts a NEW topic. Ignore previous conversation context above.\n"

    prompt += f"""
LEARNER ADAPTATION ({skill_level.upper()} LEVEL):
- If Beginner: Use simple language, intuitive explanations, minimal mathematics, and real-world analogies.
- If Intermediate: Provide concepts + mathematics, examples, circuits, and algorithm intuition.
- If Advanced: Provide mathematical detail, formal linear algebra notation, complexity, implementation details, and research-level context.

TEACHING STYLE & CONCISENESS:
Act like a human tutor giving focused, direct instruction.
1. Answer Length & Density:
   - For standard questions, provide a concise, direct answer: aim for 80–150 words (approximately 180 words maximum).
   - Answer directly in 1–2 well-structured paragraphs.
   - Do NOT force every answer into a rigid multi-heading format, and do NOT force unnecessary equations, examples, misconceptions, or next steps into ordinary explanations.
   - Allow longer, detailed responses (>180 words) ONLY when:
     * The user explicitly asks for detail (e.g., "in detail", "deep dive", "thoroughly", "step by step", "comprehensive"), OR
     * The user asks a multi-part question, OR
     * The topic genuinely requires mathematical proofs or multi-step derivations.
2. Lightweight Structure:
   - Simple / introductory questions: Direct, plain explanation in 1–2 short paragraphs.
   - Technical questions: Brief conceptual explanation with an equation or short example only when helpful.
   - Multi-part questions: Use clear Markdown headings to separate the distinct parts requested by the user.

ACCURACY & ANTI-HALLUCINATION RULES:
- Accuracy is more important than sounding confident. Never invent algorithms, gates, experimental results, learner scores, quiz results, circuit outputs, citations, or hardware capabilities.
- Never claim quantum computers "try all possibilities simultaneously" or "do all computations at once." Explain speedup through superposition and constructive/destructive interference.
- Never claim entanglement enables faster-than-light communication.
- Never claim quantum computers universally outperform classical computers.
- MULTI-PART QUESTIONS: Detect and explicitly answer ALL parts using clear Markdown section headings (e.g. `## What is Quantum Computing?` and `## Applications of Quantum Computing`).

CIRCUIT ASSISTANT RULE:
When the user asks about a quantum circuit, DETERMINISTIC CIRCUIT VALIDATION IS THE SOURCE OF TRUTH for invalid gates, invalid qubit indices, control/target errors, structural circuit errors, known circuit patterns, and exact corrected circuit pieces.
Do NOT override deterministic validator results. If validator says valid = false, explain that exact correction rather than inventing another correction.

QUIZ ASSISTANT RULE:
Python/deterministic analysis IS THE SOURCE OF TRUTH for scores, percentages, correct/incorrect counts, weak topics, and strong topics.
NEVER calculate or invent the score. Explain why incorrect answers were wrong, clarify the correct quantum concepts, and recommend targeted practice.

MODE INSTRUCTIONS ({mode.upper()}):
- explain / chat: Provide clear conceptual explanations tailored to {skill_level} difficulty. Keep ordinary answers direct and concise (80–150 words).
- hint: Provide progressive hints WITHOUT revealing the full direct answer immediately.
- debug: Identify code bugs, explain why they occur, and provide corrected Qiskit syntax.
- code_explain: Provide step-by-step code walkthroughs for Qiskit circuits.
- circuit_explain / circuit_assistant: Provide grounded circuit guidance based on deterministic validation.
- quiz_analysis: Explain verified quiz scores and topic performance. Use provided deterministic quiz analysis payload.
- practice: Provide a guided conceptual or coding practice problem with solutions.
"""

    if context.get("circuit_validation"):
        prompt += f"\nVERIFIED CIRCUIT VALIDATION RESULT:\n{json.dumps(context['circuit_validation'], indent=2)}\n"

    if context.get("quiz_analysis"):
        prompt += f"\nVERIFIED QUIZ ANALYSIS RESULT:\n{json.dumps(context['quiz_analysis'], indent=2)}\n"

    prompt += f"""
RESPONSE REQUIREMENTS:
You MUST respond strictly in valid JSON format matching this schema:
{{
    "answer": "Direct, concise Markdown response (80-150 words for standard questions, max ~180 words unless detail explicitly requested) addressing user query about {context['current_topic']}",
    "concept": "{context['current_topic']}",
    "difficulty": "{skill_level}",
    "mode": "{mode}",
    "hint": "Actionable hint or key insight",
    "next_step": "Suggested next learning activity",
    "confidence": 0.95,
    "suggestions": ["Topic-specific follow-up question 1", "Topic-specific follow-up question 2", "Topic-specific follow-up question 3"]
}}
"""
    return prompt


def build_critic_system_prompt() -> str:
    """Constructs system prompt instructions for the AI Critic LLM."""
    return """You are an AI Critic for a Quantum Computing Educational Platform.
Evaluate the candidate AI tutor response on pedagogical accuracy, relevance to the exact question asked, topic correctness, appropriate conciseness (80–150 words normally, ~180 words max unless in-depth detail was explicitly requested), clarity, factual consistency, and freedom from quantum misconceptions.
Do NOT penalize a response for brevity if it accurately and directly answers the question without redundant padding.

Respond strictly in valid JSON format matching this schema:
{
    "score": 88.0,
    "accuracy": 90.0,
    "relevance": 90.0,
    "difficulty_fit": 85.0,
    "clarity": 90.0,
    "completeness": 85.0,
    "issues": ["List of specific issues if any"],
    "should_improve": false
}
"""


def parse_json_safely(raw_text: str) -> Optional[dict]:
    """Parses JSON text string safely with Markdown code block stripping."""
    if not raw_text or not isinstance(raw_text, str):
        return None
        
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except Exception:
        return None


def fallback_critic(candidate: dict, context: dict) -> dict:
    """
    Deterministic Fallback Critic layer executing when LLM Critic fails or returns invalid JSON.
    """
    answer = candidate.get("answer", "")
    query = context.get("query", "").lower()
    concept = context.get("current_topic", "").lower()
    score = 88.0
    issues = []
    
    if not answer or len(answer.strip()) < 15:
        score = 50.0
        issues.append("Answer response is empty or excessively short.")
    elif "draft requiring refinement" in answer.lower():
        score = 70.0
        issues.append("Response requires technical refinement.")
        
    # Check for misconceptions
    if "try all possibilities at once" in answer.lower() or "try every answer at once" in answer.lower():
        score = 65.0
        issues.append("Response contains common misconception about parallel execution.")

    if "faster than light" in answer.lower() and "cannot" not in answer.lower() and "not" not in answer.lower():
        score = 60.0
        issues.append("Response incorrectly claims faster-than-light communication.")

    # 1. Detect template substitution bug
    if "allows quantum systems to exist in linear combinations" in answer.lower():
        if not any(k in query or k in concept for k in ("superposition", "qubit", "linear combination")):
            score = 30.0
            issues.append("Response uses generic superposition template for an unrelated topic.")

    # 2. Check multi-part queries
    if "quantum computing" in query and ("application" in query or "applications" in query):
        if "application" not in answer.lower() and "applications" not in answer.lower():
            score = 50.0
            issues.append("User asked about quantum computing and applications, but applications were omitted.")

    # 3. Check topic relevance for specific keywords
    if "shor" in query and "factor" not in answer.lower() and "shor" not in answer.lower():
        score = 40.0
        issues.append("Answer fails to explain Shor's algorithm or integer factorization.")

    # 4. Check Topic Drift
    prev_topic = context.get("previous_topic")
    is_fu = context.get("is_follow_up", False)
    drift_info = check_topic_drift(
        query=context.get("query", ""),
        answer=answer,
        current_topic=context.get("current_topic", ""),
        previous_topic=prev_topic,
        is_follow_up=is_fu
    )
    if drift_info["drift"]:
        score = min(score, drift_info["score"])
        if drift_info["issue"]:
            issues.append(drift_info["issue"])
        
    return {
        "score": score,
        "accuracy": score,
        "relevance": score,
        "difficulty_fit": score,
        "clarity": score,
        "completeness": score,
        "issues": issues,
        "should_improve": score < QUALITY_THRESHOLD,
        "critic_type": "deterministic_fallback"
    }


def critique_response(
    candidate: dict,
    context: dict,
    llm_client: LLMClient
) -> dict:
    """
    Evaluates candidate response via LLM Critic or Fallback Critic.
    """
    system_prompt = build_critic_system_prompt()
    user_prompt = f"Evaluate this tutor response for query: '{context['query']}'"
    
    critique_dict = None
    try:
        critique_text = llm_client.evaluate_critique(system_prompt, user_prompt, candidate, context)
        critique_dict = parse_json_safely(critique_text)
        
        if critique_dict and "score" in critique_dict:
            critique_dict["score"] = float(critique_dict["score"])
            critique_dict["should_improve"] = critique_dict["score"] < QUALITY_THRESHOLD
            critique_dict["critic_type"] = "llm_critic"
    except Exception:
        pass
        
    if not critique_dict:
        critique_dict = fallback_critic(candidate, context)

    # Post-process with deterministic topic-drift check
    drift_info = check_topic_drift(
        query=context.get("query", ""),
        answer=candidate.get("answer", ""),
        current_topic=context.get("current_topic", ""),
        previous_topic=context.get("previous_topic"),
        is_follow_up=context.get("is_follow_up", False)
    )
    if drift_info["drift"]:
        critique_dict["score"] = min(float(critique_dict.get("score", 100.0)), drift_info["score"])
        critique_dict["should_improve"] = True
        if "issues" not in critique_dict:
            critique_dict["issues"] = []
        if drift_info["issue"] and drift_info["issue"] not in critique_dict["issues"]:
            critique_dict["issues"].append(drift_info["issue"])

    return critique_dict


def tutor(
    query: str,
    mode: str = "explain",
    learner_profile: Optional[dict] = None,
    recommendation_context: Optional[dict] = None,
    curriculum: Optional[list] = None,
    llm_client: Optional[LLMClient] = None,
    use_mock: bool = False,
    extra_context: Optional[dict] = None
) -> dict:
    """
    Main entry point for AI Quantum Tutor executing the Bounded Loop Engineering workflow.
    
    Workflow:
        CONTEXT -> RELEVANCE GATE -> EXECUTION -> CRITIC -> EXIT CONDITION -> IMPROVE / DELIVER
    """
    if llm_client is None:
        llm_client = LLMClient(use_mock=use_mock)
        
    if curriculum is None:
        curriculum = load_curriculum_topics()

    s_key = get_session_key(learner_profile, extra_context)

    # 1. Relevance / Intent Gate Check (BEFORE normal answer-generation logic)
    if not is_quantum_or_learning_query(query, mode=mode, extra_context=extra_context, curriculum=curriculum, session_key=s_key):
        off_topic_suggestions = generate_dynamic_suggestions(query, "General", mode, learner_profile, extra_context, is_off_topic=True)
        return {
            "answer": "That's outside the scope of the Quantum Tutor. QURIO specializes in quantum computing and quantum algorithms, including qubits, superposition, entanglement, quantum gates, and circuits. For example, you could ask: 'How does a Hadamard gate create superposition?'",
            "concept": "General",
            "difficulty": learner_profile.get("skill_level", "Intermediate") if learner_profile else "Intermediate",
            "mode": mode,
            "hint": "Try asking a question about qubits, superposition, quantum circuits, or algorithms.",
            "next_step": "Ask a quantum computing question or try a practice quiz.",
            "confidence": 1.0,
            "quality_score": 100.0,
            "iterations": 1,
            "is_off_topic": True,
            "suggestions": off_topic_suggestions
        }

    # 2. Build Grounded Context
    context = build_context(
        query=query,
        mode=mode,
        learner_profile=learner_profile,
        recommendation_context=recommendation_context,
        curriculum=curriculum,
        extra_context=extra_context
    )
    system_prompt = build_system_prompt(context)
    
    best_response = None
    best_score = -1.0
    best_critique = None
    
    iteration = 1
    improvement_feedback = ""
    
    dynamic_suggestions = generate_dynamic_suggestions(
        query=query,
        concept=context["current_topic"],
        mode=mode,
        learner_profile=learner_profile,
        extra_context=extra_context,
        is_off_topic=False
    )
    context["suggestions"] = dynamic_suggestions

    while iteration <= MAX_ITERATIONS:
        context["iteration"] = iteration
        user_prompt = f"USER QUESTION: {query}"
        if improvement_feedback:
            user_prompt += f"\n\nIMPROVEMENT FEEDBACK FROM PREVIOUS CRITIC:\n{improvement_feedback}"
            
        # Execution (Generate Candidate Response)
        raw_completion = llm_client.generate_completion(system_prompt, user_prompt, context)
        parsed_candidate = parse_json_safely(raw_completion)
        
        if not parsed_candidate or "answer" not in parsed_candidate:
            from src.tutor.mock_llm import _generate_explain_answer
            fb_ans, fb_hint, fb_next = _generate_explain_answer(query, context["current_topic"], context["skill_level"])
            parsed_candidate = {
                "answer": fb_ans,
                "concept": context["current_topic"],
                "difficulty": context["skill_level"],
                "mode": context["mode"],
                "hint": fb_hint,
                "next_step": fb_next,
                "confidence": 0.80,
                "suggestions": dynamic_suggestions
            }
            
        # Critic (Evaluate Response)
        critique = critique_response(parsed_candidate, context, llm_client)
        score = float(critique.get("score", 85.0))
        
        if score > best_score:
            best_score = score
            best_response = parsed_candidate.copy()
            best_critique = critique.copy()
            
        if score >= QUALITY_THRESHOLD:
            break
            
        issues = critique.get("issues", [])
        improvement_feedback = f"Previous iteration score: {score:.1f}/100. Issues to address: {', '.join(issues)}"
        iteration += 1
        
    final_payload = best_response if best_response else parsed_candidate
    final_payload["quality_score"] = best_score
    final_payload["iterations"] = min(iteration, MAX_ITERATIONS)
    final_payload["critic_type"] = best_critique.get("critic_type", "deterministic_fallback") if best_critique else "deterministic_fallback"
    
    if not final_payload.get("suggestions") or final_payload.get("suggestions") == ["Suggested follow-up 1", "Suggested follow-up 2", "Suggested follow-up 3"]:
        final_payload["suggestions"] = dynamic_suggestions

    if context.get("circuit_validation"):
        final_payload["circuit_validation"] = context["circuit_validation"]
    if context.get("quiz_analysis"):
        final_payload["quiz_analysis"] = context["quiz_analysis"]
        
    # Record conversation turn in store for valid multi-turn chat
    add_conversation_turn(
        session_key=s_key,
        query=query,
        concept=context["current_topic"],
        answer=final_payload["answer"]
    )

    return final_payload
