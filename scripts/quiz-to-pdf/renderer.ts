/**
 * Quiz HTML Renderer
 *
 * Generates HTML for quiz PDF generation including cover sheet,
 * questions with syntax-highlighted code, and answer key.
 */

import { Marked } from 'marked';
import { markedHighlight } from 'marked-highlight';
import hljs from 'highlight.js';
import QRCode from 'qrcode';
import type { ParsedQuiz, QuizQuestion, PdfOptions, CaseStudy, SubPart } from './types';
import { getStyles } from './styles';

// Store mermaid blocks to preserve raw content (avoid HTML escaping of <|--)
const mermaidBlocks: Map<string, string> = new Map();
let mermaidCounter = 0;

// Configure marked with syntax highlighting
const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code: string, lang: string) {
      if (lang === 'mermaid') {
        const id = `__MERMAID_${mermaidCounter++}__`;
        mermaidBlocks.set(id, code);
        return id;
      }
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    },
  })
);

marked.use({
  renderer: {
    code(token) {
      if (token.lang === 'mermaid') {
        const rawContent = mermaidBlocks.get(token.text) || token.text;
        const escaped = rawContent
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;');
        return `<pre class="mermaid">${escaped}</pre>`;
      }
      const langClass = token.lang ? `hljs language-${token.lang}` : '';
      return `<pre><code class="${langClass}">${token.text}</code></pre>`;
    },
  },
});

async function generateQRCode(data: string): Promise<string> {
  return QRCode.toDataURL(data, {
    width: 300,
    margin: 2,
    errorCorrectionLevel: 'H',
  });
}

export interface RenderedQuiz {
  quizHtml: string;
  answerKeyHtml?: string;
}

const DEFAULT_LINE_COUNT = 5;
const LINES_PER_INCH = 4;

function inchesToLineCount(inches: number | undefined): number {
  if (inches === undefined) return DEFAULT_LINE_COUNT;
  return Math.max(1, Math.round(inches * LINES_PER_INCH));
}

function renderWriteInBlock(label: string, lineCount: number): string {
  const ruled = Array.from(
    { length: lineCount },
    () => '<div class="answer-ruled-line"></div>'
  ).join('');
  return `
    <div class="write-in-block">
      <div class="write-in-label">${escapeHtml(label)}</div>
      <div class="write-in-lines">${ruled}</div>
    </div>`;
}

function renderSubPartAnswer(caseNum: number, sp: SubPart): string {
  if (sp.subSubParts.length > 0) {
    const subs = sp.subSubParts
      .map(ss =>
        renderWriteInBlock(
          `${caseNum}(${sp.letter})(${ss.numeral})`,
          inchesToLineCount(ss.spaceInches)
        )
      )
      .join('');
    return `
    <div class="sub-subpart-group">
      <div class="write-in-parent-label">${caseNum}(${escapeHtml(sp.letter)})</div>
      ${subs}
    </div>`;
  }
  return renderWriteInBlock(
    `${caseNum}(${sp.letter})`,
    inchesToLineCount(sp.spaceInches)
  );
}

/**
 * Part II handwritten answer areas (cover / early pages only).
 */
function renderPartTwoAnswerCapture(caseStudies: CaseStudy[]): string {
  if (!caseStudies.length) return '';

  const blocks = caseStudies
    .map((cs, idx) => {
      const caseNum = idx + 1;
      const parts = cs.subparts.length > 0
        ? cs.subparts.map(sp => renderSubPartAnswer(caseNum, sp)).join('')
        : renderWriteInBlock(`Case ${caseNum} Answer`, DEFAULT_LINE_COUNT);
      return `
      <div class="case-study-answer-block">
        <h3 class="case-study-answer-title">${escapeHtml(cs.title)}</h3>
        ${parts}
      </div>`;
    })
    .join('');

  return `
<div class="answer-sheet-part-ii">
  <div class="answer-sheet-part-ii-title">Part II — write answers here only (not on question pages)</div>
  ${blocks}
</div>`;
}

/**
 * Cover sheet plus optional Part II answer sheet (continuation page).
 */
