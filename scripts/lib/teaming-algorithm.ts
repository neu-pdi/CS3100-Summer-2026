/**
 * Team formation algorithm: preferences, skill balancing, schedule constraints.
 */

import type { Student, Team, UnmatchedStudent, UnmatchedPreferencePair, RemainderStrategy } from "./types.js";
import {
  getTeamingPool,
  extractEmailsFromText,
  fuzzyMatchEmail,
} from "./csv-parser";

export interface AlgorithmInput {
  students: Student[];
  rosterEmails: Set<string>;
  unmatchedStudents: UnmatchedStudent[];
  remainderStrategy?: RemainderStrategy;
  /** When true (default), avoid using as hanger-on students who have unassigned mutual partners */
  preferMutualPairs?: boolean;
}

/** Add unmatched preferred/avoid references to the list (uses fuzzy match: only unmatched if no unique close match) */
function trackUnmatchedReferences(
  students: Student[],
  rosterEmails: Set<string>,
  unmatched: UnmatchedStudent[]
): void {
  for (const student of students) {
    if (!student.surveyData) continue;
    const refBy = student.email;
    for (const email of student.surveyData.preferredTeammates) {
      const matched = rosterEmails.has(email) || fuzzyMatchEmail(email, rosterEmails);
      if (!matched) {
        unmatched.push({
          email,
          category: "preferred_teammate",
          referencedBy: refBy,
          originalText: email,
        });
      }
    }
    for (const email of student.surveyData.studentsToAvoid) {
      const matched = rosterEmails.has(email) || fuzzyMatchEmail(email, rosterEmails);
      if (!matched) {
        unmatched.push({
          email,
          category: "avoid_list",
          referencedBy: refBy,
          originalText: email,
        });
      }
    }
  }
}

/** Resolve preferred email to roster email (exact or fuzzy match within pool) */
function resolveToRosterEmail(enteredEmail: string, rosterEmails: Set<string>): string | null {
  return rosterEmails.has(enteredEmail) ? enteredEmail : fuzzyMatchEmail(enteredEmail, rosterEmails);
}

/** Build mutual preference graph: A wants B AND B wants A */
function buildMutualPreferences(students: Student[]): Map<string, Set<string>> {
  const byEmail = new Map<string, Student>();
  for (const s of students) byEmail.set(s.email, s);
  const rosterEmails = new Set(students.map((s) => s.email));

  const mutual = new Map<string, Set<string>>();
  for (const student of students) {
    if (!student.surveyData?.preferredTeammates?.length) continue;
    for (const pref of student.surveyData.preferredTeammates) {
      const resolved = resolveToRosterEmail(pref, rosterEmails);
      if (!resolved || !byEmail.has(resolved)) continue;
      const other = byEmail.get(resolved)!;
      const otherPrefs = other.surveyData?.preferredTeammates || [];
      const otherWantsMe = otherPrefs.includes(student.email) || otherPrefs.some((p) => resolveToRosterEmail(p, rosterEmails) === student.email);
      if (otherWantsMe) {
        if (!mutual.has(student.email)) mutual.set(student.email, new Set());
        mutual.get(student.email)!.add(resolved);
        if (!mutual.has(resolved)) mutual.set(resolved, new Set());
        mutual.get(resolved)!.add(student.email);
      }
    }
  }
  return mutual;
}

/** Find connected components (mutual preference clusters) */
function findConnectedComponents(
  mutual: Map<string, Set<string>>
): Set<string>[] {
  const visited = new Set<string>();
  const components: Set<string>[] = [];

  function dfs(email: string, component: Set<string>) {
    if (visited.has(email)) return;
    visited.add(email);
    component.add(email);
    for (const neighbor of mutual.get(email) || []) {
      dfs(neighbor, component);
    }
  }

  for (const email of mutual.keys()) {
    if (visited.has(email)) continue;
    const component = new Set<string>();
    dfs(email, component);
    components.push(component);
  }
  return components;
}

