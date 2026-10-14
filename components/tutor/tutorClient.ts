'use client';

export interface TutorAskOptions {
  question: string;
  goal: string;
  stepTitle: string;
  stepDetail: string;
  stepAction: string;
  learnerId?: string;
  mode?: string;
}

export interface TutorReply {
  answer: string;
  concept?: string;
  difficulty?: string;
  hint?: string;
  next_step?: string;
  quality_score?: number;
  suggestions?: string[];
  isAi: boolean;
}

const API_TUTOR_URL = '/api/tutor';
const API_HEALTH_URL = '/api/health';
const TIMEOUT_MS = 14000;

/**
 * Check if the Python AI Tutor backend is active and healthy.
 * Points to relative /api paths so it routes cleanly both in local Next.js dev
 * and on Vercel multi-service architecture (/api/(.*) -> backend service).
 */
export async function checkTutorBackendHealth(): Promise<boolean> {
  // 1. Try relative /api/health (direct backend rewrite on Vercel)
  try {
    const res = await fetch(API_HEALTH_URL, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      return data.status === 'ok' && data.tutor_available !== false;
    }
  } catch {
    // Fall back to /api/tutor status probe
  }

  // 2. Try relative /api/tutor GET probe
  try {
    const res = await fetch(API_TUTOR_URL, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      return Boolean(data.connected || data.status === 'ok');
    }
  } catch {
    return false;
  }

  return false;
}

/**
 * Sends a question to the AI Tutor backend with rich grounded context.
 * Points to relative /api/tutor path for client-side execution.
 * Falls back gracefully to deterministic guidance if the service is unreachable.
 */
export async function askTutorBackend(opts: TutorAskOptions): Promise<TutorReply> {
  const payload = {
    learner_id: opts.learnerId || 'LEARNER_0001',
    mode: opts.mode || (opts.question.toLowerCase().includes('hint') ? 'hint' : 'explain'),
    question: opts.question,
    context: {
      goal: opts.goal,
      step_title: opts.stepTitle,
      step_detail: opts.stepDetail,
      suggested_action: opts.stepAction,
    },
  };

  try {
    const res = await fetch(API_TUTOR_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });

    if (res.ok) {
      const data = await res.json();
      return {
        answer: data.answer || 'I am ready to help you explore this quantum step.',
        concept: data.concept,
        difficulty: data.difficulty,
        hint: data.hint,
        next_step: data.next_step,
        quality_score: data.quality_score,
        suggestions: Array.isArray(data.suggestions) ? data.suggestions : [],
        isAi: true,
      };
    }
  } catch {
    // Both network paths unreachable, fall through to deterministic guidance
  }

  // 3. Graceful Deterministic Fallback (never breaks UX)
  const qLower = opts.question.toLowerCase();
  let fallbackAnswer = `Keep this step concrete: ${opts.stepDetail}. Follow the suggested action: "${opts.stepAction}".`;
  let fallbackHint = `For this step: ${opts.stepDetail}`;
  let fallbackNextStep = opts.stepAction;

  if (qLower.includes('hint') || qLower.includes('help') || qLower.includes('stuck')) {
    fallbackAnswer = `Look for the smallest experiment that can answer the question. For this step: start with the smallest unit of quantum information. Follow the suggested action: "${opts.stepAction}".`;
    fallbackHint = 'Try the smallest possible experiment first.';
  } else if (qLower.includes('why') || qLower.includes('how does')) {
    fallbackAnswer = `That's a great question about quantum concepts! For now, focus on completing this step: ${opts.stepDetail}. You'll understand the "why" better once you try it: "${opts.stepAction}".`;
    fallbackHint = 'Understanding grows from doing, not just reading.';
  } else if (qLower.includes('what') || qLower.includes('explain') || qLower.includes('understand')) {
    fallbackAnswer = `To understand this better, the best approach is hands-on learning. ${opts.stepDetail}. Try this: ${opts.stepAction}.`;
    fallbackHint = 'Quantum concepts are best learned through practice.';
  } else if (qLower.includes('next') || qLower.includes('try') || qLower.includes('should i')) {
    fallbackAnswer = `Your next move is to ${opts.stepAction.toLowerCase()}. When you finish, mark this step complete and I'll move you forward.`;
    fallbackHint = 'Each step builds on the last one.';
    fallbackNextStep = opts.stepAction;
  } else if (qLower.includes('challenge') || qLower.includes('difficult') || qLower.includes('hard')) {
    fallbackAnswer = `This step might feel challenging at first! Remember: ${opts.stepDetail}. The key is to take action: ${opts.stepAction}. You'll build intuition as you practice.`;
    fallbackHint = 'Quantum concepts reveal themselves through experimentation.';
  } else if (qLower.includes('concrete') || qLower.includes('example') || qLower.includes('show me')) {
    fallbackAnswer = `A concrete way to explore this: ${opts.stepAction}. This will give you hands-on experience with ${opts.stepDetail.toLowerCase()}.`;
    fallbackHint = 'The best way to learn is by doing.';
  }

  return {
    answer: fallbackAnswer,
    hint: fallbackHint,
    next_step: fallbackNextStep,
    isAi: false,
    suggestions: [
      'Why does H create superposition?',
      'Give me a hint for this step',
      'What should I try next?',
    ],
  };
}