async function renderCoverAndAnswerSheets(
  quiz: ParsedQuiz,
  version: string | undefined,
  inlineAnswers: boolean
): Promise<string> {
  const { metadata, instructions, caseStudies } = quiz;

  const maxChoiceCount = quiz.questions.reduce(
    (max, q) => Math.max(max, q.choices.length),
    0
  );
  const bubbleGrid = renderAnswerBubbleGrid(metadata.questionCount, maxChoiceCount || 4);

  const partTwoInstruction = caseStudies?.length
    ? inlineAnswers
      ? ['Write each Part II answer in the space provided directly under its prompt.']
      : ['Record all Part II answers in the Part II answer areas that follow — not on the question pages.']
    : [];

  const mcInstruction = inlineAnswers
    ? 'For each multiple-choice question, fill in the bubble next to your chosen answer.'
    : 'Record all multiple-choice answers on the answer grid below.';

  const allInstructions = [
    'Write your initials on EVERY page of this exam.',
    mcInstruction,
    ...partTwoInstruction,
    ...instructions,
  ];
  const instructionsHtml = `<div class="instructions">
        <div class="instructions-title">Instructions</div>
        <ul>
          ${allInstructions.map(i => `<li>${escapeHtml(i)}</li>`).join('\n          ')}
        </ul>
      </div>`;

  let coverVersionHtml = '';
  if (version) {
    const qrDataUrl = await generateQRCode(version);
    coverVersionHtml = `
    <div class="qr-warning-box">
      <div class="qr-left">
        <img class="version-qr" src="${qrDataUrl}" alt="QR" />
        <div class="qr-label">DO NOT MARK</div>
      </div>
      <div class="qr-right">
        <strong>Warning:</strong> Each exam has a unique, randomized answer pattern.
        Your neighbor's answers are different from yours—copying will result in wrong answers.
        Marks in the QR area will invalidate your exam.
      </div>
    </div>`;
  }

  const courseLine = metadata.course
    ? `<p><strong>Course:</strong> ${escapeHtml(metadata.course)}</p>`
    : '';

  const cover = `
<div class="cover-sheet">
  <div class="cover-header">
    <h1>${escapeHtml(metadata.title)}</h1>
    <h2>CS 3100 - Program Design and Implementation II</h2>
  </div>

  <div class="cover-metadata">
    ${courseLine}
    <p><strong>Topics:</strong> ${escapeHtml(metadata.topicsCovered)}</p>
    <p><strong>Time:</strong> ${escapeHtml(metadata.timeLimit)}</p>
    <p><strong>Format:</strong> ${escapeHtml(metadata.format)}</p>
  </div>

  <div class="student-info">
    <div class="student-info-row">
      <span class="student-info-label">Name:</span>
      <span class="student-info-line"></span>
    </div>
    <div class="student-info-row">
      <span class="student-info-label">NUID:</span>
      <span class="student-info-line"></span>
    </div>
  </div>

  ${instructionsHtml}

  ${
    inlineAnswers
      ? ''
      : `<div class="answer-grid-container">
    <div class="answer-grid-title">Part I — Answer grid (multiple choice)</div>
    ${bubbleGrid}
  </div>`
  }

  ${coverVersionHtml}
</div>`;

  const part2Sheet =
    caseStudies?.length && !inlineAnswers ? renderPartTwoAnswerCapture(caseStudies) : '';
  return cover + part2Sheet;
}

export async function renderQuizToHtml(quiz: ParsedQuiz, options: PdfOptions): Promise<RenderedQuiz> {
  const quizParts: string[] = [];

  if (options.includeCover) {
    quizParts.push(
      await renderCoverAndAnswerSheets(quiz, options.version, options.inlineAnswers)
    );
    // Add a blank page after cover when there's no Part II answer sheet pushing onto the next page.
    if (!options.noBlankPage && (!quiz.caseStudies?.length || options.inlineAnswers)) {
      quizParts.push(renderBlankPage());
    }
  }

  if (quiz.partOneIntroMarkdown?.trim()) {
    quizParts.push(`<div class="part-intro">${marked.parse(quiz.partOneIntroMarkdown)}</div>`);
  }

  quizParts.push(renderMcQuestions(quiz.questions, options.inlineAnswers));
  quizParts.push(renderPartTwoPrompts(quiz, options.inlineAnswers, options.includeAnswers));
  quizParts.push(renderOverflowPages(2));

  const result: RenderedQuiz = {
    quizHtml: renderDocument(quizParts.join('\n'), options),
  };

  const hasMcKey = quiz.answerKey && quiz.answerKey.length > 0;
  const hasOpenKey = !!quiz.answerKeyOpenEndedMarkdown?.trim();
  const hasCaseStudies = !!quiz.caseStudies?.length;
  if (options.includeAnswers && (hasMcKey || hasOpenKey || hasCaseStudies)) {
    // Include case study prompts with rubric blockquotes in the answer key
    const answerKeyContent = renderAnswerKey(quiz)
      + renderPartTwoPrompts(quiz, false, true);
    result.answerKeyHtml = renderDocument(answerKeyContent, options);
  }

  return result;
}

