---
title: "Assignment 5: Interactive CLI"
sidebar_position: 6
---


# 1 Overview

In this assignment, you'll build an **interactive command-line interface (CLI)** for CookYourBooks — an instruction-oriented terminal application that lets users manage their recipe library, import recipes, scale ingredients, and generate shopping lists.

The CLI is your first **driving adapter** in the hexagonal architecture — an adapter that *drives* the application by calling into your service layer on behalf of a user (as opposed to *driven* adapters like repositories, which the application calls out to).

:::danger 

Design Quality Is Equally Weighted with Implementation

- **We provide the majority of the test suite.** You can run tests locally to verify functionality.
- **Design documentation is worth 50% of your grade.** Reflection questions are worth 50 points total.
- **Manual grading can deduct up to 30 points** for poor design, architecture, or code quality.

:::

**Prerequisites:** This assignment builds on the A4 sample implementation (provided). You should be familiar with `RecipeRepository`, `RecipeCollectionRepository`, `ConversionRegistry`, and the domain model.


# 2 Learning Objectives

By completing this assignment, you will demonstrate proficiency in:

- **Building a driving adapter** — implementing the CLI as a hexagonal driving adapter (it *drives* the application on behalf of the user) that consumes your services without leaking domain logic into the presentation layer; preparing for a second driving adapter (GUI) in the group project
- **Designing a command architecture** — creating an extensible system for dispatching, parsing, and executing commands
- **End-to-end testing with JLine** — understanding how integration tests use dumb terminal mode to verify CLI behavior
- **Interactive UX for terminals** — building rich interactions including tab completion, and contextual help

---

# 3 Assignment Context and Concepts

## 3.1 Actors: Who Uses CookYourBooks?

CookYourBooks this summer will serve a single actor: a librarian who wants to organize, curate, and transform their recipe collection. This librarian will want to perform the following operations

- import and remove recipes
- create collections
- search collections
- view a particular recipe
- scale recipes and optionally save them

The specific commands you will expose via your CLI are defined [in this command reference](/assignments/Appendices/cyb5-command-reference).

We have provided a modified `RecipeService` facade to cater to this single actor. In this assignment, you will create the CLI driving adapter utilizing this facade.

## 3.2 Data Persistence

The provided `CybLibrary` class handles all data persistence automatically, storing everything in `cyb-library.json` in the current working directory:

- **On startup:** `CybLibrary.load()` loads all collections, recipes, and house conversion rules, or starts with an empty library if the file doesn't exist.
- **On changes:** Every mutation is written to the file immediately. You do not need to call save explicitly.
- **On save failure:** Log the error at `ERROR` level with message `"Failed to save library: {}"` (passing the exception as the final argument), and print: `Warning: Failed to save changes to cyb-library.json: <error message>. Your changes may be lost.`

## 3.3 Application Wiring

The provided `CookYourBooksApp` main class creates the repositories and conversion registry. You are responsible for wiring the service to your CLI and launching the CLI:

```java
public class CookYourBooksApp {
    public static void main(String[] args) {
        Path libraryPath = Path.of("cyb-library.json");
        CybLibrary library = CybLibrary.load(libraryPath);

        RecipeRepository recipeRepo = library.getRecipeRepository();
        RecipeCollectionRepository collRepo = library.getCollectionRepository();
        ConversionRegistry conversionRegistry = library.getConversionRegistry();

        RecipeService service = new RecipeServiceImpl(recipeRepo, collRepo, conversionRegistry);

        CookYourBooksCli cli = new CookYourBooksCli(service);
        cli.run();
    }
}
```

## 3.4 Build and Run

```bash
./gradlew build
java -jar build/libs/cookyourbooks-all.jar
```

The project includes a VS Code launch configuration — select **"Run CookYourBooks CLI (Interactive)"** from the Run and Debug view.

# 4 AI Policy

AI coding assistants are encouraged. Use AI to implement your design — the key learning objectives are architectural thinking, not coding speed.

:::tip 

Using AI as a Thinking Tool for Design

Instead of asking "How should I design my CLI driver?", try visualizing your own ideas first:

> "I'm thinking of having different command objects for the following commands in my CLI that utilize the `RecipeService`: [insert command details here]. Some commands like `collection` and `show` must also enable some type of autocompletion. Generate a Mermaid diagram showing the command objects and their dependency on the RecipeService."

Seeing your ideas as a diagram helps you spot issues. Use AI to externalize your thinking, not replace it.

:::

:::warning 

AI and Design Decisions

AI tools can generate plausible-looking ADRs, but they often miss the nuances of your specific context. If your ADRs read like generic templates without specific references to your code and the L18 heuristics, graders will notice. The architectural thinking is the learning outcome.

:::

Use the "Plan" mode in Copilot or Cursor to generate an implementation plan from your ADRs. Review and refine it, then use "Build" mode to generate code. **Do not use AI to write your reflection.**

:::danger 

AI Resource Consumption — Use "Auto" Mode Only

Do not manually select expensive AI models. Always use **"Auto" mode** in Copilot or Cursor.

:::

---

# 5 Design Task

Before writing any implementation code, plan and document your CLI architecture. By planning and documenting the architecture, your group can decide how to divide work so each member can implement and test without waiting on another. It may be tempting to let one member do the heavy lifting, but this is how teams fail to meet deadlines! That one member needs more time due to the heavy implementation workload and suddenly everyone is waiting on **them** to finish. That is not fair to that member, yourself, and the other teammates. 

**Task**: Plan ahead to avoid this scenario by documenting your answers to the following questions in `GROUP_PLAN.md`:

- For each command to be tested, what commands must already be implemented? (Hint: Read the tests we gave you to validate your answers.)
- Are there any shared interfaces we should design together before implementing separately? What are they and what do they represent?
- What will we do if a shared interface needs to be changed?
- Have we accurately distributed the commands such that everyone has roughly the same amount of work?
- Who will take charge and implement which commands given our answers to the above?

## 5.1 Separation of Concerns

Think of your CLI as three distinct layers. Code for one layer must not mix concerns from another:

- **Application services** coordinate domain operations (scaling, conversion, aggregation, search, persistence) — no formatting or I/O logic
- **Presentation logic** handles command parsing and dispatch — no domain logic like ingredient math or conversion calculations
- **Formatting logic** turns data into displayable output — reusable across commands (the same recipe formatter used by `show`, `cook`, and `scale`)

## 5.2 Command Architecture

Design an extensible command system. Refer to our lecture on the [Command Design Pattern](/lecture-notes/l19-command-design-pattern) as a starting point in your design. What you must *not* do is put the details of all that must be done in one giant `switch` or `if-else` -- that would make this code grow non-linearly over time and become hard to maintain.

## 5.3 Tab Completion Architecture

Tab completion involves distinct concerns:

| Concern | Question | Example |
|---------|----------|---------|
| **What arguments does a command need?** | Which positions expect which types? | `scale` needs a recipe at position 1 and a positive integer at position 2 |
| **What values are available?** | Where do recipe titlescome from? | Recipe titles from services |
| **How to format completions?** | How are candidates presented? | Names with spaces need quotes |

Consider where each concern belongs and document your reasoning in your `REFLECTION.md`.

---

# 6 Implementation Task

Once you have a plan, implement your design. The command reference and full example session are on the [Command Reference page](/assignments/Appendices/cyb5-command-reference).

## 6.1 Command Summary

Below are all the commands in a convenient table. The full reference and details for each commands are on the [Command Reference page](/assignments/Appendices/cyb5-command-reference).

