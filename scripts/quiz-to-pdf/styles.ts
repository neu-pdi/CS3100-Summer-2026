/**
 * Quiz PDF Styles
 *
 * Print-optimized CSS for quiz PDF generation.
 */

export function getStyles(margin: string): string {
  return `
/* Base Styles */
* {
  box-sizing: border-box;
}

body {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 11pt;
  line-height: 1.4;
  color: #000;
  margin: 0;
  padding: 0;
}

/* ============================================
   QR CODE WARNING BOX STYLES (Compact)
   ============================================ */

/* Warning box - horizontal layout */
.qr-warning-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 2px solid #c00;
  background: #fff8f8;
  padding: 0.5rem 0.75rem;
  margin: 0.5rem 0;
}

/* Left side: QR code */
.qr-left {
  flex-shrink: 0;
  text-align: center;
}

.version-qr {
  width: 100px;
  height: 100px;
  display: block;
}

.qr-label {
  font-size: 6pt;
  font-weight: bold;
  color: #c00;
  margin-top: 2px;
}

/* Right side: Warning text */
.qr-right {
  font-size: 8pt;
  line-height: 1.25;
  color: #333;
}

.qr-right strong {
  color: #c00;
}

/* Running header watermark for question pages (in margin area, above content) */
.page-version {
  position: fixed;
  top: -0.5in;
  right: 0;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  font-size: 11pt;
  color: #c00;
  z-index: 1000;
}

/* Hide page version on cover sheet */
.cover-sheet ~ .page-version {
  display: block;
}

/* ============================================
   COVER SHEET STYLES (Minimalist)
   ============================================ */

.cover-sheet {
  page-break-after: always;
  padding: 0;
}

/* Part II handwritten answer sheet (continuation of cover flow) */
.answer-sheet-part-ii {
  page-break-before: always;
  page-break-after: always;
  padding: 0.25rem 0 0 0;
}

.answer-sheet-part-ii-title {
  font-size: 11pt;
  font-weight: bold;
  text-align: center;
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 2px solid #000;
  padding-bottom: 0.35rem;
}

.case-study-answer-block {
  margin-bottom: 1rem;
}

.case-study-answer-title {
  font-size: 11pt;
  font-weight: bold;
  margin: 0 0 0.4rem 0;
}

.write-in-block {
  margin-bottom: 0.65rem;
  box-sizing: border-box;
  page-break-inside: avoid;
}

/* Keep an inline prompt together with its answer box on the same page. */
.subpart-inline-unit {
  page-break-inside: avoid;
  margin-bottom: 0.5rem;
}

.write-in-label {
  font-weight: bold;
  font-size: 10pt;
  margin-bottom: 0.2rem;
}

.sub-subpart-group {
  margin-bottom: 0.75rem;
}

.write-in-parent-label {
  font-weight: bold;
  font-size: 10pt;
  margin: 0.1rem 0 0.3rem 0;
}

.sub-subpart-group .write-in-block {
  margin-left: 1rem;
  margin-bottom: 0.4rem;
}

.sub-subpart-group .write-in-label {
  font-size: 9.5pt;
  font-weight: normal;
  font-style: italic;
}

.write-in-lines {
  border: 1px solid #333;
  padding: 0.35rem 0.5rem 0.25rem 0.5rem;
  background: #fafafa;
  box-sizing: border-box;
  overflow: hidden;
  max-width: calc(100% - 6px);
}

.answer-ruled-line {
  border-bottom: 1px solid #888;
  min-height: 1.35rem;
  margin-bottom: 0.15rem;
}

.answer-ruled-line:last-child {
  margin-bottom: 0;
}

.answer-grid-empty {
  font-size: 10pt;
  color: #666;
  margin: 0.25rem 0;
}

/* Part I intro before MC questions */
.part-intro {
  margin-bottom: 1rem;
  padding: 0.5rem 0;
  page-break-after: avoid;
}

.part-intro p {
  margin: 0 0 0.5rem 0;
}

/* Part II prompts (exam body) */
.part-two-container {
  margin-top: 1.25rem;
  padding-top: 0.5rem;
  border-top: 2px solid #000;
}

.part-two-heading {
  font-size: 14pt;
  margin: 0 0 0.5rem 0;
  page-break-after: avoid;
}

.part-two-intro {
  margin-bottom: 1rem;
  font-size: 11pt;
  page-break-after: avoid;
}

.part-two-intro p {
  margin: 0 0 0.5rem 0;
}

.case-study-prompt {
  margin-bottom: 1.5rem;
}

.case-study-title {
  font-size: 12pt;
  margin: 0 0 0.5rem 0;
  page-break-after: avoid;
}

.case-study-body {
  font-size: 11pt;
}

.case-study-body p {
  margin: 0 0 0.5rem 0;
}

.case-study-subpart-inline {
  font-size: 11pt;
  margin: 0.5rem 0 0.25rem 0;
}

.case-study-subpart-inline p {
  margin: 0 0 0.35rem 0;
}

.answer-key-part-title {
  font-size: 12pt;
  margin: 1rem 0 0.5rem 0;
}

.answer-key-open-ended {
  margin-top: 1rem;
  font-size: 10pt;
}

.answer-key-open-ended h3 {
  font-size: 11pt;
  margin-top: 1rem;
}

.answer-key-open-ended p,
.answer-key-open-ended li {
  margin: 0.35rem 0;
}

/* Blank page after cover */
.blank-page {
  page-break-after: always;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blank-page-text {
  font-style: italic;
  color: #999;
  font-size: 11pt;
}

/* Overflow pages at end of exam */
.overflow-page {
  page-break-before: always;
}

.overflow-page-header {
  border: 2px solid #000;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
}

.overflow-page-title {
  font-weight: bold;
  font-size: 12pt;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.overflow-page-note {
  font-size: 10pt;
  line-height: 1.35;
}

.cover-header {
  text-align: center;
  border-bottom: 2px solid #000;
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.cover-header h1 {
  font-size: 20pt;
  margin: 0 0 0.25rem 0;
  font-weight: bold;
}

.cover-header h2 {
  font-size: 13pt;
  margin: 0;
  font-weight: normal;
  color: #333;
}

.cover-metadata {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  margin-bottom: 0.5rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid #ccc;
  font-size: 10pt;
}

.cover-metadata p {
  margin: 0;
}

.student-info {
  margin-bottom: 0.5rem;
  padding: 0.4rem 0;
}

.student-info-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 0.5rem;
  font-size: 11pt;
}

.student-info-label {
  font-weight: bold;
  min-width: 60px;
}

.student-info-line {
  flex: 1;
  border-bottom: 1px solid #000;
  margin-left: 0.5rem;
  min-height: 1.2rem;
}

/* Answer Grid */
.answer-grid-container {
  border: 2px solid #000;
  padding: 0.5rem 0.75rem;
}

.answer-grid-title {
  font-size: 11pt;
  font-weight: bold;
  text-align: center;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.35rem 2rem;
}

.answer-grid.three-columns {
  grid-template-columns: repeat(3, 1fr);
  gap: 0.3rem 1.5rem;
}

.answer-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.question-num {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  min-width: 1.5rem;
  text-align: right;
  font-size: 10pt;
}

.bubbles {
  display: flex;
  gap: 0.3rem;
}

.bubble {
  width: 1.1rem;
  height: 1.1rem;
  border: 1.5px solid #000;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: 'Arial', sans-serif;
  font-size: 0.55rem;
  font-weight: bold;
}

/* Instructions Section */
.instructions {
  margin: 0.5rem 0;
  padding: 0.4rem 0.75rem;
  border: 1px solid #ccc;
  background: #fafafa;
  font-size: 10pt;
}

.instructions-title {
  font-size: 10pt;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.instructions ul {
  margin: 0;
  padding-left: 1.25rem;
}

.instructions li {
  margin-bottom: 0.15rem;
}

/* ============================================
   QUESTION STYLES
   ============================================ */

.questions-container {
  padding: 0;
}

.question {
  margin-bottom: 0.5rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid #ddd;
  page-break-inside: avoid;
}

.question:last-child {
  border-bottom: none;
}

.question-header {
  font-weight: bold;
  font-size: 11pt;
  margin-bottom: 0.15rem;
  page-break-after: avoid;
}

.question-text {
  margin-bottom: 0.3rem;
  line-height: 1.3;
}

.question-text p {
  margin: 0 0 0.25rem 0;
}

.q-num-prefix {
  font-weight: bold;
  margin-right: 0.35rem;
}

/* Inline the question number with the first paragraph of the prompt */
.question-text > p:first-of-type {
  display: inline;
}

/* Choices */
.choices {
  list-style: none;
  padding: 0;
  margin: 0 0 0 0.5rem;
  page-break-before: avoid;
}

.choice {
  display: flex;
  align-items: baseline;
  margin-bottom: 0.15rem;
  line-height: 1.3;
}

.choice-letter {
  font-weight: bold;
  min-width: 2rem;
  flex-shrink: 0;
}

.choice-text {
  flex: 1;
}

/* Per-choice fillable bubble (inline-answers mode) */
.choice-bubble {
  display: inline-block;
  width: 0.85rem;
  height: 0.85rem;
  border: 1.25px solid #000;
  border-radius: 50%;
  flex-shrink: 0;
  margin-right: 0.5rem;
  transform: translateY(0.1rem);
}

.choices-inline .choice {
  margin-bottom: 0.25rem;
}

/* Code Blocks */
pre {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.4rem 0.75rem;
  margin: 0.35rem 0;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 9.5pt;
  line-height: 1.25;
  page-break-inside: avoid;
}

/* Mermaid Diagrams */
pre.mermaid {
  background: transparent;
  border: none;
  padding: 0.5rem 0;
  text-align: center;
  font-family: inherit;
}

pre.mermaid svg {
  max-width: 70%;
  max-height: 200px;
  height: auto;
}

code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 9.5pt;
}

/* Inline code */
p code, li code {
  background: #f0f0f0;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-size: 9.5pt;
}

/* Highlight.js Theme (GitHub-like) */
.hljs {
  background: #f5f5f5;
}

.hljs-comment,
.hljs-quote {
  color: #6a737d;
  font-style: italic;
}

.hljs-keyword,
.hljs-selector-tag {
  color: #d73a49;
}

.hljs-string,
.hljs-attr {
  color: #032f62;
}

.hljs-number,
.hljs-literal {
  color: #005cc5;
}

.hljs-built_in,
.hljs-builtin-name {
  color: #6f42c1;
}

.hljs-type,
.hljs-class .hljs-title {
  color: #6f42c1;
}

.hljs-function .hljs-title,
.hljs-title.function_ {
  color: #6f42c1;
}

.hljs-variable,
.hljs-template-variable {
  color: #e36209;
}

.hljs-meta {
  color: #6a737d;
}

/* ============================================
   ANSWER KEY STYLES
   ============================================ */

.answer-key {
  page-break-before: always;
  padding-top: 0.5in;
}

.answer-key h2 {
  font-size: 16pt;
  margin-bottom: 1rem;
  border-bottom: 2px solid #000;
  padding-bottom: 0.5rem;
}

.answer-key-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10pt;
}

.answer-key-table th,
.answer-key-table td {
  border: 1px solid #000;
  padding: 0.4rem 0.75rem;
  text-align: left;
}

.answer-key-table th {
  background: #f0f0f0;
  font-weight: bold;
}

.answer-key-table td:first-child,
.answer-key-table td:nth-child(2) {
  text-align: center;
  width: 60px;
}

/* ============================================
   PRINT STYLES
   ============================================ */

@page {
  size: letter;
  margin: ${margin};
}

@media print {
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .question-header {
    page-break-after: avoid;
  }

  .question {
    page-break-inside: avoid;
  }

  .choices {
    page-break-before: avoid;
  }

  .choice {
    page-break-inside: avoid;
  }

  pre {
    page-break-inside: avoid;
  }

  .cover-sheet {
    page-break-after: always;
  }

  .answer-key {
    page-break-before: always;
  }

  .answer-sheet-part-ii {
    page-break-before: always;
    page-break-after: always;
  }
}
`;
}