function renderDocument(content: string, options: PdfOptions): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quiz</title>
  <style>${getStyles(options.margin)}</style>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
  ${content}
  <script>
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
  </script>
</body>
</html>`;
}

function renderAnswerBubbleGrid(questionCount: number, choiceCount: number): string {
  if (questionCount <= 0) {
    return '<p class="answer-grid-empty">(No multiple-choice questions)</p>';
  }
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    .slice(0, Math.max(1, Math.min(choiceCount, 26)))
    .split('');

  const numColumns = questionCount > 20 ? 3 : 2;
  const rowsPerColumn = Math.ceil(questionCount / numColumns);

  const columns: number[][] = [];
  for (let col = 0; col < numColumns; col++) {
    const column: number[] = [];
    for (let row = 0; row < rowsPerColumn; row++) {
      const questionNum = col * rowsPerColumn + row + 1;
      if (questionNum <= questionCount) {
        column.push(questionNum);
      }
    }
    columns.push(column);
  }

  const rows: string[] = [];
  for (let row = 0; row < rowsPerColumn; row++) {
    const rowCells = columns
      .map(column => {
        const questionNum = column[row];
        if (questionNum === undefined) {
          return '<div class="answer-row"></div>';
        }
        return `
      <div class="answer-row">
        <span class="question-num">${questionNum}.</span>
        <div class="bubbles">
          ${letters.map(letter => `<span class="bubble">${letter}</span>`).join('')}
        </div>
      </div>`;
      })
      .join('');
    rows.push(rowCells);
  }

  const gridClass = numColumns === 3 ? 'answer-grid three-columns' : 'answer-grid';
  return `<div class="${gridClass}">${rows.join('')}</div>`;
}

function renderBlankPage(): string {
  return `
<div class="blank-page">
  <div class="blank-page-text">This page intentionally left blank.</div>
</div>`;
}

function renderOverflowPages(count: number): string {
  const pages: string[] = [];
  for (let i = 1; i <= count; i++) {
    pages.push(`
<div class="overflow-page">
  <div class="overflow-page-header">
    <div class="overflow-page-title">Overflow Space — Page ${i} of ${count}</div>
    <div class="overflow-page-note">Mark this area only if you run out of space, and clearly reference which question you are answering.</div>
  </div>
</div>`);
  }
  return pages.join('\n');
}

function renderMcQuestions(questions: QuizQuestion[], inlineAnswers: boolean): string {
  if (!questions.length) return '';
  const questionHtml = questions.map(q => renderQuestion(q, inlineAnswers)).join('\n');
  return `
<div class="questions-container">
  ${questionHtml}
