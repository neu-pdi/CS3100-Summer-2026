#!/usr/bin/env npx tsx

/**
 * Form 4-person teams from roster and survey data.
 *
 * Usage:
 *   npx tsx scripts/form-teams.ts --instructor Bell
 *   npx tsx scripts/form-teams.ts --instructor all
 *   npm run form:teams -- --instructor Spertus --output ./teams.csv
 */

import { program } from "commander";
import * as path from "path";
import { loadData } from "./lib/csv-parser";
import { formTeams } from "./lib/teaming-algorithm";
import { printConsoleStats, writeTeamsCsv, writeUnmatchedCsv } from "./lib/output";
import type { Instructor, FormTeamsResult, RemainderStrategy } from "./lib/types";

const VALID_INSTRUCTORS: (Instructor | "all")[] = ["Bell", "Shesh", "Spertus", "Vesely", "all"];

program
  .name("form-teams")
  .description("Form 4-person teams from roster and survey data")
  .requiredOption(
    "-i, --instructor <name>",
    "Instructor to process: Bell, Shesh, Spertus, Vesely, or all"
  )
  .option(
    "-r, --roster <path>",
    "Path to roster CSV",
    path.join(process.cwd(), "grade-analysis", "roster.csv")
  )
  .option(
    "-s, --survey <path>",
    "Path to team survey CSV",
    path.join(process.cwd(), "team-survey.csv")
  )
  .option(
    "-o, --output <path>",
    "Path for teams output CSV",
    path.join(process.cwd(), "teams-output.csv")
  )
  .option(
    "-u, --unmatched <path>",
    "Path for unmatched students CSV",
    path.join(process.cwd(), "unmatched-students.csv")
  )
  .option(
    "--remainder <strategy>",
    "When can't make groups of 4: 'prefer-3' (make several groups of 3) or 'allow-5' (allow groups of 5)"
  )
  .option(
    "--no-prefer-mutual",
    "Disable mutual-pair prioritization (may produce unmatched pairs)"
  )
  .action(async (options) => {
    const instructor = options.instructor as Instructor | "all";
    if (!VALID_INSTRUCTORS.includes(instructor)) {
      console.error(
        `Invalid instructor: ${instructor}. Must be one of: ${VALID_INSTRUCTORS.join(", ")}`
      );
      process.exit(1);
    }

    const remainderStrategy = options.remainder as RemainderStrategy;
    if (remainderStrategy && !["prefer-3", "allow-5"].includes(remainderStrategy)) {
      console.error(`Invalid remainder strategy: ${remainderStrategy}. Use 'prefer-3' or 'allow-5'`);
      process.exit(1);
    }

    const rosterPath = path.resolve(options.roster);
    const surveyPath = path.resolve(options.survey);

    try {
      const { students, rosterEmails, unmatchedStudents } = loadData(
        rosterPath,
        surveyPath,
        instructor
      );

      const { teams, unmatchedStudents: allUnmatched, unmatchedPreferencePairs } = formTeams({
        students,
        rosterEmails,
        unmatchedStudents,
        remainderStrategy: remainderStrategy || undefined,
        preferMutualPairs: !options.noPreferMutual,
      });

      const studentsWithSurvey = students.filter((s) => s.surveyData).length;
      const studentsWithoutSurvey = students.length - studentsWithSurvey;

      const result: FormTeamsResult = {
        teams,
        unmatchedStudents: allUnmatched,
        unmatchedPreferencePairs,
        stats: {
          totalStudents: students.length,
          studentsWithSurvey,
          studentsWithoutSurvey,
          teamsByPreference: teams.filter((t) => t.formationType === "preference").length,
          teamsByAlgorithm: teams.filter((t) => t.formationType === "algorithm").length,
          teamsWithScheduleConcern: teams.filter((t) => t.flags.includes("schedule_concern")).length,
          teamsWithAvoidViolation: teams.filter((t) => t.flags.includes("avoid_violation")).length,
          incompleteTeams: teams.filter((t) => t.flags.includes("incomplete")).length,
        },
      };

      printConsoleStats(result);
      writeTeamsCsv(teams, options.output);
      writeUnmatchedCsv(allUnmatched, options.unmatched);
    } catch (err) {
      console.error("Error:", err);
      process.exit(1);
    }
  });

program.parse();
