/**
 * Types for the team formation script.
 */

export type Instructor = "Bell" | "Shesh" | "Spertus" | "Vesely";

/** When can't make groups of 4: prefer groups of 3, or allow groups of 5 */
export type RemainderStrategy = "prefer-3" | "allow-5";

export type UnmatchedCategory = "survey_respondent" | "preferred_teammate" | "avoid_list";

export interface UnmatchedStudent {
  email: string;
  name?: string;
  category: UnmatchedCategory;
  referencedBy?: string;
  originalText?: string;
}

export interface RosterRow {
  name: string;
  email: string;
  class_section_name: string;
  lab_section_name: string;
  private_profile_id: string;
  public_profile_id: string;
}

export interface SurveyRow {
  Timestamp: string;
  "Full name": string;
  "Northeastern Email": string;
  "Class Section": string;
  "Preferred teammates": string;
  "Students to avoid": string;
  "Java Experience Prior to CS 3100": string;
  "GUI/Desktop Application Experience Prior to CS 3100": string;
  "Git Collaboration Experience Prior to CS 3100": string;
  "When will you generally be available for team meetings? (Check all that apply)": string;
  "When are your best days for team meetings? (Check all that apply)": string;
}

export interface SkillScores {
  java: number;
  gui: number;
  git: number;
  total: number;
}

export interface Student {
  name: string;
  email: string;
  instructor: Instructor;
  section: string;
  labSection: string;
  surveyData?: {
    preferredTeammates: string[];
    studentsToAvoid: string[];
    javaExperience: string;
    guiExperience: string;
    gitExperience: string;
    availabilitySlots: string[];
    bestDays: string[];
  };
  skillScores?: SkillScores;
  isScheduleConstrained: boolean;
}

export interface Team {
  teamId: string;
  instructor: Instructor;
  section: string;
  members: Student[];
  formationType: "preference" | "algorithm";
  flags: string[];
}

export interface FormTeamsConfig {
  rosterPath: string;
  surveyPath: string;
  outputPath: string;
  unmatchedPath: string;
  instructor: Instructor | "all";
  remainderStrategy?: RemainderStrategy;
}

export interface UnmatchedPreferencePair {
  studentA: string;
  studentB: string;
  nameA: string;
  nameB: string;
}

export interface FormTeamsResult {
  teams: Team[];
  unmatchedStudents: UnmatchedStudent[];
  unmatchedPreferencePairs: UnmatchedPreferencePair[];
  stats: {
    totalStudents: number;
    studentsWithSurvey: number;
    studentsWithoutSurvey: number;
    teamsByPreference: number;
    teamsByAlgorithm: number;
    teamsWithScheduleConcern: number;
    teamsWithAvoidViolation: number;
    incompleteTeams: number;
  };
}