| Category | Command | Description |
|----------|---------|-------------|
| **Library** | [`collections`](/assignments/Appendices/cyb5-command-reference#collections--list-collections) | List all recipe collections |
| | [`collection create <name>`](/assignments/Appendices/cyb5-command-reference#collection-create-name--create-a-personal-collection) | Create a new personal collection |
| | [`recipes <collection>`](/assignments/Appendices/cyb5-command-reference#recipes-collection--list-recipes-in-a-collection) | List recipes in a collection |
| **Recipe** | [`show <recipe>`](/assignments/Appendices/cyb5-command-reference#show-recipe--display-a-recipe) | Display a recipe |
| | [`search <ingredient>`](/assignments/Appendices/cyb5-command-reference#search-ingredient--search-recipes-by-ingredient) | Find recipes containing an ingredient |
| | [`import json <file> <coll>`](/assignments/Appendices/cyb5-command-reference#import-json-file-collection--import-recipe-from-json) | Import recipe from JSON file |
| | [`delete <recipe>`](/assignments/Appendices/cyb5-command-reference#delete-recipe--delete-a-recipe) | Delete a recipe |
| **Tools** | [`scale <recipe> <servings>`](/assignments/Appendices/cyb5-command-reference#scale-recipe-servings--scale-a-recipe) | Scale recipe to target servings |
| **General** | [`help [command]`](/assignments/Appendices/cyb5-command-reference#help--contextual-help) | Show help (or help for a specific command) |
| | [`quit` / `exit`](/assignments/Appendices/cyb5-command-reference#quit--exit--exit-the-application) | Exit the application |

## 6.2 JLine: Rich Terminal Interaction

Your CLI must use [JLine 3](https://github.com/jline/jline3) for terminal interaction. JLine provides:

- **Line editing** — arrow keys, backspace, home/end, etc.
- **Command history** — up/down arrows to recall previous commands
- **Tab completion** — auto-complete command names, collection names, recipe titles
- **Styled output** — colors and formatting for readable output

### 6.2.1 How CLI Input Parsing Works

When a user types a command and presses Enter, JLine gives you the entire line as a `String`. Your CLI must **tokenize** it — splitting into a command name and arguments. The challenge is that spaces separate arguments *and* appear within argument values. Use **quoting** to group words:

```
search "Chicken Thighs"
```

Configure your `LineReader` with a `DefaultParser` for quote-aware tokenization:

```java
DefaultParser parser = new DefaultParser();
LineReader reader = LineReaderBuilder.builder()
    .terminal(terminal)
    .completer(yourCompleter)
    .parser(parser)
    .build();

// Retrieve pre-tokenized arguments from ParsedLine:
String line = reader.readLine("cyb> ");
ParsedLine parsed = reader.getParsedLine();
List<String> words = parsed.words(); // ["search", "Chicken Thighs"]
```

:::tip 

Single-word Arguments

Single-word arguments don't need quotes

`show Pancakes` and `show "Pancakes"` are equivalent. Quotes are only needed when an argument contains spaces.

:::

:::tip 

Paths across operating systems

Windows Users: Backslash in Paths

JLine's `DefaultParser` treats backslash (`\`) as an escape character. On Windows, paths like `C:\Users\recipes\pie.json` get mangled — backslashes are stripped and path segments merge (see [jline/jline3#1238](https://github.com/jline/jline3/issues/1238)). To fix this, use a custom parser that does not treat backslash as an escape:

```java
public class WindowsPathAwareParser extends DefaultParser {
    @Override
    public boolean isEscapeChar(char ch) {
        // Don't treat backslash as an escape character
        return false;
    }
}
```

Then configure your `LineReader` with it:

```java
LineReader reader = LineReaderBuilder.builder()
    .parser(new WindowsPathAwareParser())
    .terminal(terminal)
    .completer(yourCompleter)
    .build();
```

:::

The starter code includes `JLineExample.java` you can run to see basic JLine features. See the [JLine Wiki](https://github.com/jline/jline3/wiki) for full documentation. AI assistants are effective at helping with JLine configuration.

## 6.3 Error Handling

Error messages must be **actionable** — tell the user what went wrong and what they can do about it. Exact error messages for each command are specified in the [Command Reference](/assignments/Appendices/cyb5-command-reference).

### 6.3.1 Ambiguous Match Format

When a user-provided name matches multiple recipes, display the matches with short IDs (first 8 characters of the recipe's internal ID) and prompt the user to be more specific:

```text
Multiple recipes match 'Cookies':
  1. Chocolate Chip Cookies  [ab3fc891]  (Holiday Favorites)
  2. Oatmeal Raisin Cookies  [7c2e04d6]  (Joy of Cooking)
Please specify the full recipe name, or use a short ID (e.g. 'show ab3fc891').
```

The command is **not re-prompted** — the user must re-enter with a more specific name or short ID.

**Recipe lookup order:** If the argument has fewer than 3 characters, match by title only (case-insensitive substring). If 3 or more characters, first try matching as a short ID prefix; if no match, fall back to title matching.

## 6.4 Tab Completion

Your CLI must provide tab completion for:

1. **Command names** — `sc` + Tab suggests `scale`; `col` suggests `collection`, `collections`
2. **Recipe titles and short IDs** — for `show`, `delete`, and `scale`
3. **Collection names** — for `recipes` and the collection argument of `import json`
4. **Conversion rule identifiers** — after `conversion remove`, Tab suggests existing rule identifiers

Use JLine's [`Completer` interface](https://jline.org/docs/tab-completion#custom-completers). A combination of `AggregateCompleter` and `StringsCompleter` may be helpful.

## 6.5 Testing Requirements

**We provide the majority of the test suite.** Run `./gradlew test` locally to verify functionality before submitting. You do not need to write additional tests.

All CLI testing uses **JLine's dumb terminal mode** — no mocks. This tests your CLI as users will actually experience it, with piped input and captured output:

```java
class CookYourBooksCliTest {

    private Terminal terminal;
    private ByteArrayOutputStream output;
    private PipedInputStream pipedIn;
    private PipedOutputStream commandInput;

    @BeforeEach
    void setUp() throws Exception {
        output = new ByteArrayOutputStream();
        pipedIn = new PipedInputStream();
        commandInput = new PipedOutputStream(pipedIn);

        // Create a dumb terminal for testing — no escape sequences, no special handling
        terminal = TerminalBuilder.builder()
            .type(Terminal.TYPE_DUMB)
            .streams(pipedIn, output)
            .build();
    }

    @Test
    void collectionsCommand_listsAllCollections() throws Exception {
        // Arrange: set up test data in repositories
        setupTestCollections();

        // Act: send command to CLI
        sendCommand("collections\n");
        sendCommand("quit\n");
        runCli();

        // Assert: verify output
        String result = output.toString();
        assertThat(result).contains("Holiday Favorites");
        assertThat(result).contains("Joy of Cooking");
    }

    @Test
    void cookMode_navigatesThroughSteps() throws Exception {
        setupRecipeWithSteps("Pancakes", 4);

        sendCommands(
            "cook \"Pancakes\"\n",
            "next\n",
            "next\n",
            "prev\n",
            "quit\n",
            "quit\n"
        );
        runCli();

        String result = output.toString();
        assertThat(result).contains("Step 1 of 4");
        assertThat(result).contains("Step 2 of 4");
        assertThat(result).contains("Step 3 of 4");
        assertThat(result).contains("Step 2 of 4"); // After prev
    }

    private void sendCommand(String command) throws IOException {
        commandInput.write(command.getBytes());
        commandInput.flush();
    }

    private void sendCommands(String... commands) throws IOException {
        for (String cmd : commands) {
            sendCommand(cmd);
        }
    }
}
```

:::info

Why E2E Testing Instead of Mocks?

Unit testing CLIs with mocks often tests that your mock setup is correct, not that your CLI works. Real terminal behavior is hard to mock accurately, and integration bugs slip through because mocked layers never actually talk to each other. E2E tests with a dumb terminal are simpler and catch more bugs.

:::

:::caution

Test Location Matters

The provided tests are in `src/test/java/app/cookyourbooks/cli/`. Do not modify them. If you write additional tests for your own helper classes, put them in a different package.

:::

# 7 Expectation of Group Work

We expect all group members to contribute equitably in the project. We highly recommend using branching, code reviews and pull requests for these assignments. Specifically, we expect:

* Each group member to file at least one pull request (PR) in the Git repo
* Each group member to place at least one comment on a PR that they did not file.

We will be verifying this during grading.


# 8 Reflection

**Do not use AI to write your reflection.** Your answers must be your own.

Update `REFLECTION.md` to address:

## TODO: Replace question 1-4 with something else relevant to commands and CLI. describe and justify specific design decisions etc. 


1. **Handling different data for each operation:** Each operation requires a different set of data obtained from different sources (See [Section 5.3](#53-tab-completion-architecture)). Elaborate on how you handled that in your design.

2. **Components and Wiring:** Your design likely includes several elements: parsing of the CLI instructions, interaction with `RecipeService` and possibly a controller orchestrating everything. Use the specific instruction `search <ingredient>` and provide a point-wise "trace" describing how this input is processed. Be specific: mention class and method names that are called in sequence.

3. **Documenting Design Decisions:** When your group made design decisions about which classes and interfaces to write, what they represent and which methods belong in which class, how were these design decisions documented? Hypothetically if another group continued the project using your implementation, how would they know why you designed things the way you did? Be specific: point to places in your submission where design was documented.

4. **Group Contributions:** For each group member, provide at least two bullet points describing how they contributed to the project. As this is part of the reflection for the entire group, we assume some consensus will be reached within the group about this. In case there are differences, we encourage individual group members to reach out to the instructor directly via email. Such emails will not influence the grade for the assignment, except in extreme cases where a group member simply did not contribute.

5. **E2E Testing Experience:** Compare E2E tests with a dumb terminal to A4's mock-based approach. Which bugs does E2E testing catch that mocks might miss? Were there situations where you wished you had finer-grained unit tests? What's your takeaway about when to use each approach?

6. **AI Collaboration:** Which parts of the CLI did AI help you build most effectively? Where did you need to think independently? Did AI help or hinder your architectural thinking — for example, did it suggest designs that violated the boundary heuristics?

---

# 9 Grading

**Total: 100 points** (50 implementation [38 automated + 12 manual] + 50 design documentation & reflection), minus up to −30 for design quality (floor of 0).

## 9.1 Automated Testing (38 points)

Run `./gradlew test` locally to verify before submitting.

## 9.1.1 Library Commands (38 points)

| Component | Points |
|-----------|--------|
| `help` (list and per-command) | 4 |
| `collections` | 4 |
| `collection create` | 4 |
| `recipes <collection>` | 4 |
| Data persistence (`cyb-library.json` load/save) | 4 |
| `show <recipe>` | 3 |
| `search <ingredient>` | 4 |
| `import json` | 4 |
| `delete <recipe>` | 4 |
| `scale` | 3 |

## 9.2 Manual Demo Tests (12 points)

Run `./gradlew test --tests "*ManualDemoTest"` to generate output files in `build/manual-demo-output/`. Graders review these for formatting and visual layout.

| Test | Output File | Points | Grading Criteria |
|------|-------------|--------|------------------|
| Recipe Display & Transform | `recipe-transform-demo.txt` | 6 | Decorative borders (═══); bullet points (•); scale comparison tables with column headers, arrows (→), and alignment; vague ingredients show "to taste" |
| Library & Shopping List | `library-lists-demo.txt` | 6 | Collections list shows numbered items with [Personal]/[Cookbook]/[Web] badges and recipe counts; recipe listing shows servings; search results include collection names; ambiguous match shows short IDs in brackets and context-appropriate hint|

## 9.3 Manual Grading — Design Quality (up to −30 points)

### 9.3.1 CLI Architecture (up to −10)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| Giant switch/if-else dispatcher | −5 | All commands in one method instead of a principled command architecture |
| Domain logic in CLI layer | −5 | CLI code creates domain objects, does arithmetic, parses ingredients, etc. |
| No separation of formatting | −3 | Output formatting mixed into command logic instead of dedicated formatters/views |
| Copy-paste code across commands | −3 | Same formatting or error handling logic duplicated across commands |

### 9.3.2 Code Quality (up to −5)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| Poor error messages | −2 | Generic errors without actionable guidance |
| Missing Javadoc | −2 | Public classes and methods lack documentation |
| Poor naming/style | −1 | Unclear variable names; inconsistent formatting |


## 9.4 Reflection Questions (20 points)

6 questions × ~3-4 points each. See [Reflection](#8-reflection) for full prompts. Answers should demonstrate genuine reflection on your design process, not just describe what you built.

## 9.5 Evidence of Group Work (10 points)

This part will be graded for each member individually.

* At least one PR per group member: 5 points
* At least one comment on a PR filed by another group member: 5 points

# Submission

```text
├── src/
│   ├── main/java/app/cookyourbooks/...
│   └── test/java/app/cookyourbooks/...  (provided — do not modify)
└── REFLECTION.md
```

Ensure `./gradlew build` and `./gradlew test` succeed before submitting. Submission limit: 15 per rolling 24-hour period.