/** Find hangers on: students who listed someone in the group (one-way preference) but aren't in the group */
function findHangersOn(
  groupEmails: Set<string>,
  poolStudents: Student[],
  rosterEmails: Set<string>
): Student[] {
  const hangers: Student[] = [];
  for (const s of poolStudents) {
    if (groupEmails.has(s.email)) continue;
    if (!s.surveyData?.preferredTeammates?.length) continue;
    for (const pref of s.surveyData.preferredTeammates) {
      const resolved = resolveToRosterEmail(pref, rosterEmails);
      if (resolved && groupEmails.has(resolved)) {
        hangers.push(s);
        break;
      }
    }
  }
  return hangers;
}

/** Resolve avoid-list email to roster email (for comparison) */
function resolveAvoidEmail(avoidEmail: string, rosterEmails: Set<string>): string | null {
  return rosterEmails.has(avoidEmail) ? avoidEmail : fuzzyMatchEmail(avoidEmail, rosterEmails);
}

/** Check if adding candidate would create avoid violation with existing members */
function wouldAvoidViolation(
  candidate: Student,
  existingMembers: Student[],
  rosterEmails: Set<string>
): boolean {
  const existingEmails = new Set(existingMembers.map((m) => m.email));
  for (const m of existingMembers) {
    for (const avoid of m.surveyData?.studentsToAvoid || []) {
      const resolved = resolveAvoidEmail(avoid, rosterEmails);
      if (resolved === candidate.email) return true;
    }
  }
  for (const avoid of candidate.surveyData?.studentsToAvoid || []) {
    const resolved = resolveAvoidEmail(avoid, rosterEmails);
    if (resolved && existingEmails.has(resolved)) return true;
  }
  return false;
}

/** Check if team has avoid list violation */
function hasAvoidViolation(members: Student[]): boolean {
  const emails = new Set(members.map((m) => m.email));
  for (const m of members) {
    for (const avoid of m.surveyData?.studentsToAvoid || []) {
      if (emails.has(avoid)) return true;
    }
  }
  return false;
}

/** Check if team has schedule concern (constrained students without overlap) */
function hasScheduleConcern(members: Student[]): boolean {
  const constrained = members.filter((m) => m.isScheduleConstrained);
  if (constrained.length < 2) return false;
  for (let i = 0; i < constrained.length; i++) {
    for (let j = i + 1; j < constrained.length; j++) {
      const a = constrained[i].surveyData?.availabilitySlots || [];
      const b = constrained[j].surveyData?.availabilitySlots || [];
      const overlap = a.some((s) => b.includes(s));
      if (!overlap) return true;
    }
  }
  return false;
}

