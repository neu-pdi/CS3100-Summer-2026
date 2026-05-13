/**
 * CSV loading and joining logic for team formation.
 */

import * as fs from "fs";
import * as path from "path";
import { parse } from "csv-parse/sync";
import type {
  Student,
  Instructor,
  UnmatchedStudent,
  RosterRow,
  SkillScores,
} from "./types.js";

const EMAIL_REGEX = /[a-zA-Z0-9._%+-]+@northeastern\.edu/gi;

/** Normalize email to lowercase for matching */
export function normalizeEmail(email: string): string {
  return (email || "").trim().toLowerCase();
}

/** Levenshtein (edit) distance between two strings */
function editDistance(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  const dp: number[][] = Array(m + 1)
    .fill(null)
    .map(() => Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      );
    }
  }
  return dp[m][n];
}

const MAX_EDIT_DISTANCE = 3;

/** Swap foo.bar -> bar.foo in local part (for format first.last@northeastern.edu) */
function swapLocalPart(email: string): string | null {
  const at = email.indexOf("@");
  if (at <= 0) return null;
  const local = email.slice(0, at);
  const domain = email.slice(at);
  const parts = local.split(".");
  if (parts.length !== 2) return null;
  return `${parts[1]}.${parts[0]}${domain}`;
}

/**
 * Fuzzy match: find roster email for an entered email.
 * Tries: 1) exact match, 2) swapped format (foo.bar -> bar.foo), 3) edit distance 1-3.
 * Returns null if no match or multiple close matches (for edit distance).
 */
export function fuzzyMatchEmail(
  enteredEmail: string,
  rosterEmails: Set<string>,
  maxDistance: number = MAX_EDIT_DISTANCE
): string | null {
  const normalized = normalizeEmail(enteredEmail);
  if (rosterEmails.has(normalized)) return normalized;

  const swapped = swapLocalPart(normalized);
  if (swapped && rosterEmails.has(swapped)) return swapped;

  const closeMatches: string[] = [];
  for (const rosterEmail of rosterEmails) {
    const dist = editDistance(normalized, rosterEmail);
    if (dist >= 1 && dist <= maxDistance) {
      closeMatches.push(rosterEmail);
    }
  }
  return closeMatches.length === 1 ? closeMatches[0]! : null;
}

/** Extract instructor name from class_section_name (e.g., "Bell - MWR 10:30a" -> "Bell") */
export function extractInstructor(classSection: string): Instructor | null {
  if (!classSection || classSection === "null") return null;
  const match = classSection.match(/^(Bell|Shesh|Spertus|Vesely)\s*-/);
  return match ? (match[1] as Instructor) : null;
}

/** Get teaming pool key - Spertus sections combine into one pool */
export function getTeamingPool(instructor: Instructor, classSection: string): string {
  if (instructor === "Spertus") {
    return "Spertus";
  }
  return classSection;
}

/** Parse availability into time slot count (schedule constrained = < 2 slots) */
function parseAvailabilitySlots(availabilityText: string): string[] {
  if (!availabilityText || !availabilityText.trim()) return [];
  const slots: string[] = [];
  const lower = availabilityText.toLowerCase();
  if (lower.includes("weekday mornings") || lower.includes("before noon")) slots.push("mornings");
  if (lower.includes("weekday afternoons") || lower.includes("noon") || lower.includes("5pm")) slots.push("afternoons");
  if (lower.includes("weekday evenings") || lower.includes("after 5pm")) slots.push("evenings");
  if (lower.includes("weekends")) slots.push("weekends");
  return slots;
}

/** Parse skill scores from survey (0-3 each, total 0-9) */
export function calculateSkillScores(
  java: string,
  gui: string,
  git: string
): SkillScores {
  const javaScore = scoreJava(java);
  const guiScore = scoreGui(gui);
  const gitScore = scoreGit(git);
  return {
    java: javaScore,
    gui: guiScore,
    git: gitScore,
    total: javaScore + guiScore + gitScore,
  };
}

function scoreJava(val: string): number {
  const v = (val || "").toLowerCase();
  if (v.includes("none") || !v) return 0;
  if (v.includes("2510") || v.includes("fundamentals")) return 1;
  if (v.includes("ap ") || v.includes("ap computer")) return 2;
  if (v.includes("other") || v.includes("work")) return 3;
  return 0;
}

function scoreGui(val: string): number {
  const v = (val || "").toLowerCase();
  if (v.includes("none") || !v) return 0;
  if (v.includes("some") || v.includes("exposure") || v.includes("tutorial")) return 1;
  if (v.includes("comfortable")) return 2;
  if (v.includes("experienced")) return 3;
  return 0;
}

function scoreGit(val: string): number {
  const v = (val || "").toLowerCase();
  if (v.includes("never") || v.includes("submitting") || !v) return 0;
  if (v.includes("some") || v.includes("personal") || v.includes("basic")) return 1;
  if (v.includes("comfortable") || v.includes("branches")) return 2;
  if (v.includes("experienced") || v.includes("code review")) return 3;
  return 0;
}

