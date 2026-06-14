---
sidebar_position: 5
image: /img/labs/web/lab5.png
---



In this lab, you'll experience firsthand why requirements analysis matters. You and a partner will interpret an intentionally ambiguous project brief, then discover how dramatically your interpretation differs from another pair's—even though you read the exact same words. This "parallel universe" exercise demonstrates the critical importance of building shared understanding before writing code.

:::info Grading: What You Need to Submit

**Option 1: Complete entire lab**

- Complete Parts 1-5 of the lab
- Complete the reflection in `REFLECTION.md`
- Push your completed work to GitHub
- You may leave the lab after confirming with a TA that you're done

**Option 2: Complete what you are able and ask for help**
If you're unable to complete everything:

- Submit a `REFLECTION.md` documenting what you completed, where you got stuck, and what you tried
- A TA will review your submission and award credit for your good-faith effort

:::

# 1 Getting Started

Please identify a partner to complete this lab. **Important:** During Parts 1 and 2, do not communicate with other pairs—this is essential for the exercise.

**Soft Skill Focus: Building Shared Understanding**

During pair work, practice these skills:

- Explain your interpretation *and the reasoning behind it*
- Listen to understand (not to argue)
- Identify where your interpretations differ
- Create a merged understanding that incorporates both perspectives

**Step 1:** Introduce yourself to your partner and record their name in `REFLECTION.md`.

# 2 Learning Objectives

By the end of this lab, you will be able to:

- Experience how the same requirements text can lead to dramatically different interpretations
- Identify ambiguous terms and hidden assumptions in requirements documents
- Apply the three risk dimensions (understanding, scope, volatility) to analyze requirements divergence
- Practice building shared understanding through structured negotiation
- Develop questions that would clarify ambiguous requirements

# 3 The Scenario: Office Hours System

You have been hired to build a system for the CS department. Here's the brief you received:

:::note Project Brief

**OFFICE HOURS SYSTEM**

The CS department needs a system to help students get help from TAs.

Key points:

- Students can request help with course material
- TAs provide assistance during their scheduled hours
- Some office hours are in-person, some are virtual
- The system should support both live help and leaving questions for later
- Students should know when they can expect a response
- TAs need to manage their workload fairly

Build something that works for a course with 300 students and 10 TAs across three campuses in different time zones.

:::

That's it. That's all you get.

Your job in this lab is to turn this vague brief into a concrete specification—and then discover what happens when different people interpret the same brief differently.

---

## 3.1 Part 1: Individual Interpretation (15 minutes)

**Work alone for this part.** Do not discuss with your partner yet.

Read the project brief carefully. Then, working independently, complete the following exercises in your `REFLECTION.md`.

### 3.1.1  Exercise 1.1: Your Requirements

List **5-7 specific requirements** you believe the system needs. For each requirement:

- State it clearly enough that another engineer could implement it
- Note any assumptions you're making
- Identify which stakeholder (student, TA, instructor, department) it primarily serves

**Format:**
> **Requirement:** [A specific, testable requirement]
> **Assumption:** [What you assumed about the brief to arrive at this requirement]
> **Stakeholder:** [Who benefits and why]

### 3.2.2 Exercise 1.2: Ambiguity Identification

List **3 or more terms or phrases** from the brief that you found unclear or ambiguous. For each:

- Quote the exact phrase
- Explain why it's ambiguous
- State what you *assumed* it means for your requirements above

**Format:**
> **Phrase:** [Quote the exact words from the brief]
> **Why ambiguous:** [What different interpretations are possible?]
> **My assumption:** [Which interpretation you chose for your requirements]

**Write your answers in the "Part 1: Individual Interpretation" section of `REFLECTION.md` before proceeding.**

---

## 3.2 Part 2: Pair Negotiation (20 minutes)

**Now work with your partner. Still no communication with other pairs!**

### 3.2.1 Exercise 2.1: Share Interpretations (10 minutes)

Take turns sharing your individual interpretations from Part 1:

- Read your requirements aloud to your partner
- Discuss: Where do you agree? Where do you disagree?
- Identify: What assumptions did each of you make?

**Pay attention to moments where you made different assumptions about the same phrase.** These are the most interesting findings.

### 3.2.2 Exercise 2.2: Joint Specification (10 minutes)

Together, create a **joint specification of exactly 8 requirements**:

- Each requirement must be specific enough that a developer could test whether it's been implemented correctly
- Both partners must agree on the exact wording
- Document any assumptions you're both making

**Write your joint specification in the "Part 2: Pair Specification" section of `REFLECTION.md`.**

The goal is consensus—you should both be able to defend every requirement as the "right" interpretation of the brief.

---

:::note Sync Point
**Wait here** until your TA signals to proceed to Part 3.
:::