/** Form teams from students */
export function formTeams(input: AlgorithmInput): {
  teams: Team[];
  unmatchedStudents: UnmatchedStudent[];
} {
  const { students, rosterEmails, unmatchedStudents, remainderStrategy, preferMutualPairs = true } = input;
  const unmatched = [...unmatchedStudents];

  trackUnmatchedReferences(students, rosterEmails, unmatched);

  const poolToStudents = new Map<string, Student[]>();
  for (const s of students) {
    const pool = getTeamingPool(s.instructor, s.section);
    if (!poolToStudents.has(pool)) poolToStudents.set(pool, []);
    poolToStudents.get(pool)!.push(s);
  }

  const teams: Team[] = [];
  const assigned = new Set<string>();
  let teamCounter = 0;

  for (const [pool, poolStudents] of poolToStudents) {
    const mutual = buildMutualPreferences(poolStudents);
    let components = findConnectedComponents(mutual);
    if (preferMutualPairs) {
      components = components.sort((a, b) => b.size - a.size);
    }

    for (const component of components) {
      // Filter out students already assigned (e.g. as hangers-on to a prior component)
      const arr = [...component].filter((e) => !assigned.has(e));
      if (arr.length === 0) continue;

      const seedMembers = arr
        .map((e) => poolStudents.find((s) => s.email === e)!)
        .filter(Boolean);

      if (hasAvoidViolation(seedMembers)) continue;

      if (arr.length === 4) {
        for (const m of seedMembers) assigned.add(m.email);
        teams.push({
          teamId: `team-${++teamCounter}`,
          instructor: seedMembers[0].instructor,
          section: seedMembers[0].section,
          members: seedMembers,
          formationType: "preference",
          flags: [],
        });
      } else if (arr.length > 4) {
        const subset = arr.slice(0, 4);
        const members = subset
          .map((e) => poolStudents.find((s) => s.email === e)!)
          .filter(Boolean);
        if (members.length === 4 && !hasAvoidViolation(members)) {
          for (const m of members) assigned.add(m.email);
          teams.push({
            teamId: `team-${++teamCounter}`,
            instructor: members[0].instructor,
            section: members[0].section,
            members,
            formationType: "preference",
            flags: [],
          });
        }
      } else if (arr.length >= 1 && arr.length < 4) {
        for (const m of seedMembers) assigned.add(m.email);
        const needed = 4 - seedMembers.length;
        const groupEmails = new Set(arr);

        const hangersOn = findHangersOn(groupEmails, poolStudents, rosterEmails)
          .filter((s) => !assigned.has(s.email))
          .filter((c) => !wouldAvoidViolation(c, seedMembers, rosterEmails));

        const others = poolStudents
          .filter((s) => !assigned.has(s.email) && !hangersOn.includes(s))
          .sort((a, b) => {
            const aScore = a.skillScores?.total ?? 4.5;
            const bScore = b.skillScores?.total ?? 4.5;
            return aScore - bScore;
          });

        const toAdd: Student[] = [];
        const seedHasConstrained = seedMembers.some((s) => s.isScheduleConstrained);
        const candidates = [...hangersOn, ...others];

        const hasUnassignedMutualPartner = (email: string): boolean => {
          if (!preferMutualPairs) return false;
          const partners = mutual.get(email);
          if (!partners?.size) return false;
          const groupEmails = new Set([...arr, ...toAdd.map((x) => x.email)]);
          for (const p of partners) {
            if (!assigned.has(p) && !groupEmails.has(p)) return true;
          }
          return false;
        };

        for (const c of candidates) {
          if (toAdd.length >= needed) break;
          if (assigned.has(c.email)) continue;
          if (hasUnassignedMutualPartner(c.email)) continue;
          if (wouldAvoidViolation(c, [...seedMembers, ...toAdd], rosterEmails)) continue;
          const canAdd =
            !c.isScheduleConstrained ||
            !seedHasConstrained ||
            [...seedMembers, ...toAdd].some((s) => {
              const sa = s.surveyData?.availabilitySlots || [];
              const ca = c.surveyData?.availabilitySlots || [];
              return sa.some((x) => ca.includes(x));
            });
          if (canAdd) {
            toAdd.push(c);
            assigned.add(c.email);
          }
        }

        const allMembers = [...seedMembers, ...toAdd];
        const flags: string[] = [];
        if (hasAvoidViolation(allMembers)) flags.push("avoid_violation");
        if (hasScheduleConcern(allMembers)) flags.push("schedule_concern");
        if (allMembers.length < 4) flags.push("incomplete");

        teams.push({
          teamId: `team-${++teamCounter}`,
          instructor: allMembers[0].instructor,
          section: allMembers[0].section,
          members: allMembers,
          formationType: "preference",
          flags,
        });
      }
    }

    const unassigned = poolStudents.filter((s) => !assigned.has(s.email));
    const withSurvey = unassigned.filter((s) => s.surveyData).sort((a, b) => {
      const aScore = a.skillScores?.total ?? 4.5;
      const bScore = b.skillScores?.total ?? 4.5;
      return aScore - bScore;
    });
    const withoutSurvey = unassigned.filter((s) => !s.surveyData);

    // Assign in order: no-survey first, then low-skill. Remainder (team of 3) = high-skill survey respondents.
    const assignmentOrder = [...withoutSurvey, ...withSurvey];

    const getTargetTeamSize = (n: number): number => {
      if (n < 3) return n;
      if (remainderStrategy === "prefer-3") {
        const remainderIf4 = n - 4;
        if (remainderIf4 >= 0 && (remainderIf4 === 1 || remainderIf4 === 2)) return 3;
        return n >= 4 ? 4 : 3;
      }
      if (remainderStrategy === "allow-5") {
        return n >= 5 ? 5 : n >= 4 ? 4 : n;
      }
      return n >= 4 ? 4 : n;
    };

    while (true) {
      const available = assignmentOrder.filter((s) => !assigned.has(s.email));
      const targetSize = getTargetTeamSize(available.length);
      if (targetSize < 3 && available.length > 0) break;
      if (available.length < 3) break;

      const teamMembers: Student[] = [];
      for (const s of available) {
        if (teamMembers.length >= targetSize) break;
        if (wouldAvoidViolation(s, teamMembers, rosterEmails)) continue;
        teamMembers.push(s);
        assigned.add(s.email);
      }

      if (teamMembers.length === 0) break;

      const flags: string[] = [];
      if (hasAvoidViolation(teamMembers)) flags.push("avoid_violation");
      if (hasScheduleConcern(teamMembers)) flags.push("schedule_concern");
      if (teamMembers.length < 4) flags.push("incomplete");

      teams.push({
        teamId: `team-${++teamCounter}`,
        instructor: teamMembers[0].instructor,
        section: teamMembers[0].section,
        members: teamMembers,
        formationType: "algorithm",
        flags,
      });
    }

    const remainder = poolStudents.filter((s) => !assigned.has(s.email));
    if (remainder.length >= 1) {
      const flags: string[] = ["incomplete"];
      if (hasAvoidViolation(remainder)) flags.push("avoid_violation");
      if (hasScheduleConcern(remainder)) flags.push("schedule_concern");
      teams.push({
        teamId: `team-${++teamCounter}`,
        instructor: remainder[0].instructor,
        section: remainder[0].section,
        members: remainder,
        formationType: "algorithm",
        flags,
      });
    }
  }

  const dedupedUnmatched = Array.from(
    new Map(unmatched.map((u) => [`${u.email}-${u.category}-${u.referencedBy || ""}`, u])).values()
  );

  const emailToTeam = new Map<string, Team>();
  for (const t of teams) {
    for (const m of t.members) {
      if (emailToTeam.has(m.email) && emailToTeam.get(m.email)!.teamId !== t.teamId) {
        throw new Error(`Duplicate assignment: ${m.email} appears in both ${emailToTeam.get(m.email)!.teamId} and ${t.teamId}`);
      }
      emailToTeam.set(m.email, t);
    }
  }

  const byEmail = new Map<string, Student>();
  for (const s of students) byEmail.set(s.email, s);

  const mutual = buildMutualPreferences(students);
  const unmatchedPairs: UnmatchedPreferencePair[] = [];
  const seenPairs = new Set<string>();

  for (const [emailA, prefSet] of mutual) {
    const teamA = emailToTeam.get(emailA);
    const studentA = byEmail.get(emailA);
    if (!studentA) continue;
    for (const emailB of prefSet) {
      const key = [emailA, emailB].sort().join("|");
      if (seenPairs.has(key)) continue;
      seenPairs.add(key);
      const teamB = emailToTeam.get(emailB);
      const studentB = byEmail.get(emailB);
      if (!studentB) continue;
      if (teamA && teamB && teamA.teamId !== teamB.teamId) {
        const poolA = getTeamingPool(studentA.instructor, studentA.section);
        const poolB = getTeamingPool(studentB.instructor, studentB.section);
        if (poolA === poolB) {
          unmatchedPairs.push({
            studentA: emailA,
            studentB: emailB,
            nameA: studentA.name,
            nameB: studentB.name,
          });
        }
      }
    }
  }

  return {
    teams,
    unmatchedStudents: dedupedUnmatched,
    unmatchedPreferencePairs: unmatchedPairs,
  };
}
