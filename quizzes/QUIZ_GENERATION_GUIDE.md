# Quiz Generation Guide for CS3100

This document instructs agents on how to generate quizzes for CS3100 (Program Design and Implementation 2). It captures the principles behind quiz1.md and the lecture materials, focusing on the **kinds** of questions we generate and **why**.

## Overview

- **Format**: Multiple choice, 4 options (a-d), single best answer
- **Length**: ~17 questions for a 65-minute exam
- **Weight**: All questions are equal weight
- **Coverage**: Proportional across covered lectures (roughly 2-4 questions per lecture)
- **Closed-book**: No notes, books, or electronic devices

## Question Taxonomy

Every question on the quiz should fall into one of the following categories. A well-balanced quiz uses a MIX of these types, not just one.

### 1. Code Tracing ("What does this print?")

Present a short Java code snippet (5-15 lines) and ask the student to predict the output or runtime behavior. These test whether students can **mentally execute** code and understand Java's runtime semantics.

**What makes a good code tracing question:**
- Tests a SPECIFIC concept (reference semantics, dynamic dispatch, autoboxing, hashCode/equals behavior)
- The code must be short enough to trace in ~3 minutes
- The correct answer requires understanding a subtle mechanism; a naive reading leads to a wrong answer
- Distractors represent common misconceptions

**Examples from quiz1:**
- Q1 (reference semantics): Reassigning a parameter inside a method does NOT affect the caller. Students who think Java is pass-by-reference pick (a).
- Q8 (autoboxing): `Integer boxed = primitive; boxed.equals(42)` — tests whether students know autoboxing works and `.equals()` compares values.
- Q10 (Set + equals/hashCode): Adding two objects with the same logical identity to a HashSet — tests understanding of how equals/hashCode interact with Set.
- Q16 (fragile base class / double-counting): A subclass overrides both `notifyUser` and `notifyGroup`, but the superclass's `notifyGroup` calls `notifyUser` internally. This is the HARDEST type — it requires tracing through TWO classes with dynamic dispatch.

**Construction recipe:**
1. Identify a concept with a common misconception
2. Write minimal code that exposes the misconception
3. Make the "naive" answer one of the distractors
4. Ensure the code compiles (unless "compilation error" IS the answer)
5. Use the course's domain types (Quantity, Ingredient, DimmableLight, etc.) where possible

### 2. Design Rationale ("Why is it done this way?")

Present an existing design decision from the course codebase or lectures and ask **why** it was made that way. These test whether students understand the principles behind the code, not just the code itself.

**Examples from quiz1:**
- Q2: Why does `MeasuredIngredient` store `Quantity` as a reference type rather than a primitive double? (Answer: polymorphism — it can hold ExactQuantity, FractionalQuantity, or RangeQuantity)
- Q15: A subclass relies on superclass implementation details. What is the risk? (Answer: fragile base class problem)

**Construction recipe:**
1. Find a design decision in the assignments or lectures that embodies a specific principle
2. Frame it as "Why does X do Y?" or "What is the risk of X?"
3. The correct answer names the PRINCIPLE (polymorphism, encapsulation, fragile base class, etc.)
4. Distractors include technically-sounding but wrong reasons (performance, compiler requirements, etc.)

### 3. Concept Application ("What would you change/use?")

Present a scenario and ask the student to choose the correct approach, data structure, or modification. Tests the ability to APPLY knowledge to a new situation.

**Examples from quiz1:**
- Q3: What would we change to make ExactQuantity a subclass of FractionalQuantity? (Tests understanding of `extends` vs `implements` vs multiple inheritance)
- Q6: How to store both MeasuredIngredient and VagueIngredient in one collection? (Tests generics + inheritance: `List<Ingredient>`)

**Construction recipe:**
1. Start with a real design from the course
2. Propose a hypothetical change or new requirement
3. Ask which modification achieves the goal
4. Distractors should be syntactically plausible but semantically wrong (e.g., multiple class inheritance, raw types)

