/**
 * Quiz to PDF Types
 */

export interface QuizMetadata {
  title: string;
  topicsCovered: string;
  timeLimit: string;
  format: string;
  questionCount: number;
  /** From **Course:** when Topics Covered style is absent */
  course?: string;
}

export interface QuizChoice {
  letter: string;
  text: string;
}

export interface QuizQuestion {
  number: number;
  text: string;
  choices: QuizChoice[];
}

export interface AnswerKeyEntry {
  question: number;
  answers: string[];
  topic: string;
}

/** One `**(d)(i)**`-style sub-sub-part nested under a subpart */
export interface SubSubPart {
  /** Lowercase roman numeral e.g. 'i', 'ii', 'iii' */
  numeral: string;
  /** Vertical space for the answer area, inches. Omit to use default. */
  spaceInches?: number;
}

/** One `**(a)**`-style subpart */
export interface SubPart {
  /** Lowercase letter e.g. 'a', 'b' */
  letter: string;
  /** Vertical space for the answer area, inches. Ignored when subSubParts is non-empty. */
  spaceInches?: number;
  /** Nested `**(a)(i)**`-style sub-sub-parts in document order. */
  subSubParts: SubSubPart[];
}

/** Open-ended case study (Part II) */
export interface CaseStudy {
  title: string;
  bodyMarkdown: string;
  subparts: SubPart[];
}

export interface ParsedQuiz {
  metadata: QuizMetadata;
  instructions: string[];
  questions: QuizQuestion[];
  answerKey?: AnswerKeyEntry[];
  /** Intro after Part I / Questions heading, before first ### Question */
  partOneIntroMarkdown?: string;
  /** Raw Part II document heading line (without leading #) */
  partTwoHeading?: string;
  /** Text after Part II heading and before first ## Case Study */
  partTwoIntroMarkdown?: string;
  caseStudies?: CaseStudy[];
  /** Instructor rubric markdown (Part II answer key) */
  answerKeyOpenEndedMarkdown?: string;
}

export interface CliOptions {
  inputFile: string;
  outputFile?: string;
  version?: string;
  includeCover: boolean;
  includeAnswers: boolean;
  margin: string;
  shuffle: boolean;
  seed?: number;
  /** Place Part II write-in areas inline under each prompt instead of on a separate answer sheet. */
  inlineAnswers: boolean;
  /** Add initials space in top-right margin of every page. */
  initialsSpace: boolean;
  /** Skip the blank page that normally follows the cover sheet. */
  noBlankPage: boolean;
}

export interface PdfOptions {
  version?: string;
  includeCover: boolean;
  includeAnswers: boolean;
  margin: string;
  /** Place Part II write-in areas inline under each prompt instead of on a separate answer sheet. */
  inlineAnswers: boolean;
  /** Add initials space in top-right margin of every page. */
  initialsSpace: boolean;
  /** Skip the blank page that normally follows the cover sheet. */
  noBlankPage: boolean;
}
