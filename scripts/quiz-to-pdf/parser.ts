/**
 * Quiz Markdown Parser
 *
 * Parses quiz markdown files into structured data for PDF generation.
 */

import type {
  ParsedQuiz,
  QuizMetadata,
  QuizQuestion,
  QuizChoice,
  AnswerKeyEntry,
  CaseStudy,
  SubPart,
} from './types';

interface DocumentBoundaries {
  mcStart: number;
  mcEnd: number;
  part2Start: number;
  part2End: number;
  answerKeyStart: number;
}

function findAnswerKeyStart(content: string): number {
  const idxs: number[] = [];
  const re = /^#{1,2} Answer Key\s*$/gm;
  let m: RegExpExecArray | null;
  while ((m = re.exec(content)) !== null) {
    if (m.index !== undefined) idxs.push(m.index);
  }
  return idxs.length ? Math.min(...idxs) : -1;
}

function findMcSectionStart(content: string): number {
  const candidates: number[] = [];
  const q = content.indexOf('## Questions');
  if (q >= 0) candidates.push(q);
  const m1 = content.match(/^# Part I[^\n]*/m);
  if (m1?.index !== undefined) candidates.push(m1.index);
  const m2 = content.match(/^## Part I[^\n]*/m);
  if (m2?.index !== undefined) candidates.push(m2.index);
  return candidates.length ? Math.min(...candidates) : -1;
}

/** Next boundary after start of MC section (relative to slice starting at mcStart). */
function findMcEndRelativeToSlice(slice: string): number {
  const patterns = [/^#{1,2} Part II[^\n]*/m, /^#{1,2} Answer Key\s*$/m, /^## Topic Coverage/m];
  let minRel = -1;
  for (const p of patterns) {
    const m = slice.match(p);
    if (m?.index !== undefined && m.index > 0) {
      if (minRel < 0 || m.index < minRel) minRel = m.index;
    }
  }
  return minRel >= 0 ? minRel : slice.length;
}

function computeBoundaries(content: string): DocumentBoundaries {
  const answerKeyStart = findAnswerKeyStart(content);

  const mcStart = findMcSectionStart(content);
  const contentLen = content.length;
  let mcEnd = contentLen;
  if (mcStart >= 0) {
    const slice = content.slice(mcStart);
    const rel = findMcEndRelativeToSlice(slice);
    mcEnd = mcStart + rel;
  }

  const part2SearchFrom = mcStart >= 0 ? mcEnd : 0;
  const part2SearchEnd = answerKeyStart >= 0 ? answerKeyStart : contentLen;
  const part2Slice = content.slice(part2SearchFrom, part2SearchEnd);
  const p2rel = part2Slice.search(/^#{1,2} Part II[^\n]*/m);
  const part2Start = p2rel >= 0 ? part2SearchFrom + p2rel : -1;
  const part2End = part2SearchEnd;

  return { mcStart, mcEnd, part2Start, part2End, answerKeyStart };
}

/**
 * Match `**(a)**` or `**(a)(i)**`. Group 1 = letter. Group 2 = optional roman numeral.
 */
const SUBPART_MARKER_RE = /\*\*\(([a-z])\)(?:\(([ivx]+)\))?\*\*/gi;

/** `<!-- space: 2.5in -->` anywhere in the chunk. */
const SPACE_ANNOTATION_RE = /<!--\s*space:\s*([\d.]+)\s*in\s*-->/i;

function extractSpaceInches(text: string): number | undefined {
  const m = text.match(SPACE_ANNOTATION_RE);
  if (!m) return undefined;
  const n = parseFloat(m[1]);
  return Number.isFinite(n) && n > 0 ? n : undefined;
}

function extractSubpartsFromBody(body: string): SubPart[] {
  const markers: { letter: string; numeral?: string; start: number; end: number }[] = [];
  const re = new RegExp(SUBPART_MARKER_RE.source, SUBPART_MARKER_RE.flags);
  let m: RegExpExecArray | null;
  while ((m = re.exec(body)) !== null) {
    markers.push({
      letter: m[1].toLowerCase(),
      numeral: m[2]?.toLowerCase(),
      start: m.index,
      end: m.index + m[0].length,
    });
  }

  const subparts: SubPart[] = [];
  const indexByLetter = new Map<string, number>();

  for (let i = 0; i < markers.length; i++) {
    const cur = markers[i];
    const next = markers[i + 1];
    const chunk = body.slice(cur.end, next ? next.start : body.length);
    const spaceInches = extractSpaceInches(chunk);

    if (cur.numeral === undefined) {
      if (indexByLetter.has(cur.letter)) continue;
      indexByLetter.set(cur.letter, subparts.length);
      subparts.push({ letter: cur.letter, spaceInches, subSubParts: [] });
    } else {
      let parentIdx = indexByLetter.get(cur.letter);
      if (parentIdx === undefined) {
        parentIdx = subparts.length;
        indexByLetter.set(cur.letter, parentIdx);
        subparts.push({ letter: cur.letter, subSubParts: [] });
      }
      const parent = subparts[parentIdx];
      if (parent.subSubParts.some(ss => ss.numeral === cur.numeral)) continue;
      parent.subSubParts.push({ numeral: cur.numeral!, spaceInches });
      // When a parent has sub-sub-parts, the parent itself gets no answer area.
      parent.spaceInches = undefined;
    }
  }

  return subparts;
}

function extractPartOneIntro(content: string, mcStart: number, mcEnd: number): string | undefined {
  if (mcStart < 0) return undefined;
  const region = content.slice(mcStart, mcEnd);
  const nl = region.indexOf('\n');
  if (nl < 0) return undefined;
  const afterHeading = region.slice(nl + 1);
  const qm = afterHeading.search(/\n### Question \d+/);
  if (qm < 0) return undefined;
  let intro = afterHeading.slice(0, qm).trim();
  intro = intro.replace(/^---\s*\n?/gm, '').replace(/\n---\s*$/g, '').trim();
  return intro || undefined;
}

function extractCaseStudies(content: string, part2Start: number, part2End: number): {
  heading?: string;
  intro?: string;
  studies: CaseStudy[];
} {
  if (part2Start < 0) return { studies: [] };
  const region = content.slice(part2Start, part2End);
  const firstNl = region.indexOf('\n');
  const headingLine =
    firstNl >= 0 ? region.slice(0, firstNl).replace(/^#+\s*/, '').trim() : region.replace(/^#+\s*/, '').trim();
  const afterHeading = firstNl >= 0 ? region.slice(firstNl + 1) : '';
  const firstCase = afterHeading.search(/^## Case Study /m);
  let intro: string | undefined;
  let body = afterHeading;
  if (firstCase >= 0) {
    let introRaw = afterHeading.slice(0, firstCase).trim();
    introRaw = introRaw.replace(/^---\s*\n?/gm, '').replace(/\n---\s*$/g, '').trim();
    intro = introRaw || undefined;
    body = afterHeading.slice(firstCase);
  }
  const chunks = body.split(/(?=^## Case Study )/m).filter(c => /^## Case Study /m.test(c));
  const studies: CaseStudy[] = [];
  for (const chunk of chunks) {
    const titleMatch = chunk.match(/^## (.+?)\s*$/m);
    const title = titleMatch?.[1]?.trim() ?? 'Case Study';
    const bodyMarkdown = chunk.replace(/^## [^\n]+\n?/, '').trim();
    studies.push({
      title,
      bodyMarkdown,
      subparts: extractSubpartsFromBody(bodyMarkdown),
    });
  }
  return { heading: headingLine || undefined, intro, studies };
}

/**
 * Parse a quiz markdown file into structured data.
 */
export function parseQuizMarkdown(content: string): ParsedQuiz {
  const boundaries = computeBoundaries(content);
  const partOneIntroMarkdown = extractPartOneIntro(content, boundaries.mcStart, boundaries.mcEnd);
  const questions = extractQuestionsFromRegion(content, boundaries.mcStart, boundaries.mcEnd);
  const { heading: partTwoHeading, intro: partTwoIntroMarkdown, studies } = extractCaseStudies(
    content,
    boundaries.part2Start,
    boundaries.part2End
  );
  const caseStudies = studies.length > 0 ? studies : undefined;

  let metadata = extractMetadata(content);
  const instructions = extractInstructions(content, partOneIntroMarkdown);
  const { answerKey, answerKeyOpenEndedMarkdown } = extractAnswerKeyFull(
    content,
    boundaries.answerKeyStart
  );

  if (metadata.questionCount <= 0 && questions.length > 0) {
    metadata = { ...metadata, questionCount: questions.length };
  }

  return {
    metadata,
    instructions,
    questions,
    answerKey,
    partOneIntroMarkdown,
    partTwoHeading,
    partTwoIntroMarkdown,
    caseStudies,
    answerKeyOpenEndedMarkdown,
  };
}

function extractMetadata(content: string): QuizMetadata {
  const titleMatch = content.match(/^# (.+)$/m);
  const title = titleMatch?.[1]?.trim() ?? 'Quiz';

  const topicsMatch = content.match(/\*\*Topics Covered:\*\*\s*(.+)/);
  const coverageMatch = content.match(/\*\*Coverage:\*\*\s*(.+)/);
  const timeLimitMatch = content.match(/\*\*Time Limit:\*\*\s*(.+)/);
  const formatMatch = content.match(/\*\*Format:\*\*\s*(.+)/);
  const courseMatch = content.match(/\*\*Course:\*\*\s*(.+)/);

  const topicsCovered = (topicsMatch?.[1] ?? coverageMatch?.[1] ?? '').trim();
  const timeLimit = (timeLimitMatch?.[1] ?? '').trim();
  const format = (formatMatch?.[1] ?? '').trim();
  const course = courseMatch?.[1]?.trim();

  const countParen = format.match(/\((\d+)\s+questions?\)/i);
  const countLeading = format.match(/^(\d+)\s+multiple[- ]choice/i);
  let questionCount = countParen ? parseInt(countParen[1], 10) : 0;
  if (questionCount <= 0 && countLeading) {
    questionCount = parseInt(countLeading[1], 10);
  }

  const meta: QuizMetadata = {
    title,
    topicsCovered,
    timeLimit,
    format,
    questionCount,
  };
  if (course) meta.course = course;
  return meta;
}

function extractInstructions(content: string, partOneIntro?: string): string[] {
  const instructionsMatch = content.match(/## Instructions\s*\n([\s\S]*?)(?=\n---|\n## )/);
  if (instructionsMatch) {
    const lines = instructionsMatch[1].split('\n');
    return lines
      .filter(line => line.trim().startsWith('-'))
      .map(line => line.replace(/^-\s*/, '').trim());
  }
  if (partOneIntro) {
    const lines = partOneIntro.split('\n').map(l => l.trim());
    const bullets = lines.filter(l => l.startsWith('- ')).map(l => l.replace(/^-\s+/, ''));
    if (bullets.length > 0) return bullets;
  }
  return [];
}

function extractQuestionsFromRegion(content: string, mcStart: number, mcEnd: number): QuizQuestion[] {
  const questions: QuizQuestion[] = [];
  if (mcStart < 0) return questions;

  const questionsSection = content.slice(mcStart, mcEnd);
  const questionBlocks = questionsSection.split(/(?=### Question \d+)/);

  for (const block of questionBlocks) {
  const questionMatch = block.match(/### Question (\d+)[^\n]*\n([\s\S]*)/);
    if (!questionMatch) continue;

    const number = parseInt(questionMatch[1], 10);
    const questionContent = questionMatch[2];
    const parsed = parseQuestionContent(questionContent);

    questions.push({
      number,
      text: parsed.text,
      choices: parsed.choices,
    });
  }

  return questions.sort((a, b) => a.number - b.number);
}

function parseQuestionContent(content: string): { text: string; choices: QuizChoice[] } {
  const lines = content.split('\n');
  const textLines: string[] = [];
  const choices: QuizChoice[] = [];

  let inCodeBlock = false;
  let collectingText = true;

  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      if (collectingText) {
        textLines.push(line);
      }
      continue;
    }

    if (inCodeBlock) {
      textLines.push(line);
      continue;
    }

    const choiceMatch = line.match(/^- ([a-z])\) (.*)$/i);
    if (choiceMatch) {
      collectingText = false;
      choices.push({
        letter: choiceMatch[1].toUpperCase(),
        text: choiceMatch[2],
      });
      continue;
    }

    if (line.trim() === '---') continue;

    if (collectingText && line.trim()) {
      textLines.push(line);
    }
  }

  let text = textLines.join('\n').trim();
  text = text.replace(/\n---\s*$/, '').trim();

  return { text, choices };
}

function extractAnswerKeyFull(
  content: string,
  answerKeyStart: number
): { answerKey?: AnswerKeyEntry[]; answerKeyOpenEndedMarkdown?: string } {
  if (answerKeyStart < 0) return {};

  const section = content.slice(answerKeyStart);
  const rubricHeading = /^## Part II: Case Study Rubric\s*$/m;
  const rubricMatch = section.match(rubricHeading);
  let answerKeyOpenEndedMarkdown: string | undefined;
  let mcPortion = section;

  if (rubricMatch?.index !== undefined) {
    const rubricBody = section.slice(rubricMatch.index + rubricMatch[0].length).trim();
    answerKeyOpenEndedMarkdown = rubricBody || undefined;
    mcPortion = section.slice(0, rubricMatch.index);
  }

  const entries: AnswerKeyEntry[] = [];
  const tableRowPattern = /^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|$/gm;

  function parseAnswersCell(cell: string): string[] {
    const matches = cell.toUpperCase().match(/[A-Z]/g);
    if (!matches) return [];
    const seen = new Set<string>();
    return matches.filter(letter => {
      if (seen.has(letter)) return false;
      seen.add(letter);
      return true;
    });
  }

  let match: RegExpExecArray | null;
  while ((match = tableRowPattern.exec(mcPortion)) !== null) {
    const answers = parseAnswersCell(match[2]);
    if (answers.length === 0) continue;

    entries.push({
      question: parseInt(match[1], 10),
      answers,
      topic: match[3].trim(),
    });
  }

  return {
    answerKey: entries.length > 0 ? entries : undefined,
    answerKeyOpenEndedMarkdown,
  };
}
