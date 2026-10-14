'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  Bot,
  Check,
  CheckCircle2,
  ChevronRight,
  Lightbulb,
  Loader2,
  MessageCircle,
  RotateCcw,
  Send,
  Sparkles,
  Target,
  Zap,
} from 'lucide-react';

import AtlasNav from '../shared/AtlasNav';
import Stickman from '../roadmap/Stickman';
import { CIRCUIT_ACCENT } from '../circuit/circuitData';
import { askTutorBackend, checkTutorBackendHealth } from './tutorClient';
import TutorMarkdownRenderer from './TutorMarkdownRenderer';

type GoalId = 'foundations' | 'circuit' | 'entanglement';

interface WorkflowStep {
  title: string;
  detail: string;
  action: string;
  href: string;
  tutor: string;
}

interface Goal {
  id: GoalId;
  label: string;
  description: string;
  time: string;
  steps: WorkflowStep[];
}

interface ChatMessage {
  id: string;
  role: 'user' | 'tutor';
  text: string;
  concept?: string;
  hint?: string;
  quality?: number;
  isAi?: boolean;
}

const GOALS: Goal[] = [
  {
    id: 'foundations',
    label: 'Understand the basics',
    description: 'Build a mental model for qubits, measurement, and superposition.',
    time: '15 min',
    steps: [
      { title: 'Meet the qubit', detail: 'Start with the smallest unit of quantum information.', action: 'Open the roadmap', href: '/roadmap', tutor: 'A qubit is not a tiny classical bit. Before measurement, it can hold a weighted combination of |0⟩ and |1⟩.' },
      { title: 'Make a superposition', detail: 'Use a Hadamard gate to create a 50/50 state.', action: 'Try it in Circuit Studio', href: '/circuit', tutor: 'Try H on q₀. The key idea is that the probabilities become balanced, not that the qubit is secretly choosing one answer.' },
      { title: 'Check your intuition', detail: 'Play one short challenge to make the idea stick.', action: 'Play Qurio Qubit', href: '/qubit', tutor: 'Explain the result in your own words: what changed before measurement, and what did the measurement reveal?' },
    ],
  },
  {
    id: 'circuit',
    label: 'Build your first circuit',
    description: 'Place gates, run shots, and read the circuit like a programmer.',
    time: '20 min',
    steps: [
      { title: 'Choose a gate', detail: 'Learn what H, X, Y, and Z each change.', action: 'Open the gate editor', href: '/circuit', tutor: 'Start with H because its effect is easy to see in the measurement panel. X is a good second step: it flips the basis state.' },
      { title: 'Run and compare', detail: 'Run 1,024 shots, then change one gate and run again.', action: 'Run a circuit', href: '/circuit', tutor: 'A useful experiment changes one thing at a time. Predict the histogram first, then compare your prediction with the shots.' },
      { title: 'Read the code', detail: 'Connect the visual board to Qiskit syntax.', action: 'Study the generated code', href: '/circuit', tutor: 'The circuit is a sequence of operations over time. Read each column from left to right, just like a small program.' },
    ],
  },
  {
    id: 'entanglement',
    label: 'Understand entanglement',
    description: 'Build a Bell pair and separate correlation from coincidence.',
    time: '25 min',
    steps: [
      { title: 'Create uncertainty', detail: 'Put the control qubit into superposition.', action: 'Open Circuit Studio', href: '/circuit', tutor: 'The first H creates two possible branches. Entanglement begins when a later operation ties another qubit to those branches.' },
      { title: 'Connect two wires', detail: 'Use CNOT in the next column to make a Bell pair.', action: 'Build the Bell pair', href: '/circuit', tutor: 'CNOT does not copy an unknown qubit. It correlates the target with the control, so their measured results agree.' },
      { title: 'Test the correlation', detail: 'Compare individual odds with pairwise agreement.', action: 'Run the challenge', href: '/circuit', tutor: 'Each qubit looks random alone, but the pair is predictable together. That contrast is the heart of entanglement.' },
    ],
  },
];

const DEFAULT_PROMPTS = ['Why does H create superposition?', 'Give me a hint for this step', 'What should I try next?'];

