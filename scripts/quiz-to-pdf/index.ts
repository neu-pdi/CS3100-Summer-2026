#!/usr/bin/env npx tsx
/**
 * Quiz to PDF Converter
 *
 * Converts quiz markdown files to beautiful print-ready PDFs with:
 * - Auto-generated cover sheet with answer bubble grid
 * - Optional version watermark on every page
 * - Syntax-highlighted code blocks
 *
 * Usage:
 *   npm run quiz:pdf quizzes/quiz1.md
 *   npm run quiz:pdf quizzes/quiz1.md --version "Form A"
 *   npm run quiz:pdf quizzes/quiz1.md --output build/quiz1.pdf
 *   npm run quiz:pdf quizzes/quiz1.md --no-cover
 *   npm run quiz:pdf quizzes/quiz1.md --no-answers
 */

import * as fs from 'fs';
import * as path from 'path';
import { parseQuizMarkdown } from './parser';
import { renderQuizToHtml } from './renderer';
import { generatePdf } from './pdf-generator';
import type { CliOptions, PdfOptions, ParsedQuiz, QuizQuestion, QuizChoice, AnswerKeyEntry } from './types';

// ============================================================================
// Shuffling Utilities
// ============================================================================

/**
 * Seeded random number generator (Mulberry32)
 */
