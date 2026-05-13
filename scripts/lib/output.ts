/**
 * Console and CSV output for team formation results.
 */

import * as fs from "fs";
import * as path from "path";
import { stringify } from "csv-stringify/sync";
import type { Team, UnmatchedStudent, FormTeamsResult } from "./types.js";

export function printConsoleStats(result: FormTeamsResult): void {
  const { teams, unmatchedStudents, unmatchedPreferencePairs, stats } = result;

  console.log("\n=== Team Formation Summary ===\n");
  console.log(`Total students: ${stats.totalStudents}`);
  console.log(`With survey: ${stats.studentsWithSurvey}`);
  console.log(`Without survey: ${stats.studentsWithoutSurvey}`);
  console.log(`\nTeams formed: ${teams.length}`);
  console.log(`  - By preference: ${stats.teamsByPreference}`);
  console.log(`  - By algorithm: ${stats.teamsByAlgorithm}`);
  console.log(`  - With schedule concern: ${stats.teamsWithScheduleConcern}`);
  console.log(`  - With avoid violation: ${stats.teamsWithAvoidViolation}`);
  console.log(`  - Incomplete (size < 4): ${stats.incompleteTeams}`);
  console.log(`\nUnmatched references: ${unmatchedStudents.length}`);
  const byCategory = unmatchedStudents.reduce(
    (acc, u) => {
      acc[u.category] = (acc[u.category] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );
  for (const [cat, count] of Object.entries(byCategory)) {
    console.log(`  - ${cat}: ${count}`);
  }

  if (unmatchedPreferencePairs.length > 0) {
    console.log(`\nStudents who wanted to work together but couldn't be matched (${unmatchedPreferencePairs.length} pairs):`);
    for (const p of unmatchedPreferencePairs) {
      console.log(`  - ${p.nameA} (${p.studentA}) <-> ${p.nameB} (${p.studentB})`);
    }
    console.log(
      "\n  (One was assigned as a hanger-on to another group before their mutual component was processed. Omit --no-prefer-mutual to prioritize keeping mutual pairs together.)"
    );
  }

  console.log("");
}

export function writeTeamsCsv(teams: Team[], outputPath: string): void {
  const rows = teams.map((team) => {
    const row: Record<string, string> = {
      team_id: team.teamId,
      instructor: team.instructor,
      section: team.section,
      formation_type: team.formationType,
      flags: team.flags.join("; "),
    };
    team.members.forEach((m, i) => {
      const n = i + 1;
      row[`member${n}_name`] = m.name;
      row[`member${n}_email`] = m.email;
      row[`member${n}_skills`] = m.skillScores
        ? `${m.skillScores.total} (J:${m.skillScores.java} G:${m.skillScores.gui} Git:${m.skillScores.git})`
        : "N/A";
      row[`member${n}_availability`] = m.surveyData?.availabilitySlots?.join(", ") || "N/A";
    });
  /*  for (let i = team.members.length; i < 4; i++) {
      const n = i + 1;
      row[`member${n}_name`] = "";
      row[`member${n}_email`] = "";
      row[`member${n}_skills`] = "";
      row[`member${n}_availability`] = "";
    }*/
    return row;
  });

  const csv = stringify(rows, { header: true });
  fs.writeFileSync(path.resolve(outputPath), csv, "utf-8");
  console.log(`Teams written to ${outputPath}`);
}

export function writeUnmatchedCsv(unmatched: UnmatchedStudent[], outputPath: string): void {
  const rows = unmatched.map((u) => ({
    email: u.email,
    name: u.name || "",
    category: u.category,
    referenced_by: u.referencedBy || "",
    original_text: u.originalText || "",
  }));

  const csv = stringify(rows, { header: true });
  fs.writeFileSync(path.resolve(outputPath), csv, "utf-8");
  console.log(`Unmatched students written to ${outputPath}`);
}