export default function TutorWorkflow() {
  const [goalId, setGoalId] = useState<GoalId>('foundations');
  const [stepIndex, setStepIndex] = useState(0);
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompts, setPrompts] = useState<string[]>(DEFAULT_PROMPTS);
  const [isGenerating, setIsGenerating] = useState(false);
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);
  const chatBodyRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat body to bottom when messages change or AI is generating
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTo({ top: chatBodyRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, isGenerating]);

  const goal = GOALS.find((item) => item.id === goalId) ?? GOALS[0];
  const step = goal.steps[stepIndex];
  const completionKey = `${goal.id}-${stepIndex}`;

  // Check backend health on initial load
  useEffect(() => {
    let mounted = true;
    checkTutorBackendHealth().then((connected) => {
      if (mounted) setBackendConnected(connected);
    });
    return () => {
      mounted = false;
    };
  }, []);

  // When step or goal changes, reset conversation with step's foundational tutor message
  useEffect(() => {
    setMessages([
      {
        id: `step-init-${goalId}-${stepIndex}`,
        role: 'tutor',
        text: step.tutor,
        isAi: false,
      },
    ]);
    setPrompts(DEFAULT_PROMPTS);
  }, [goalId, stepIndex, step.tutor]);

  const chooseGoal = (id: GoalId) => {
    setGoalId(id);
    setStepIndex(0);
  };

  const markComplete = () => {
    setCompleted((previous) => new Set(previous).add(completionKey));
    setStepIndex((current) => Math.min(current + 1, goal.steps.length - 1));
  };

  const ask = async (prompt = question) => {
    const trimmed = prompt.trim();
    if (!trimmed || isGenerating) return;

    setQuestion('');
    const userMsgId = `user-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: 'user',
      text: trimmed,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsGenerating(true);

    try {
      const reply = await askTutorBackend({
        question: trimmed,
        goal: goal.label,
        stepTitle: step.title,
        stepDetail: step.detail,
        stepAction: step.action,
        learnerId: 'LEARNER_0001',
      });

      // Update connection status based on successful AI answer
      if (reply.isAi) {
        setBackendConnected(true);
      }

      const tutorMsg: ChatMessage = {
        id: `tutor-${Date.now()}`,
        role: 'tutor',
        text: reply.answer,
        concept: reply.concept,
        hint: reply.hint,
        quality: reply.quality_score,
        isAi: reply.isAi,
      };

      setMessages((prev) => [...prev, tutorMsg]);

      // If AI returned dynamic follow-up suggestions, display them
      if (reply.suggestions && reply.suggestions.length > 0) {
        setPrompts(reply.suggestions.slice(0, 3));
      }
    } catch {
      // Fallback
      setMessages((prev) => [
        ...prev,
        {
          id: `tutor-${Date.now()}`,
          role: 'tutor',
          text: `Keep this step concrete: ${step.detail}. Suggested action: "${step.action}".`,
          isAi: false,
        },
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="tutor-page">
      <AtlasNav />
      <main className="tutor-shell">
        <header className="tutor-hero">
          <div>
            <div className="tutor-kicker"><Sparkles size={14} /> Guided learning loop</div>
            <h1>Learn quantum computing <span>one useful move at a time.</span></h1>
            <p>Choose a goal, take the next action, then ask QurioSage for help grounded in exactly where you are.</p>
          </div>
          <div className="tutor-hero-badge"><Target size={18} /><strong>{completed.size}</strong><span>steps explored</span></div>
        </header>

        <div className="tutor-layout">
          <aside className="tutor-goals atlas-card">
            <div className="tutor-section-label">Choose your goal</div>
            {GOALS.map((item) => (
              <button key={item.id} type="button" className={`tutor-goal ${goalId === item.id ? 'is-active' : ''}`} onClick={() => chooseGoal(item.id)}>
                <span><strong>{item.label}</strong><small>{item.description}</small></span>
                <ChevronRight size={16} />
              </button>
            ))}
            <div className="tutor-goal-meta"><span>{goal.time}</span><span>{goal.steps.length} steps</span></div>
          </aside>

          <section className="tutor-workflow">
            <div className="tutor-progress-head"><div><div className="tutor-section-label">Your workflow</div><h2>{goal.label}</h2></div><span>{Math.min(stepIndex + 1, goal.steps.length)} / {goal.steps.length}</span></div>
            <div className="tutor-progress-bar"><span style={{ width: `${Math.max(8, ((stepIndex + 1) / goal.steps.length) * 100)}%` }} /></div>
            <div className="tutor-steps">
              {goal.steps.map((item, index) => {
                const done = completed.has(`${goal.id}-${index}`);
                return <button key={item.title} type="button" className={`tutor-step ${index === stepIndex ? 'is-current' : ''} ${done ? 'is-done' : ''}`} onClick={() => setStepIndex(index)}><span className="tutor-step-number">{done ? <Check size={15} /> : index + 1}</span><span><strong>{item.title}</strong><small>{item.detail}</small></span></button>;
              })}
            </div>
            <div className="tutor-action atlas-card">
              <div className="tutor-action-copy"><span className="tutor-section-label">Now</span><h3>{step.title}</h3><p>{step.detail}</p></div>
              <div className="tutor-action-buttons"><Link href={step.href} className="btn-atlas-coral">{step.action} <ArrowRight size={15} /></Link><button type="button" className="btn-atlas-ghost" onClick={markComplete}><CheckCircle2 size={15} /> Mark complete</button></div>
            </div>
          </section>

          <aside className="tutor-chat atlas-card">
            <div className="tutor-chat-head">
              <div className="tutor-avatar"><Bot size={18} /></div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <strong>QurioSage</strong>
                  {backendConnected && (
                    <span
                      title="Connected to Python Quantum AI Tutor backend"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 3,
                        padding: '2px 6px',
                        borderRadius: 999,
                        fontSize: 9,
                        fontWeight: 700,
                        background: '#DCFCE7',
                        color: '#166534',
                      }}
                    >
                      <Zap size={10} /> AI LIVE
                    </span>
                  )}
                </div>
                <small>{backendConnected ? 'Quantum AI Intelligence Engine' : 'Context-aware tutor'}</small>
              </div>
              <Lightbulb size={17} color={CIRCUIT_ACCENT} />
            </div>

            <div className="tutor-chat-body" ref={chatBodyRef}>
              {messages.map((item) => (
                item.role === 'user' ? (
                  <div className="tutor-question" key={item.id}>
                    {item.text}
                  </div>
                ) : (
                  <div className="tutor-message" key={item.id} style={{ marginBottom: 12 }}>
                    <Stickman pose="teach" size={48} accent={CIRCUIT_ACCENT} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      {item.concept && (
                        <div style={{ fontSize: 10, fontWeight: 700, color: '#D97706', textTransform: 'uppercase', marginBottom: 2 }}>
                          {item.concept} {item.quality ? `• Quality: ${Math.round(item.quality)}%` : ''}
                        </div>
                      )}
                      <TutorMarkdownRenderer content={item.text} />
                    </div>
                  </div>
                )
              ))}

              {isGenerating && (
                <div className="tutor-message" style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#9A710B', fontSize: 12 }}>
                  <Loader2 size={14} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                  <span>QurioSage is analyzing quantum concept...</span>
                </div>
              )}
            </div>

            <div className="tutor-prompts">
              {prompts.map((prompt) => (
                <button key={prompt} type="button" onClick={() => ask(prompt)} disabled={isGenerating}>
                  {prompt}
                </button>
              ))}
            </div>

            <form className="tutor-input" onSubmit={(event) => { event.preventDefault(); ask(); }}>
              <input
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask about this step..."
                aria-label="Ask the AI tutor"
                disabled={isGenerating}
              />
              <button type="submit" aria-label="Send question" disabled={isGenerating || !question.trim()}>
                {isGenerating ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={16} />}
              </button>
            </form>

            <div className="tutor-trust">
              <MessageCircle size={13} />
              <span>
                {backendConnected
                  ? 'Replies are generated by the Quantum AI Tutor & grounded in your step.'
                  : 'Tutor replies are grounded in your selected workflow step.'}
              </span>
            </div>
          </aside>
        </div>

        <button
          type="button"
          className="tutor-reset"
          onClick={() => {
            setCompleted(new Set());
            setStepIndex(0);
            setMessages([{ id: 'reset', role: 'tutor', text: goal.steps[0].tutor, isAi: false }]);
          }}
        >
          <RotateCcw size={14} /> Reset workflow
        </button>
      </main>
    </div>
  );
}