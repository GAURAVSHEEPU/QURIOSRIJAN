'use client';

import React from 'react';
import katex from 'katex';

interface TutorMarkdownRendererProps {
  content: string;
}

/**
 * Safely renders LaTeX mathematics into React elements using KaTeX.
 * Supports:
 * - Display math: \[ ... \] or $$ ... $$
 * - Inline math: \( ... \) or $ ... $
 */
function renderMath(mathCode: string, displayMode: boolean, key: string | number): React.ReactNode {
  try {
    const html = katex.renderToString(mathCode.trim(), {
      displayMode,
      throwOnError: false,
      output: 'htmlAndMathml',
    });
    return (
      <span
        key={key}
        className={displayMode ? 'tutor-math-block' : 'tutor-math-inline'}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  } catch {
    return (
      <code key={key} className="tutor-math-fallback">
        {mathCode}
      </code>
    );
  }
}

/**
 * Parses inline string segments into text, inline math, bold, italic, and inline code.
 */
function parseInline(text: string): React.ReactNode[] {
  if (!text) return [];

  // Match:
  // 1. Display math: \[ ... \] or $$ ... $$
  // 2. Inline math: \( ... \) or $ ... $
  // 3. Inline code: ` ... `
  // 4. Bold: ** ... **
  // 5. Italic: * ... *
  const inlineRegex =
    /(\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$|\\\([\s\S]*?\\\)|\$[^$\n]+?\$|`[^`]+?`|\*\*[^*]+?\*\*|\*[^*]+?\*)/g;

  const parts = text.split(inlineRegex);
  const elements: React.ReactNode[] = [];

  parts.forEach((part, index) => {
    if (!part) return;

    // Display math embedded inline
    if (part.startsWith('\\[') && part.endsWith('\\]')) {
      elements.push(renderMath(part.slice(2, -2), true, `disp-${index}`));
    } else if (part.startsWith('$$') && part.endsWith('$$') && part.length >= 4) {
      elements.push(renderMath(part.slice(2, -2), true, `disp-${index}`));
    }
    // Inline math: \( ... \)
    else if (part.startsWith('\\(') && part.endsWith('\\)')) {
      elements.push(renderMath(part.slice(2, -2), false, `inl-${index}`));
    }
    // Inline math: $ ... $
    else if (part.startsWith('$') && part.endsWith('$') && part.length >= 2) {
      elements.push(renderMath(part.slice(1, -1), false, `inl-${index}`));
    }
    // Inline code: ` ... `
    else if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
      elements.push(
        <code key={`code-${index}`} className="tutor-inline-code">
          {part.slice(1, -1)}
        </code>
      );
    }
    // Bold: ** ... **
    else if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
      elements.push(
        <strong key={`bold-${index}`} className="tutor-strong">
          {parseInline(part.slice(2, -2))}
        </strong>
      );
    }
    // Italic: * ... *
    else if (part.startsWith('*') && part.endsWith('*') && part.length >= 2) {
      elements.push(
        <em key={`em-${index}`} className="tutor-em">
          {parseInline(part.slice(1, -1))}
        </em>
      );
    }
    // Plain text
    else {
      elements.push(part);
    }
  });

  return elements;
}

export default function TutorMarkdownRenderer({ content }: TutorMarkdownRendererProps) {
  if (!content) return null;

  // Split into lines while preserving structure
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const blocks: React.ReactNode[] = [];

  let i = 0;
  let blockIndex = 0;

  while (i < lines.length) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    // 1. Empty lines
    if (!trimmed) {
      i++;
      continue;
    }

    // 2. Fenced code block: ```[lang] ... ```
    if (trimmed.startsWith('```')) {
      const codeLines: string[] = [];
      const lang = trimmed.slice(3).trim();
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      if (i < lines.length && lines[i].trim().startsWith('```')) {
        i++; // skip closing ```
      }
      blocks.push(
        <pre key={`codeblock-${blockIndex++}`} className="tutor-code-block" data-lang={lang || undefined}>
          <code>{codeLines.join('\n')}</code>
        </pre>
      );
      continue;
    }

    // 3. Display Math Block: $$ ... $$ or \[ ... \] across multiple lines
    if (trimmed === '$$' || trimmed === '\\[') {
      const closingTag = trimmed === '$$' ? '$$' : '\\]';
      const mathLines: string[] = [];
      i++;
      while (i < lines.length && lines[i].trim() !== closingTag) {
        mathLines.push(lines[i]);
        i++;
      }
      if (i < lines.length && lines[i].trim() === closingTag) {
        i++;
      }
      blocks.push(renderMath(mathLines.join('\n'), true, `display-math-${blockIndex++}`));
      continue;
    }

    // 4. Single-line Display Math: $$...$$ or \[...\]
    if (
      (trimmed.startsWith('$$') && trimmed.endsWith('$$') && trimmed.length > 2) ||
      (trimmed.startsWith('\\[') && trimmed.endsWith('\\]') && trimmed.length > 2)
    ) {
      const mathContent = trimmed.startsWith('$$') ? trimmed.slice(2, -2) : trimmed.slice(2, -2);
      blocks.push(renderMath(mathContent, true, `display-math-${blockIndex++}`));
      i++;
      continue;
    }

    // 5. Headings: #, ##, ###, ####
    if (trimmed.startsWith('#')) {
      const match = trimmed.match(/^(#{1,4})\s+(.+)$/);
      if (match) {
        const level = match[1].length;
        const headingText = match[2];
        const children = parseInline(headingText);

        if (level === 1) {
          blocks.push(
            <h3 key={`h1-${blockIndex++}`} className="tutor-heading tutor-h1">
              {children}
            </h3>
          );
        } else if (level === 2) {
          blocks.push(
            <h4 key={`h2-${blockIndex++}`} className="tutor-heading tutor-h2">
              {children}
            </h4>
          );
        } else if (level === 3) {
          blocks.push(
            <h5 key={`h3-${blockIndex++}`} className="tutor-heading tutor-h3">
              {children}
            </h5>
          );
        } else {
          blocks.push(
            <h6 key={`h4-${blockIndex++}`} className="tutor-heading tutor-h4">
              {children}
            </h6>
          );
        }
        i++;
        continue;
      }
    }

    // 6. Ordered List: 1. item
    if (/^\d+\.\s+/.test(trimmed)) {
      const listItems: React.ReactNode[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        const itemLine = lines[i].trim();
        const itemText = itemLine.replace(/^\d+\.\s+/, '');
        listItems.push(<li key={`ol-item-${listItems.length}`}>{parseInline(itemText)}</li>);
        i++;
      }
      blocks.push(
        <ol key={`ol-${blockIndex++}`} className="tutor-ordered-list">
          {listItems}
        </ol>
      );
      continue;
    }

    // 7. Unordered List: - item or * item
    if (/^[-*•]\s+/.test(trimmed)) {
      const listItems: React.ReactNode[] = [];
      while (i < lines.length && /^[-*•]\s+/.test(lines[i].trim())) {
        const itemLine = lines[i].trim();
        const itemText = itemLine.replace(/^[-*•]\s+/, '');
        listItems.push(<li key={`ul-item-${listItems.length}`}>{parseInline(itemText)}</li>);
        i++;
      }
      blocks.push(
        <ul key={`ul-${blockIndex++}`} className="tutor-unordered-list">
          {listItems}
        </ul>
      );
      continue;
    }

    // 8. Paragraph (combining consecutive non-empty regular lines)
    const paraLines: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].trim().startsWith('#') &&
      !lines[i].trim().startsWith('```') &&
      !/^\d+\.\s+/.test(lines[i].trim()) &&
      !/^[-*•]\s+/.test(lines[i].trim()) &&
      lines[i].trim() !== '$$' &&
      lines[i].trim() !== '\\['
    ) {
      paraLines.push(lines[i].trim());
      i++;
    }

    if (paraLines.length > 0) {
      blocks.push(
        <p key={`p-${blockIndex++}`} className="tutor-paragraph">
          {parseInline(paraLines.join(' '))}
        </p>
      );
    }
  }

  return <div className="tutor-rendered-content">{blocks}</div>;
}