## 3.3 Part 3: The Reveal (20 minutes)

**Now pairs combine into quads. This is where it gets interesting.**

### 3.3.1 Exercise 3.1: Specification Comparison (10 minutes)

**Do NOT debate yet—just observe.**

1. Pair AB reads their 8 requirements aloud, one at a time
2. Pair CD reads their 8 requirements aloud, one at a time
3. As you listen, note every difference you hear—big or small

You'll likely discover that despite reading the **exact same brief**, your specifications describe **different systems**.

### 3.3.2 Exercise 3.2: Divergence Catalog (10 minutes)

As a quad, create a table documenting **every significant difference** between the two specifications:

| Topic | Pair AB's Interpretation | Pair CD's Interpretation | Impact if Built Wrong |
|-------|-------------------------|-------------------------|----------------------|
| ... | ... | ... | ... |

Aim for **at least 4 divergences**. You'll probably find more.

**Record your divergence table in the "Part 3-4: The Reveal" section of `REFLECTION.md`.**

---

## 3.4 Part 4: Root Cause Analysis (15 minutes)

### 3.4.1 Exercise 4.1: Apply the Risk Framework (10 minutes)

For your **top 3 divergences**, classify each by the risk dimension from the requirements lecture (Understanding, Scope and Volatility):

| Divergence | Risk Type | Why This Classification? |
|------------|-----------|-------------------------|
| [Your divergence 1] | **Understanding** / **Scope** / **Volatility** | [Your explanation] |
| [Your divergence 2] | ... | ... |
| [Your divergence 3] | ... | ... |

For each, explain:

- Why does this divergence fall into this risk category?
- What would happen if you built one interpretation and the client wanted the other?

### 3.4.2 Exercise 4.2: What Would Have Helped? (5 minutes)

For each of your top 3 divergences, identify which **elicitation technique** from the requirements lecture could have prevented it:

| Divergence | Elicitation Technique | Specific Action |
|------------|----------------------|-----------------|
| [Your divergence 1] | Interview / Observation / Prototype / etc. | [What specifically would you do?] |
| [Your divergence 2] | ... | ... |
| [Your divergence 3] | ... | ... |

**Record your analysis in `REFLECTION.md`.**

---

:::note Sync Point
**Wait here** for a brief class discussion before proceeding to Part 5.
:::

## 3.5 Part 5: Reflection and Insights (10 minutes)

### 3.5.1 Exercise 5.1: User Perspective

You're not just engineers—you're also potential *users* of an office hours system. As a quad, discuss:

- Which interpretation from either pair would you actually *want* as a student?
- Did the "engineer" interpretation match what the "user" would want?
- What requirements did neither pair think of that you'd want as a user?

### 3.5.2 Exercise 5.2: Questions for the Client

If you could ask the CS department **3 questions** before building this system, what would they be?

- Focus on questions that would resolve your biggest divergences
- Frame questions to get useful answers (avoid yes/no questions)

**Record your insights and questions in `REFLECTION.md`.**

---

# 4 Reflection

Your `REFLECTION.md` should include all of the following sections. Make sure you've completed each one before submitting:

### Partner Information

- **Your Pair Partner:** [Name]
- **Your Quad Partners:** [Names from the other pair]

### Part 1: Individual Interpretation

- Your 5-7 initial requirements (with assumptions and stakeholders)
- Your 3+ identified ambiguities (with your assumptions)

### Part 2: Pair Specification

- Your joint 8 requirements
- Assumptions you both made

### Part 3-4: The Reveal

- Divergence table (at least 4 rows)
- Risk classification table (top 3 divergences)
- "What would have helped" table

### Part 5: Reflection and Insights

- User perspective discussion (engineer vs. user interpretations)
- 3 questions for the client

### Meta Reflection

Answer these questions thoughtfully:

1. **Most Surprising Divergence:** What difference between the pairs surprised you most? Why didn't you anticipate it?

2. **Engineer vs. User:** Did your "engineer" interpretation match what you'd actually want as a user of this system? What does that tell you about requirements gathering?

3. **Future Behavior:** What will you do differently when reading requirements for your next assignment or project?

---

# 5 Submission Checklist

Before your final submission, ensure:

- [ ] Part 1: You completed your individual interpretation (5-7 requirements, 3+ ambiguities)
- [ ] Part 2: You and your partner created a joint specification of exactly 8 requirements
- [ ] Part 3: Your quad cataloged at least 4 divergences between the pair specifications
- [ ] Part 4: You classified your top 3 divergences by risk type and identified elicitation techniques
- [ ] Part 5: Your quad discussed user perspective and identified 3 questions for the client
- [ ] `REFLECTION.md` is complete with all sections filled in
- [ ] All changes are committed and pushed to GitHub