/** Extract emails from free-text field (preferred teammates or avoid list) */
export function extractEmailsFromText(text: string): string[] {
  if (!text || !text.trim()) return [];
  const matches = text.match(EMAIL_REGEX) || [];
  return [...new Set(matches.map((m) => normalizeEmail(m)))];
}

export interface LoadDataResult {
  students: Student[];
  rosterEmails: Set<string>;
  unmatchedStudents: UnmatchedStudent[];
}

/** Load roster and survey, join by email, track unmatched */
export function loadData(
  rosterPath: string,
  surveyPath: string,
  instructorFilter: Instructor | "all"
): LoadDataResult {
  const rosterContent = fs.readFileSync(path.resolve(rosterPath), "utf-8");
  const surveyContent = fs.readFileSync(path.resolve(surveyPath), "utf-8");

  const rosterRows = parse(rosterContent, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
  }) as Record<string, string>[];

  const surveyRows = parse(surveyContent, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
    relax_column_count: true,
  }) as Record<string, string>[];

  const rosterEmails = new Set<string>();
  const rosterByEmail = new Map<string, RosterRow>();
  const unmatchedStudents: UnmatchedStudent[] = [];

  for (const row of rosterRows) {
    const email = normalizeEmail(row.email || row.Email || "");
    if (!email) continue;
    rosterEmails.add(email);
    const classSection = row.class_section_name || row["Class Section"] || "";
    const inst = extractInstructor(classSection);
    if (!inst) continue; // skip null sections
    const rosterRow: RosterRow = {
      name: row.Name || row["Full name"] || "",
      email: row.email || row.Email || "",
      class_section_name: classSection,
      lab_section_name: row.lab_section_name || "",
      private_profile_id: row.private_profile_id || "",
      public_profile_id: row.public_profile_id || "",
    };
    rosterByEmail.set(email, rosterRow);
  }

  const surveyRowsByEmail = new Map<string, Record<string, string>[]>();
  for (const row of surveyRows) {
    const email = normalizeEmail(row["Northeastern Email"] || row.email || "");
    if (!email) continue;
    if (!surveyRowsByEmail.has(email)) surveyRowsByEmail.set(email, []);
    surveyRowsByEmail.get(email)!.push(row);
  }

  const surveyByEmail = new Map<string, Record<string, string>>();
  for (const [email, rows] of surveyRowsByEmail) {
    const latest = rows.length === 1
      ? rows[0]!
      : rows.sort((a, b) => {
          const tsA = new Date(a.Timestamp || 0).getTime();
          const tsB = new Date(b.Timestamp || 0).getTime();
          return tsB - tsA;
        })[0]!;
    const fullName = latest["Full name"] || latest.name || "";
    let rosterEmail = rosterEmails.has(email) ? email : fuzzyMatchEmail(email, rosterEmails);
    if (rosterEmail) {
      surveyByEmail.set(rosterEmail, latest);
    } else {
      unmatchedStudents.push({
        email,
        name: fullName,
        category: "survey_respondent",
        originalText: email,
      });
    }
  }

  const students: Student[] = [];
  for (const [email, rosterRow] of rosterByEmail) {
    const inst = extractInstructor(rosterRow.class_section_name);
    if (!inst) continue;
    if (instructorFilter !== "all" && inst !== instructorFilter) continue;

    const surveyRow = surveyByEmail.get(email);
    let surveyData: Student["surveyData"];
    let skillScores: SkillScores | undefined;
    let isScheduleConstrained = false;

    if (surveyRow) {
      const preferredRaw = surveyRow["Preferred teammates"] || "";
      const avoidRaw = surveyRow["Students to avoid"] || "";
      const availabilityRaw = surveyRow["When will you generally be available for team meetings? (Check all that apply)"] || "";
      const availabilitySlots = parseAvailabilitySlots(availabilityRaw);
      const bestDaysRaw = surveyRow["When are your best days for team meetings? (Check all that apply)"] || "";
      const bestDays = bestDaysRaw ? bestDaysRaw.split(",").map((s) => s.trim()).filter(Boolean) : [];

      surveyData = {
        preferredTeammates: extractEmailsFromText(preferredRaw),
        studentsToAvoid: extractEmailsFromText(avoidRaw),
        javaExperience: surveyRow["Java Experience Prior to CS 3100"] || "",
        guiExperience: surveyRow["GUI/Desktop Application Experience Prior to CS 3100"] || "",
        gitExperience: surveyRow["Git Collaboration Experience Prior to CS 3100"] || "",
        availabilitySlots,
        bestDays,
      };
      skillScores = calculateSkillScores(
        surveyData.javaExperience,
        surveyData.guiExperience,
        surveyData.gitExperience
      );
      isScheduleConstrained = availabilitySlots.length < 2;
    }

    students.push({
      name: rosterRow.name,
      email: normalizeEmail(rosterRow.email),
      instructor: inst,
      section: rosterRow.class_section_name,
      labSection: rosterRow.lab_section_name,
      surveyData,
      skillScores,
      isScheduleConstrained,
    });
  }

  return { students, rosterEmails, unmatchedStudents };
}