</div>`;
}

/**
 * Strip `> **Good answer covers:** ...` blockquotes (and their continuation lines)
 * from a case study body. Used when generating the student-facing PDF.
 */
function stripRubricBlockquotes(md: string): string {
  const rubricBlock = /^> \*\*Good answer covers:\*\*.*(?:\n>.*)*\n?/gm;
  return md.replace(rubricBlock, '').replace(/\n{3,}/g, '\n\n');
}

function renderPartTwoPrompts(
  quiz: ParsedQuiz,
  inlineAnswers: boolean,
  includeAnswers: boolean
): string {
  const { caseStudies, partTwoHeading, partTwoIntroMarkdown } = quiz;
  if (!caseStudies?.length) return '';

  const h = partTwoHeading
    ? `<h2 class="part-two-heading">${escapeHtml(partTwoHeading)}</h2>`
    : '<h2 class="part-two-heading">Part II</h2>';
  const intro = partTwoIntroMarkdown?.trim()
    ? `<div class="part-two-intro">${marked.parse(partTwoIntroMarkdown)}</div>`
    : '';
  const cases = caseStudies
    .map((cs, idx) => {
      const caseNum = idx + 1;
      const body = includeAnswers ? cs.bodyMarkdown : stripRubricBlockquotes(cs.bodyMarkdown);
      const inner = inlineAnswers
        ? renderCaseStudyInline(caseNum, cs, body)
        : `<div class="case-study-body">${marked.parse(body)}</div>`;
      return `
    <div class="case-study case-study-prompt">
      <h3 class="case-study-title">${escapeHtml(cs.title)}</h3>
      ${inner}
    </div>`;
    })
    .join('\n');

  return `<div class="part-two-container">${h}${intro}${cases}</div>`;
}

/**
 * Same marker pattern as the parser — match **(a)** and **(a)(i)**.
 */
const INLINE_MARKER_RE = /\*\*\(([a-z])\)(?:\(([ivx]+)\))?\*\*/gi;

function renderCaseStudyInline(caseNum: number, cs: CaseStudy, body: string): string {
  const matches: { letter: string; numeral?: string; start: number; end: number }[] = [];
  const re = new RegExp(INLINE_MARKER_RE.source, INLINE_MARKER_RE.flags);
  let m: RegExpExecArray | null;
  while ((m = re.exec(body)) !== null) {
    matches.push({
      letter: m[1].toLowerCase(),
      numeral: m[2]?.toLowerCase(),
      start: m.index,
      end: m.index + m[0].length,
    });
  }

  if (matches.length === 0) {
    const rendered = marked.parse(body) as string;
    const block = renderWriteInBlock(`Case ${caseNum} Answer`, DEFAULT_LINE_COUNT);
    return `<div class="case-study-body">${rendered}</div>${block}`;
  }

  const parts: string[] = [];
  const intro = body.slice(0, matches[0].start).trim();
  if (intro) {
    parts.push(`<div class="case-study-body">${marked.parse(intro)}</div>`);
  }

  for (let i = 0; i < matches.length; i++) {
    const cur = matches[i];
    const next = matches[i + 1];
    const section = body.slice(cur.start, next ? next.start : body.length);
    const prompt = `<div class="case-study-subpart-inline">${marked.parse(section)}</div>`;

    const sp = cs.subparts.find(s => s.letter === cur.letter);
    let writeIn = '';
    if (sp) {
      if (cur.numeral) {
        const ss = sp.subSubParts.find(s => s.numeral === cur.numeral);
        if (ss) {
          writeIn = renderWriteInBlock(
            `${caseNum}(${sp.letter})(${ss.numeral})`,
            inchesToLineCount(ss.spaceInches)
          );
        }
      } else if (sp.subSubParts.length === 0) {
        writeIn = renderWriteInBlock(
          `${caseNum}(${sp.letter})`,
          inchesToLineCount(sp.spaceInches)
        );
      }
    }

    // Wrap prompt + answer together so they don't split across a page.
    // When this subpart has no answer area (parent of sub-sub-parts), the prompt
    // stands alone and is allowed to flow naturally.
    if (writeIn) {
      parts.push(`<div class="subpart-inline-unit">${prompt}${writeIn}</div>`);
    } else {
      parts.push(prompt);
    }
  }

  return parts.join('\n');
}

function renderQuestion(question: QuizQuestion, inlineAnswers: boolean): string {
  const textHtml = marked.parse(question.text) as string;
  const choicesHtml = question.choices
    .map(c => {
      const bubble = inlineAnswers ? `<span class="choice-bubble"></span>` : '';
      return `
    <li class="choice">
      ${bubble}
      <span class="choice-letter">${c.letter})</span>
      <span class="choice-text">${renderInlineMarkdown(c.text)}</span>
    </li>`;
    })
    .join('');

  const choicesClass = inlineAnswers ? 'choices choices-inline' : 'choices';
  return `
<div class="question" data-question="${question.number}">
  <div class="question-text"><span class="q-num-prefix">${question.number}.</span> ${textHtml}</div>
  <ul class="${choicesClass}">
    ${choicesHtml}
  </ul>
</div>`;
}

function renderInlineMarkdown(text: string): string {
  return text.replace(/`([^`]+)`/g, (_, code) => `<code>${escapeHtml(code)}</code>`);
}

function renderAnswerKey(quiz: ParsedQuiz): string {
  const hasTable = quiz.answerKey && quiz.answerKey.length > 0;
  const hasOpen = !!quiz.answerKeyOpenEndedMarkdown?.trim();
  if (!hasTable && !hasOpen) return '';

  let tableHtml = '';
  if (hasTable) {
    const rows = quiz.answerKey!
      .map(
        entry => `
    <tr>
      <td>${entry.question}</td>
      <td>${entry.answers.join(', ')}</td>
      <td>${escapeHtml(entry.topic)}</td>
    </tr>`
      )
      .join('');
    tableHtml = `
  <h3 class="answer-key-part-title">Part I — Multiple choice</h3>
  <table class="answer-key-table">
    <thead>
      <tr>
        <th>Q</th>
        <th>Answer</th>
        <th>Topic</th>
      </tr>
    </thead>
    <tbody>
      ${rows}
    </tbody>
  </table>`;
  }

  const openHtml = hasOpen
    ? `<div class="answer-key-open-ended">${marked.parse(quiz.answerKeyOpenEndedMarkdown!)}</div>`
    : '';

  return `
<div class="answer-key">
  <h2>Answer Key</h2>
  ${tableHtml}
  ${openHtml}
</div>`;
}

function escapeHtml(text: string): string {
  const htmlEscapes: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };
  return text.replace(/[&<>"']/g, char => htmlEscapes[char]);
}