function createRng(seed: number): () => number {
  return function() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

/**
 * Fisher-Yates shuffle with seeded RNG
 */
function shuffleArray<T>(array: T[], rng: () => number): T[] {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

/**
 * Shuffle questions and their answer choices, updating the answer key accordingly
 */
function shuffleQuiz(quiz: ParsedQuiz, seed: number): ParsedQuiz {
  const rng = createRng(seed);
  const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

  // Shuffle questions
  const shuffledQuestions = shuffleArray(quiz.questions, rng);

  // For each question, shuffle its choices and track the mapping
  const newQuestions: QuizQuestion[] = [];
  const newAnswerKey: AnswerKeyEntry[] = [];

  shuffledQuestions.forEach((q, newIndex) => {
    const newNumber = newIndex + 1;

    // Shuffle choices for this question
    const shuffledChoices = shuffleArray(q.choices, rng);

    // Create new choices with updated letters
    const newChoices: QuizChoice[] = shuffledChoices.map((choice, idx) => ({
      letter: letters[idx],
      text: choice.text,
    }));

    newQuestions.push({
      number: newNumber,
      text: q.text,
      choices: newChoices,
    });

    // Update answer key if it exists
    if (quiz.answerKey) {
      const originalAnswer = quiz.answerKey.find(a => a.question === q.number);
      if (originalAnswer) {
        // Preserve support for select-all questions with multiple correct options.
        const mappedAnswers = originalAnswer.answers
          .map(answerLetter => {
            const originalCorrectChoice = q.choices.find(c => c.letter === answerLetter);
            if (!originalCorrectChoice) return null;

            const newChoiceIndex = shuffledChoices.findIndex(c => c.text === originalCorrectChoice.text);
            if (newChoiceIndex < 0) return null;
            return letters[newChoiceIndex];
          })
          .filter((letter): letter is string => !!letter)
          .sort();

        if (mappedAnswers.length > 0) {
          newAnswerKey.push({
            question: newNumber,
            answers: mappedAnswers,
            topic: originalAnswer.topic,
          });
        }
      }
    }
  });

  // Shuffle case studies (keep subparts in original order within each)
  // Renumber titles: "Case Study 3: ..." → "Case Study 1: ..."
  const shuffledCaseStudies = quiz.caseStudies
    ? shuffleArray(quiz.caseStudies, rng).map((cs, idx) => ({
        ...cs,
        title: cs.title.replace(/^Case Study \d+/, `Case Study ${idx + 1}`),
      }))
    : undefined;

  return {
    ...quiz,
    questions: newQuestions,
    answerKey: quiz.answerKey ? newAnswerKey : undefined,
    caseStudies: shuffledCaseStudies,
  };
}

// ============================================================================
// CLI Argument Parsing
// ============================================================================

function printHelp(): void {
  console.log(`
Quiz to PDF Converter - Generate print-ready PDFs from quiz markdown files

Usage:
  npx tsx scripts/quiz-to-pdf/index.ts [options] <quiz-file.md>

Arguments:
  <quiz-file.md>        Path to quiz markdown file

Options:
  --version <name>      Version name to print on every page (e.g., "Form A")
  --output <path>       Output PDF path (default: same name as input with .pdf)
  --margin <size>       Page margins (default: "1in", e.g., "0.75in", "1in")
  --shuffle             Randomize question and answer order
  --seed <number>       Seed for reproducible shuffling (default: random)
  --no-cover            Skip cover sheet generation
  --no-answers          Exclude answer key from output
  --inline-answers      Place Part II answer space under each prompt
                        (instead of a separate answer sheet after the cover)
  --initials            Add initials space in top-right margin of every page
  --no-blank-page       Skip the blank page after the cover sheet
  --help                Show this help message

Examples:
  # Basic conversion
  npm run quiz:pdf -- quizzes/quiz1.md

  # With version watermark
  npm run quiz:pdf -- quizzes/quiz1.md --version "Form A"

  # Randomized version (different each time)
  npm run quiz:pdf -- quizzes/quiz1.md --shuffle --version "Form A"

  # Reproducible randomized version (same shuffle with same seed)
  npm run quiz:pdf -- quizzes/quiz1.md --shuffle --seed 12345 --version "Form A"

  # Custom output path
  npm run quiz:pdf -- quizzes/quiz1.md --output build/quiz1-form-a.pdf --version "Form A"

  # Student version (no answer key)
  npm run quiz:pdf -- quizzes/quiz1.md --no-answers

  # Questions only (no cover sheet or answers)
  npm run quiz:pdf -- quizzes/quiz1.md --no-cover --no-answers
`);
}

function parseArgs(args: string[]): CliOptions | null {
  const options: CliOptions = {
    inputFile: '',
    includeCover: true,
    includeAnswers: true,
    margin: '1in',
    shuffle: false,
    inlineAnswers: false,
    initialsSpace: false,
    noBlankPage: false,
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];

    if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (arg === '--version') {
      i++;
      if (i >= args.length) {
        console.error('Error: --version requires a value');
        return null;
      }
      options.version = args[i];
    } else if (arg === '--output') {
      i++;
      if (i >= args.length) {
        console.error('Error: --output requires a value');
        return null;
      }
      options.outputFile = args[i];
    } else if (arg === '--margin') {
      i++;
      if (i >= args.length) {
        console.error('Error: --margin requires a value');
        return null;
      }
      options.margin = args[i];
    } else if (arg === '--no-cover') {
      options.includeCover = false;
    } else if (arg === '--no-answers') {
      options.includeAnswers = false;
    } else if (arg === '--inline-answers') {
      options.inlineAnswers = true;
    } else if (arg === '--initials') {
      options.initialsSpace = true;
    } else if (arg === '--no-blank-page') {
      options.noBlankPage = true;
    } else if (arg === '--shuffle') {
      options.shuffle = true;
    } else if (arg === '--seed') {
      i++;
      if (i >= args.length) {
        console.error('Error: --seed requires a value');
        return null;
      }
      const seed = parseInt(args[i], 10);
      if (isNaN(seed)) {
        console.error('Error: --seed must be a number');
        return null;
      }
      options.seed = seed;
    } else if (arg.startsWith('--')) {
      console.error(`Error: Unknown option: ${arg}`);
      return null;
    } else {
      // Positional argument (input file)
      if (options.inputFile) {
        console.error('Error: Only one input file can be specified');
        return null;
      }
      options.inputFile = arg;
    }
    i++;
  }

  if (!options.inputFile) {
    console.error('Error: No input file specified');
    printHelp();
    return null;
  }

  return options;
}

// ============================================================================
// Main
// ============================================================================

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    printHelp();
    process.exit(1);
  }

  const options = parseArgs(args);
  if (!options) {
    process.exit(1);
  }

  // Resolve input file path
  const inputPath = path.resolve(options.inputFile);
  if (!fs.existsSync(inputPath)) {
    console.error(`Error: File not found: ${inputPath}`);
    process.exit(1);
  }

  // Determine output path
  const outputPath = options.outputFile
    ? path.resolve(options.outputFile)
    : inputPath.replace(/\.md$/, '.pdf');

  // Ensure output directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log(`Converting: ${inputPath}`);
  if (options.version) {
    console.log(`Version: ${options.version}`);
  }
  console.log(`Output: ${outputPath}`);

  try {
    // Read and parse quiz markdown
    const content = fs.readFileSync(inputPath, 'utf-8');
    let quiz = parseQuizMarkdown(content);

    console.log(`Found ${quiz.questions.length} multiple-choice questions`);
    if (quiz.caseStudies?.length) {
      console.log(`Found ${quiz.caseStudies.length} case studies (Part II)`);
    }

    // Shuffle if requested
    if (options.shuffle) {
      const seed = options.seed ?? Math.floor(Math.random() * 1000000);
      console.log(`Shuffling with seed: ${seed}`);
      quiz = shuffleQuiz(quiz, seed);
    }

    // Render to HTML
    const pdfOptions: PdfOptions = {
      version: options.version,
      includeCover: options.includeCover,
      includeAnswers: options.includeAnswers,
      margin: options.margin,
      inlineAnswers: options.inlineAnswers,
      initialsSpace: options.initialsSpace,
      noBlankPage: options.noBlankPage,
    };
    const rendered = await renderQuizToHtml(quiz, pdfOptions);

    // Generate PDF
    console.log('Generating PDF...');
    await generatePdf(rendered, { outputPath, margin: options.margin, version: options.version, initialsSpace: options.initialsSpace, includeCover: options.includeCover });

    // When --no-answers, generate a separate answer key PDF
    if (!options.includeAnswers) {
      const answerKeyRendered = await renderQuizToHtml(quiz, { ...pdfOptions, includeAnswers: true });
      if (answerKeyRendered.answerKeyHtml) {
        const answersPath = outputPath.replace(/\.pdf$/, '_Answers.pdf');
        await generatePdf(
          { quizHtml: answerKeyRendered.answerKeyHtml },
          { outputPath: answersPath, margin: options.margin, version: options.version }
        );
        console.log(`Answer key: ${answersPath}`);
      }
    }

    console.log('Done!');
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
