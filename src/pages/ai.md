---
title: Artificial Intelligence in this Course and Beyond
---

## Software Engineering in an Age of AI

The hardest parts of building software have never been typing code. They are figuring out what a system should actually accomplish, negotiating conflicting stakeholder needs, making architectural tradeoffs that balance competing concerns like performance and maintainability, keeping a codebase healthy as requirements evolve, and coordinating effectively with other people. AI tools can produce syntactically correct code at impressive speed, but none of that addresses the engineering challenges that determine whether software succeeds or fails in the real world.

When AI generates a snippet of code, someone still has to decide whether it solves the right problem, whether it will integrate cleanly with the existing system, whether it handles edge cases appropriately, whether it introduces security vulnerabilities or performance bottlenecks, and whether future developers will be able to understand and modify it. These are all skills that have **always** been important in software engineering, but with the diffusion of AI, these skills have become even more important. This is precisely why our curriculum focuses so heavily on foundational engineering skills:

- **Design for change** : Understanding coupling, cohesion, and information hiding—the principles that determine whether code can evolve gracefully or becomes brittle
- **Requirements and stakeholder analysis** : Learning to discover what people actually need, navigate conflicting interests, and recognize hidden assumptions
- **Testing and validation** : Developing the judgment to know what to test and why, not just how to write test syntax
- **Teamwork and collaboration** : Practicing code review, documentation, and communication—skills that become more important, not less, as code generation accelerates
- **Architecture and quality attributes** : Reasoning about tradeoffs among testability, performance, scalability, security, and maintainability
- **Sustainability** : Understanding the long-term impacts of design decisions on the environment, economy, and society

When code can be produced faster, the bottleneck shifts to integration, validation, and maintenance. Evaluating whether generated code is correct, secure, performant, and aligned with your design goals requires deep understanding of what good code looks like—understanding that only comes from practice. Leveraging these insights, we introduce AI coding assistants mid-way through the course, providing you with the ability to quickly generate larger codebases, forcing you to face the challenges of integration, validation, and maintenance over the course of a single semester.

## Why We Restrict AI Early in the Course

AI coding assistants like Cursor, Windsurf, and Copilot are not permitted for the early assignments in this course. This restriction exists because **we have not yet taught you to effectively review the code you could not have written yourself**. Using AI assistance before developing foundational competence means accepting whatever the model produces without the ability to recognize errors, inefficiencies, or subtle misalignments with your actual requirements. The result is not learning with assistance—it is outsourcing the learning entirely.

Feeding assignment instructions to a model and receiving code or test cases in return bypasses the thinking that produces learning. "Only looking" at AI-generated solutions before writing your own undermines the process just as thoroughly—you end up pattern-matching against the AI's approach rather than developing your own problem-solving ability, and you never build the instincts needed to recognize when an AI solution is subtly wrong. LLMs become genuinely useful once you have the competence to break down a problem precisely, specify what you need, and critically evaluate the output. That competence is what you should have begun developing in CS 2100, and it is what we continue building in this course.

## Our Approach: Competency Development, Not Just Restriction

We do not treat AI as simply "forbidden." Each assignment indicates the expected level of AI usage, ranging from "Not allowed" through "Permitted" to "Required." These designations reflect the learning objectives for that assignment. Some assignments are designed to build foundational skills that require unassisted practice; others introduce AI as a tool to be used thoughtfully.

In the [Introduction to AI agents lecture](/lecture-notes/l13-intro-ai-agents), we cover how AI programming agents work and present a structured workflow for human-AI collaboration: identifying what context the AI needs, crafting effective prompts, evaluating outputs critically against your actual goals, calibrating toward desired outcomes, and documenting decisions. 

Some interaction with AI is unavoidable—search engines now surface AI-generated summaries, and using models to clarify concepts is not necessarily problematic. But when you do use AI for information, you remain responsible for verifying accuracy against authoritative sources: official documentation, course materials, and course staff. Learning to read technical documentation is itself a valuable skill that pays dividends throughout a technical career.

### The Economic Reality

Software has historically exhibited [Jevons' paradox](https://en.wikipedia.org/wiki/Jevons_paradox): when a resource becomes cheaper to produce, total consumption increases rather than decreasing. Every major productivity improvement in software development—high-level languages, structured programming, automated testing, continuous integration—has resulted in more software being built, not fewer people employed to build it. There is no evidence that AI-assisted development will break this pattern. As certain tasks become faster, organizations pursue projects that were previously too expensive, creating new demand.

The skills that remain valuable are the ones AI does not provide: understanding what to build, designing systems that can evolve, validating that implementations meet requirements, and working effectively with other humans. These are skills that we emphasize in this course.

## How Course Staff Use AI

We maintain firsthand experience with these tools so we can guide you effectively. Some course materials were developed with AI assistance, and all such content has been reviewed and edited for accuracy. Examples include:

- Expanding learning objectives into draft lecture notes
- Drafting project requirements, instructions, solutions, test cases, and initial rubrics
- Developing Pawtograder, the course operations platform
- Creating visual assets like the OctoPaws logo and all of the pixel art images used in the course content
- Drafting this very policy document, synthesizing prior writings, emails, and notes that we have exchanged with each other

Using AI for these tasks allows us to focus on work that cannot be delegated: deciding what concepts to teach and in what sequence, designing assignments that build skills progressively, and providing feedback tailored to individual students. Every piece of AI-assisted content goes through the same critical review process we ask you to develop. 