### 4. Mechanism ("How does this work?")

Ask about a Java runtime mechanism or language feature. Tests whether students understand how the JVM or type system behaves.

**Examples from quiz1:**
- Q4 (dynamic dispatch): Given a class hierarchy with overridden toString(), which implementation is called? (Answer: the actual object's, not the declared type's)
- Q7 (List vs Set): What is the primary difference? (Tests understanding of collection semantics)

**Construction recipe:**
1. Identify a mechanism covered in lecture (dynamic dispatch, generics, autoboxing, etc.)
2. Present a scenario where the mechanism determines the outcome
3. Include a class diagram (Mermaid) if the hierarchy matters
4. Distractors represent alternative mechanisms or common confusions

### 5. Best Practice / Terminology ("Which is correct?")

Ask students to identify the correct definition, appropriate usage, or best practice for a concept. These are the most "recall-like" questions but should still require understanding, not pure memorization.

**Examples from quiz1:**
- Q5: Which exception for a precondition violation? (IllegalArgumentException)
- Q9: What does `@Nullable` indicate? (The parameter may be null)
- Q11: What does Comparable enable? (Natural ordering for sorting)
- Q12: When is a named method preferable to a lambda? (Complex/multi-line logic)
- Q13: Pattern matching for instanceof — which statement is correct?
- Q14: Open/Closed Principle definition

**Construction recipe:**
1. Identify a concept, pattern, or best practice from the lectures
2. State it precisely in the stem
3. The correct answer captures the core definition or guideline
4. Distractors invert, overstate, or confuse the concept with a related one
5. Avoid pure trivia — the question should test understanding of WHY the practice exists

### 6. Comparative Design ("What is the advantage?")

Present two concrete implementations side-by-side OR two named architectural approaches, and ask students to evaluate the trade-off or advantage of one over the other. These are the highest-level questions.

This type has two sub-forms:

**6a. Side-by-side code comparison:** Show two implementations and ask about a specific advantage for a specific change.

**Examples from quiz1:**
- Q17: Strategy pattern (Design B) vs if/else chain (Design A) for processing submissions in different languages. What is the advantage when adding TypeScript? (Answer: Design B requires only a new class; Design A requires modifying existing code — Open/Closed Principle)

**6b. Conceptual tradeoff:** Name two architectural approaches (e.g., monolith vs microservices, technical vs domain partitioning) and ask which has an advantage for a specific quality attribute or scenario. No code required — tests whether students understand the tradeoffs at a conceptual level.

**Examples:**
- "Which is an advantage of well-designed microservices over a monolith?" (Answer: better scalability — not simplicity, not easier debugging, not better latency)
- "Can an architectural choice improve one quality attribute and worsen another?" (Answer: yes, and we need to know which attributes are most important for this context)

**Construction recipe:**
1. For 6a: Write two implementations, one using a design principle/pattern and one not. For 6b: Name two approaches covered in lecture.
2. Propose a specific change, scenario, or quality attribute to evaluate against
3. Ask what advantage the better design has FOR THAT SPECIFIC CONTEXT
4. The correct answer should reference a concrete benefit (no modification needed, fewer classes affected, better scalability, etc.)
5. Distractors claim false advantages (performance, memory, compiler requirements) or name real advantages of the *wrong* approach

### 7. Code Quality Analysis ("Which version has better quality X?")

Present two short code snippets that implement the same behavior but with different structural choices, and ask students to evaluate a specific quality property (testability, observability, controllability). Unlike Code Tracing, students don't mentally execute the code. Unlike Comparative Design, they're not evaluating extensibility — they're analyzing structural properties.

