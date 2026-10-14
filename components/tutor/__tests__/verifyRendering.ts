import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import TutorMarkdownRenderer from '../TutorMarkdownRenderer';

export function runFocusedRenderingVerification(): {
  success: boolean;
  checks: Record<string, boolean>;
} {
  const sampleMarkdownWithMath = `## What is Grover's Algorithm?
Grover's algorithm provides **quadratic speedup** for unstructured search.

The Hadamard gate is represented as:
\\[ H = \\frac{1}{\\sqrt{2}}\\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix} \\]

State formula: \\( |\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle \\) and $O|x\\rangle = (-1)^{f(x)}|x\\rangle$.

Key steps:
1. First step with \`qc.h(0)\`
2. Second step with diffusion operator

Summary bullets:
- Point A: Superposition
- Point B: Amplitude amplification
`;

  const html = renderToStaticMarkup(
    React.createElement(TutorMarkdownRenderer, { content: sampleMarkdownWithMath })
  );

  const checks = {
    rendersSuccessfully: html.length > 500,
    hasKatexMath: html.includes('class="katex"'),
    hasRenderedHeading: html.includes('class="tutor-heading tutor-h2"') && html.includes("What is Grover&#x27;s Algorithm?"),
    hasRenderedBold: html.includes('class="tutor-strong"') && html.includes('quadratic speedup'),
    hasRenderedOrderedList: html.includes('class="tutor-ordered-list"') && html.includes('First step with'),
    hasRenderedUnorderedList: html.includes('class="tutor-unordered-list"') && html.includes('Point A: Superposition'),
    hasRenderedInlineCode: html.includes('class="tutor-inline-code"') && html.includes('qc.h(0)'),
    noRawHeadingMarkers: !html.includes('## What is Grover'),
    noRawBoldMarkers: !html.includes('**quadratic speedup**'),
    noRawDisplayDelimiters: !html.includes('\\[ H ='),
    noRawInlineDelimiters: !html.includes('\\( |\\psi'),
  };

  const success = Object.values(checks).every(Boolean);
  return { success, checks };
}

if (typeof require !== 'undefined' && require.main === module) {
  const result = runFocusedRenderingVerification();
  console.log(JSON.stringify(result, null, 2));
  if (!result.success) {
    process.exit(1);
  }
}

