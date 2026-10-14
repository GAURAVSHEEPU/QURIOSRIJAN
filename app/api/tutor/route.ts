import { NextResponse } from 'next/server';

const BACKEND_BASE_URL = (process.env.BACKEND_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');

async function queryPythonBackend(
  endpoint: string,
  method: string,
  data?: unknown
): Promise<{ ok: boolean; status: number; data?: unknown; error?: unknown }> {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${BACKEND_BASE_URL}${cleanEndpoint}`;
  const payload = data ? JSON.stringify(data) : undefined;

  try {
    const res = await fetch(url, {
      method,
      headers: {
        ...(payload ? { 'Content-Type': 'application/json' } : {}),
      },
      body: payload,
      signal: AbortSignal.timeout(15000),
    });

    let parsed: unknown;
    try {
      parsed = await res.json();
    } catch {
      const text = await res.text().catch(() => '');
      return { ok: res.ok, status: res.status, error: text };
    }

    return { ok: res.ok, status: res.status, data: parsed };
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Backend connection error';
    return { ok: false, status: 503, error: errorMsg };
  }
}

export async function GET() {
  try {
    const res = await queryPythonBackend('/health', 'GET');
    if (res.ok) {
      return NextResponse.json({ connected: true, ...(res.data as object) });
    }
    return NextResponse.json({ connected: false, status: res.status }, { status: 502 });
  } catch {
    return NextResponse.json({ connected: false }, { status: 503 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const result = await queryPythonBackend('/api/tutor', 'POST', {
      learner_id: body.learner_id || 'LEARNER_0001',
      mode: body.mode || 'explain',
      question: body.question,
      context: body.context || null,
    });

    if (!result.ok) {
      return NextResponse.json(
        { error: 'Backend error', detail: result.error || result.data },
        { status: result.status }
      );
    }

    return NextResponse.json(result.data);
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: 'Tutor backend unreachable', detail: msg },
      { status: 503 }
    );
  }
}