**Examples:**
- Two versions of `checkDevice()`: Version A calls `repo.save()` internally (side effect); Version B returns a `HealthReport` (pure). Ask: which is more observable? (Answer: Version B, because the caller can inspect the return value)
- Two versions of `calculateTax()`: Version A calls `TaxService.getInstance()` (hidden dependency); Version B accepts `TaxService` as a parameter. Ask: which is more controllable? (Answer: Version B, because the test can inject any `TaxService`)

**Construction recipe:**
1. Write two versions of the same method with ONE structural difference (return vs side-effect, injected vs looked-up dependency, pure vs stateful)
2. Ask which version has more of a specific, named quality property
3. The correct answer requires understanding what the quality property means in terms of code structure
4. Distractors confuse the properties (e.g., claim the less observable version is more observable) or claim both are equivalent

### 8. Practical Judgment ("What's the best approach?")

Present a realistic development scenario with a specific real-world constraint and ask the student to choose the most appropriate action. Unlike Concept Application, there's no hypothetical design change — it tests the kind of judgment an experienced developer exercises daily.

**Examples:**
- "A developer is testing a method that sends an email when an order is placed. What is the best approach?" (Answer: use a test double for the email service so tests are fast and don't send real emails)
- "A method calls a remote payment API. Why use a test double instead of the real API?" (Answer: calling the real API in tests could trigger actual charges)
- "A developer adds a 5-second timeout and falls back to cached data when an external API is slow. This applies which concept?" (Answer: graceful degradation)

**Construction recipe:**
1. Describe a realistic development scenario with a specific constraint (cost, speed, reliability, side effects)
2. Present 4 approaches, only one of which appropriately addresses the constraint
3. Distractors represent over-engineering, under-engineering, or misunderstanding the constraint
4. The answer should be what an experienced developer would actually do — not a textbook definition

## Distractor Design Principles

Good distractors are CRITICAL. Each wrong answer should be wrong for a specific, identifiable reason:

| Distractor Type | Description | Example |
|---|---|---|
| **Common misconception** | What a student who misunderstands the concept would pick | Q1(a): thinking parameter reassignment affects caller |
| **Partially correct** | True in a related context but wrong here | Q3(a): multiple inheritance syntax (not valid Java) |
| **Superficially plausible** | Sounds technical but is fabricated | Q7(b): "Set maintains insertion order" (it doesn't) |
| **Overgeneralization** | Extends a true statement too far | Q2(d): "Java requires all fields to be objects" |
| **Compilation/runtime confusion** | Confuses compile-time and runtime behavior | Q4(d): "Compilation error because Quantity is abstract" |

**Rules for distractors:**
- Never include a distractor that is arguably also correct
- Never include "All of the above" or "None of the above"
- If "Compilation error" is a distractor, the code MUST actually compile (unless it's the answer)
- Distractors should be roughly the same length as the correct answer

## Grounding in Course Material

### Use Course Domain Examples

Questions should use types and scenarios from the course's own assignments and lectures:
- **CookYourBooks domain** (from assignments): `Quantity`, `ExactQuantity`, `FractionalQuantity`, `RangeQuantity`, `Ingredient`, `MeasuredIngredient`, `VagueIngredient`, `Recipe`
- **IoT domain** (from lectures): `IoTDevice`, `Light`, `DimmableLight`, `TunableWhiteLight`, `SwitchedLight`, `Fan`
- **Pawtograder domain** (from lectures): `Submission`, `Assignment`, `Student`, `BuildStrategy`, `NotificationService`

Using these familiar types reduces extraneous cognitive load and tests understanding of the concepts, not the student's ability to parse unfamiliar code.

### Map Questions to Lecture Learning Objectives

Each lecture has explicit learning objectives (the `##` headings in the lecture notes). Every quiz question should map to at least one learning objective. The answer key must include the lecture number and topic for each question.

### Use Mermaid Diagrams

When a question involves a class hierarchy or design comparison, include a Mermaid `classDiagram` in the question. This matches the lecture format and makes the question clearer. See Q4, Q6, and Q17 in quiz1 for examples.

## Coverage and Balance

### Lecture Distribution

For a quiz covering N lectures, aim for:
- At least 1 question per lecture
- No more than 4 questions per lecture
- More questions on lectures with more substantial content or that introduced more concepts

Example from quiz1 (covering L1-L8):

| Lectures | Questions | Concepts |
|---|---|---|
| L1 (Intro/Java basics) | 2 | Reference semantics, primitives vs references |
| L2 (Inheritance) | 3 | Interfaces, dynamic dispatch, exceptions |
| L3 (Collections) | 3 | Generics, List vs Set, autoboxing |
| L4 (Specifications) | 3 | Nullability, hashCode/equals, Comparable |
| L5 (FP/Readability) | 2 | Lambdas vs named methods, pattern matching |
| L6-7 (Changeability I-II) | 0 | (Tested indirectly through L8) |
| L8 (Changeability III) | 4 | SOLID, fragile base class, composition, Strategy |

Note: L6-L7 concepts (information hiding, coupling, cohesion) are tested indirectly through L8 questions about SOLID and design patterns. Not every lecture needs DIRECT questions if its concepts are naturally tested through later material that builds on it.

### Cognitive Level Distribution

A good quiz has a distribution across difficulty levels:
- **~25% recall/recognition** (Type 5): definitions, terminology, best practices
- **~35% application** (Types 3, 4, 8): applying concepts to new scenarios, understanding mechanisms, practical judgment
- **~25% analysis** (Types 1, 2, 7): tracing code, understanding design rationale, analyzing code quality properties
- **~15% evaluation** (Type 6): comparing designs, evaluating trade-offs (both code-level and conceptual)

### Difficulty Curve

Order questions to build confidence:
- Start with moderately easy questions (not trivially easy — students should feel challenged but not demoralized)
- Place the hardest questions (multi-class code tracing, comparative design) in the second half
- End with a satisfying "capstone" question that integrates multiple concepts

## Answer Key Format

The answer key should be a table at the end of the document:

```markdown
| Q | Answer | Topic |
|---|--------|-------|
| 1 | B | L1: Reference semantics |
| 2 | B | L1: Primitives vs references |
...
```

Followed by a Topic Coverage Summary:

```markdown
| Lecture | Questions | Topics |
|---------|-----------|--------|
| L1 | 1-2 | Reference semantics, primitives vs references |
...
```

## Anti-Patterns to Avoid

1. **Trivial recall**: "What year was Java released?" — not useful
2. **Ambiguous stems**: Questions where two answers are defensibly correct
3. **Trick questions**: Questions designed to confuse rather than test understanding
4. **Pattern-matching answers**: Where students can guess correctly from answer structure alone (e.g., longest answer is always right)
5. **"All of the above"**: Eliminates useful information from wrong answers
6. **Negative stems**: "Which of the following is NOT..." — use sparingly, prefer positive framing
7. **Implementation trivia**: Exact method signatures, parameter orders, or API details that a developer would look up in practice
8. **Tool-specific trivia**: IDE features, debugger button names, menu locations, or tool-specific terminology that a developer would discover by using the tool. Test the underlying concept instead — e.g., don't ask "Which is NOT a type of breakpoint in VS Code?" (memorization); instead ask "When would a conditional breakpoint be more useful than a line breakpoint?" (understanding)
9. **Questions about syntax alone**: "What keyword makes a field non-reassignable?" — test the CONCEPT (immutability, why we use it) not the keyword (`final`)

## Document Format

Use the exact format of quiz1.md:
- Title, topics covered, time limit, format in header
- Instructions section
- Questions numbered with `### Question N`
- Code blocks use ```java with realistic, compilable code
- Mermaid diagrams where hierarchies matter
- Options as `- a)`, `- b)`, `- c)`, `- d)`
- `---` separators between questions
- Answer key and topic coverage summary at the end
