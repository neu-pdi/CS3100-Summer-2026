/**
 * Example TypeScript Course Configuration
 * 
 * This file demonstrates how to create a type-safe course configuration.
 * Rename to course.config.ts and import in docusaurus.config.ts for type checking.
 */

import type { CourseConfig } from './types';

const config: CourseConfig = {
  courseCode: 'CS 3100',
  courseTitle: 'Software Engineering and Software Development',
  semester: 'Spring 2026',
  academicYear: '2025-2026',
  startDate: '2026-01-12',
  endDate: '2026-04-24',
  timezone: 'America/New_York',
  
  sections: [
    {
      id: '01',
      name: 'Section 01 - MWF Morning',
      crn: '12345',
      timeZone: 'America/New_York',
      meetings: [
        {
          days: ['Monday', 'Wednesday', 'Friday'],
          startTime: '09:50',
          endTime: '10:55',
          location: 'Churchill Hall 103',
        },
      ],
      instructors: ['Jonathan Bell'],
      // Canvas course ID for this section - enables Canvas sync
      canvasCourseId: '123456',
    },
    {
      id: '02',
      name: 'Section 02 - TR Afternoon',
      crn: '12346',
      timeZone: 'America/New_York',
      meetings: [
        {
          days: ['Tuesday', 'Thursday'],
          startTime: '13:35',
          endTime: '15:15',
          location: 'Snell Library 035',
        },
      ],
      instructors: ['Jonathan Bell'],
      // Canvas course ID for this section - enables Canvas sync
      canvasCourseId: '123457',
    },
  ],
  
  holidays: [
    {
      date: '2026-01-19',
      name: 'Martin Luther King Jr. Day',
      type: 'holiday',
      notes: 'University closed, no classes',
    },
    {
      date: '2026-02-16',
      name: "Presidents' Day",
      type: 'holiday',
    },
    {
      date: '2026-03-02',
      endDate: '2026-03-06',
      name: 'Spring Break',
      type: 'break',
      notes: 'Enjoy your break!',
    },
    {
      date: '2026-04-17',
      name: "Patriots' Day",
      type: 'holiday',
      notes: 'Boston Marathon',
    },
    {
      date: '2026-04-27',
      endDate: '2026-05-01',
      name: 'Final Exams',
      type: 'exam-period',
    },
  ],
  
  lectures: [
    {
      lectureId: 'l0-summary',
      title: 'Course Overview',
      dates: ['2026-01-12'],
      topics: ['Introduction', 'Syllabus', 'Course Structure'],
      materials: {
        slides: 'https://example.com/slides/l0',
      },
    },
    {
      lectureId: 'l1-intro',
      title: 'Introduction to Software Engineering',
      dates: ['2026-01-14', '2026-01-15'],
      topics: ['Software Engineering Principles', 'Development Lifecycle'],
      materials: {
        slides: 'https://example.com/slides/l1',
        additionalReading: [
          'https://example.com/reading/se-intro',
        ],
      },
    },
    {
      lectureId: 'l2-data-in-jvm',
      title: 'Data Structures and the JVM',
      dates: ['2026-01-16', '2026-01-20', '2026-01-21'],
      topics: ['JVM Architecture', 'Memory Management', 'Data Structures'],
    },
    {
      lectureId: 'l3-more-java-new',
      title: 'Advanced Java Features',
      dates: ['2026-01-22', '2026-01-23', '2026-01-26'],
      topics: ['Generics', 'Collections', 'Streams', 'Lambdas'],
    },
    {
      lectureId: 'l4-specs-contracts',
      title: 'Specifications and Contracts',
      dates: ['2026-01-27', '2026-01-28', '2026-01-29'],
      topics: ['Design by Contract', 'Pre/Post Conditions', 'Invariants'],
    },
    {
      lectureId: 'l10-review1',
      title: 'Exam 1 Review',
      dates: ['2026-02-23', '2026-02-24'],
      topics: ['Review Session'],
    },
    {
      lectureId: 'l11-exam1',
      title: 'Exam 1',
      dates: ['2026-02-25', '2026-02-26'],
      topics: ['Midterm Exam'],
      notes: 'Bring a pencil and calculator',
    },
  ],
  
  assignments: [
    {
      id: 'hw1',
      title: 'Homework 1: Java Warmup',
      type: 'homework',
      assignedDate: '2026-01-14',
      dueDate: '2026-01-21',
      dueTime: '23:59',
      points: 100,
      url: '/assignments/hw1',
      notes: 'Review Java basics before starting',
    },
    {
      id: 'hw2',
      title: 'Homework 2: Design Patterns',
      type: 'homework',
      assignedDate: '2026-01-28',
      dueDate: '2026-02-11',
      dueTime: '23:59',
      points: 100,
      url: '/assignments/hw2',
    },
    {
      id: 'project1',
      title: 'Project 1: Multiplayer Game',
      type: 'project',
      assignedDate: '2026-02-04',
      dueDate: '2026-03-14',
      dueTime: '23:59',
      points: 300,
      url: '/assignments/project1',
      notes: 'Work in teams of 3-4',
    },
    {
      id: 'quiz1',
      title: 'Quiz 1: Java Fundamentals',
      type: 'quiz',
      assignedDate: '2026-01-23',
      dueDate: '2026-01-23',
      dueTime: '10:55',
      points: 50,
      notes: 'In-class quiz',
    },
  ],
  
  // Canvas LMS integration configuration
  // Set CANVAS_API_TOKEN environment variable to enable sync during build
  canvas: {
    // Your Canvas instance URL
    canvasUrl: 'https://canvas.northeastern.edu',
    // Environment variable name for API token (default: CANVAS_API_TOKEN)
    apiTokenEnvVar: 'CANVAS_API_TOKEN',
    // Sync assignments as stubs with links to course website (default: true)
    syncAssignments: true,
    // Sync lectures and labs as modules with external URL items (default: true)
    syncModules: true,
  },
  
  metadata: {
    department: 'Khoury College of Computer Sciences',
    credits: 4,
    prerequisites: ['CS 2510'],
    description: 'Presents a systematic approach to the principles and concepts of software engineering and modern software development techniques. Topics include requirements engineering, software design, implementation, testing, and maintenance; lifecycle models; unified modeling language; design patterns; refactoring; configuration management; and project management.',
    syllabus: 'https://example.com/syllabus.pdf',
    officeHours: [
      {
        instructor: 'Jonathan Bell',
        schedule: 'Tuesdays 2-3pm, Fridays 11am-12pm',
        location: 'ISEC 621',
        bookingUrl: 'https://calendly.com/jbell/office-hours',
      },
      {
        instructor: 'TA: Jane Smith',
        schedule: 'Mondays 3-4pm, Wednesdays 4-5pm',
        location: 'ISEC 055',
      },
    ],
  },
};

export default config;

