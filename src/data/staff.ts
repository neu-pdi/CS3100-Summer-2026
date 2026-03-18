/**
 * Staff member information for the CS 3100 course
 */

export type StaffRole = 'instructor' | 'academic-coordinator' | 'ta';

export interface StaffMember {
  /** Full name of the staff member */
  name: string;
  /** Pronouns (e.g., "he/him", "she/her", "they/them") - optional */
  pronouns?: string;
  /** Role: instructor, academic-coordinator, or ta */
  role: StaffRole;
  /** Campus location (e.g., "Boston", "Oakland", "Seattle") */
  campus: string;
  /** Brief biography */
  bio: string;
  /** Path to headshot image relative to static/img/staff/ */
  headshot: string;
  /** Email address (for instructors) - optional */
  email?: string;
  /** Homepage URL (for instructors) - optional, makes name a link */
  homepage?: string;
}

export const staffMembers: StaffMember[] = [
  // Instructors
  {
    name: "Rasika Bhalerao",
    pronouns: "",
    role: "instructor",
    campus: "Oakland",
    bio: "",
    headshot: "staff-placeholder.svg",
    email: "r.bhalerao@northeastern.edu"
  },
  {
    name: "Tamara Bonaci",
    pronouns: "",
    role: "instructor",
    campus: "Seattle",
    bio: "",
    headshot: "staff-placeholder.svg",
    email: "t.bonaci@northeastern.edu"
  },
  {
    name: "Lucia Nunez",
    pronouns: "",
    role: "instructor",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg",
    email: "l.nunez@northeastern.edu"
  },
  {
    name: "Amit Shesh",
    pronouns: "he/him",
    role: "instructor",
    campus: "Boston",
    bio: "Teaching Professor, Assistant Dean of Masters Programs",
    headshot: "amit_shesh.jpg",
    email: "a.shesh@northeastern.edu"
  },
  
  // Academic Coordinator
  {
    name: "Tim Howard",
    pronouns: "",
    role: "academic-coordinator",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  
  // Teaching Assistants
  {
    name: "Dhairya Bhatia",
    pronouns: "he/him",
    role: "ta",
    campus: "Boston",
    bio: "MS student in Computer Science.",
    headshot: "dhairya-bhatia.jpeg"
  },
  {
    name: "Lauren Brissette",
    pronouns: "she/her",
    role: "ta",
    campus: "Boston",
    bio: "Third year undergrad Computer Science student with a concentration in AI.",
    headshot: "lbrissette.jpg"
  },
  {
    name: "Edgar Castaneda",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Edward Chan",
    pronouns: "he/him",
    role: "ta",
    campus: "Boston",
    bio: "PlusOne Master's student in CS and a 10th-semester TA supporting students across Khoury's core programming courses.",
    headshot: "echan.jpg"
  },
  {
    name: "Rohan Kumar Chitra",
    pronouns: "he/him",
    role: "ta",
    campus: "Boston",
    bio: "First year Computer Science Graduate Student",
    headshot: "rohan.kumar.jpg"
  },
  {
    name: "Sahil Chute",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Manav Kamleshbhai Dhamani",
    role: "ta",
    campus: "Boston",
    bio: "Second year MS CS student; enjoys astronomy, hiking, and chess.",
    headshot: "manav_dhamani.jpg"
  },
  {
    name: "Amber Friar",
    pronouns: "she/her",
    role: "ta",
    campus: "Boston",
    bio: "Third year studying Computer Science and Economics",
    headshot: "amberfriar.jpg"
  },
  {
    name: "Ran Fukazawa",
    role: "ta",
    campus: "Oakland",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Carmen Gray",
    pronouns: "she/her",
    role: "ta",
    campus: "Boston",
    bio: "Fourth-year environmental engineering major with a minor in computer science who enjoys figure skating, reading, and hiking in her free time.",
    headshot: "carmen-gray.jpg"
  },
  {
    name: "Zainab Imadulla",
    pronouns: "she/her",
    role: "ta",
    campus: "Boston",
    bio: "Third year Computer Science major, concentrating in AI.",
    headshot: "zainab-imadulla.png"
  },
  {
    name: "Pratham Mehta",
    role: "ta",
    campus: "Boston",
    bio: "Computer Science graduate student",
    headshot: "Pratham.jpeg"
  },
  {
    name: "Avery Neuner",
    role: "ta",
    campus: "Boston",
    bio: "Undergraduate student in Computer Science and English with a concentration in AI and natural language processing.",
    headshot: "averyneuner.jpg"
  },
  {
    name: "Shivang Manishkumar Patel",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Peter SantaLucia",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Samyak Bijal Shah",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Ivan Shuvalov",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Sean Snaider",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Advaita Srihari Raghavan",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Samuel Schumacher",
    pronouns: "he/him",
    role: "ta",
    campus: "Boston",
    bio: "Fourth-year CS student with a concentration in software.",
    headshot: "samuel-schumacher.jpg"
  },
  {
    name: "Afrah Fathima",
    pronouns: "she/her",
    role: "ta",
    campus: "Boston",
    bio: "Second-year MS student in Computer Science, specializing in AI and software engineering.",
    headshot: "afrah-fathima.jpg"
  },
  {
    name: "Lucia Sun",
    pronouns: "she/her",
    role: "ta",
    campus: "Oakland",
    bio: "Second year MS student",
    headshot: "lucia-sun.jpg"
  },
  {
    name: "Jessica Teurn",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Prakriti Timalsina",
    role: "ta",
    campus: "Boston",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Abhishek Tuteja",
    role: "ta",
    campus: "Oakland",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
  {
    name: "Aditya Vij",
    role: "ta",
    campus: "Boston",
    bio: "Second year undergrad CS student with a concentration in AI.",
    headshot: "avij.jpg"
  },
  {
    name: "Rebecca Williams",
    role: "ta",
    campus: "Oakland",
    bio: "",
    headshot: "staff-placeholder.svg"
  },
];
