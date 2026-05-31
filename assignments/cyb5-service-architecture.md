---
title: "Assignment 5: Interactive CLI"
sidebar_position: 6
---
## Update log
- 3/16/2026: When displaying a recipe with no servings information, use the phrase "No Servings" (applies to `show`, `recipes` listing, `cook` mode header).

---

## Overview

In this assignment, you'll build an **interactive command-line interface (CLI)** for CookYourBooks — a command-oriented terminal application that lets users manage their recipe library, import recipes, scale ingredients, and generate shopping lists.

The CLI is your first **driving adapter** in the [hexagonal architecture](/lecture-notes/l16-testability) — an adapter that *drives* the application by calling into your service layer on behalf of a user (as opposed to *driven* adapters like repositories, which the application calls out to).

:::danger 

Design Quality Is Equally Weighted with Implementation

- **We provide the majority of the test suite.** You can run tests locally to verify functionality.
- **Design documentation is worth 50% of your grade.** Reflection questions are worth 50 points total.
- **Manual grading can deduct up to 30 points** for poor design, architecture, or code quality.

:::

**Due:** Friday, June 12, 2026 at 11:59 PM Boston Time

**Prerequisites:** This assignment builds on the A4 sample implementation (provided). You should be familiar with `RecipeRepository`, `RecipeCollectionRepository`, `ConversionRegistry`, and the domain model.

:::danger 

Start Early — Design Takes Time

Good design requires iteration. You'll make better architectural decisions if you have time to sketch ideas, sleep on them, get feedback in office hours, and refine before implementing.

**Submission limits:** Up to **15 times per rolling 24-hour period.**

:::

---

## Learning Objectives

By completing this assignment, you will demonstrate proficiency in:

- **Building a driving adapter** — implementing the CLI as a hexagonal driving adapter (it *drives* the application on behalf of the user) that consumes your services without leaking domain logic into the presentation layer; preparing for a second driving adapter (GUI) in the group project
- **Designing a command architecture** — creating an extensible system for dispatching, parsing, and executing commands
- **End-to-end testing with JLine** — understanding how integration tests use dumb terminal mode to verify CLI behavior
- **Interactive UX for terminals** — building rich interactions including tab completion, and contextual help

---

## Assignment Context and Concepts

### Actors: Who Uses CookYourBooks?

CookYourBooks this summer will serve a single actor: a librarian who wants to organize, curate, and transform their recipe collection. This librarian will want to perform the following operations

- import and remove recipes
- create collections
- search collections
- view a particular recipe
- scale recipes and optionally save them

The specific commands you will expose via your CLI are defined [in this command reference](/assignments/Appendices/cyb5-command-reference.md).

We have provided a modified `RecipeService` facade to cater to this single actor. In this assignment, you will create the CLI driving adapter utilizing this facade.

### Data Persistence

The provided `CybLibrary` class handles all data persistence automatically, storing everything in `cyb-library.json` in the current working directory:

- **On startup:** `CybLibrary.load()` loads all collections, recipes, and house conversion rules, or starts with an empty library if the file doesn't exist.
- **On changes:** Every mutation is written to the file immediately. You do not need to call save explicitly.
- **On save failure:** Log the error at `ERROR` level with message `"Failed to save library: {}"` (passing the exception as the final argument), and print: `Warning: Failed to save changes to cyb-library.json: <error message>. Your changes may be lost.`

### Application Wiring

The provided `CookYourBooksApp` main class creates the repositories and conversion registry. You are responsible for wiring your own services and launching the CLI:

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

### Build and Run

```bash
./gradlew build
java -jar build/libs/cookyourbooks-all.jar
```

The project includes a VS Code launch configuration — select **"Run CookYourBooks CLI (Interactive)"** from the Run and Debug view.

### AI Policy

AI coding assistants are encouraged. Use AI to implement your design — the key learning objectives are architectural thinking, not coding speed.

:::tip Using AI as a Thinking Tool for Design

Instead of asking "How should I design my CLI driver?", try visualizing your own ideas first:

> "I'm thinking of having different command objects for the following commands in my CLI that utilize the `RecipeService`: [insert command details here]. Some commands like `collection` and `show` must also enable some type of autocompletion. Generate a Mermaid diagram showing the command objects and their dependency on the RecipeService."

Seeing your ideas as a diagram helps you spot issues. Use AI to externalize your thinking, not replace it.

:::

:::warning AI and Design Decisions

AI tools can generate plausible-looking ADRs, but they often miss the nuances of your specific context. If your ADRs read like generic templates without specific references to your code and the L18 heuristics, graders will notice. The architectural thinking is the learning outcome.

:::

Use the "Plan" mode in Copilot or Cursor to generate an implementation plan from your ADRs. Review and refine it, then use "Build" mode to generate code. **Do not use AI to write your reflection.**

:::danger AI Resource Consumption — Use "Auto" Mode Only

Do not manually select expensive AI models. Always use **"Auto" mode** in Copilot or Cursor.

:::

---

## Design Task

Before writing any implementation code, plan and document your CLI architecture. By planning and documenting the architecture, your group can decide
how to divide work so each member can implement and test without waiting on another. It may be tempting to let one member do the heavy lifting, 
but this is how teams fail to meet deadlines! That one member needs more time due to the heavy implementation workload and suddenly everyone 
is waiting on **them** to finish. That is not fair to that member, yourself, and the other teammates. 

**Task**: Plan ahead to avoid this scenario by documenting your answers to the following questions in `GROUP_PLAN.md`:

- For each command to be tested, what commands must already be implemented? (Hint: Read the tests we gave you to validate your answers.)
- Are there any shared interfaces we should design together before implementing separately? What are they and what do they represent?
- What will we do if a shared interface needs to be changed?
- Have we accurately distributed the commands such that everyone has roughly the same amount of work?
- Who will take charge and implement which commands given our answers to the above?

### Separation of Concerns

Think of your CLI as three distinct layers. Code for one layer must not mix concerns from another:

- **Application services** coordinate domain operations (scaling, conversion, aggregation, search, persistence) — no formatting or I/O logic
- **Presentation logic** handles command parsing and dispatch — no domain logic like ingredient math or conversion calculations
- **Formatting logic** turns data into displayable output — reusable across commands (the same recipe formatter used by `show`, `cook`, and `scale`)

### Command Architecture

Design an extensible command system. Refer to our lecture on the [Command Design Pattern]() as a starting point in your design. What you must *not* do is put all commands in one giant `switch` or `if-else` — that's the same anti-pattern as a monolithic service, just at the CLI layer.

### Tab Completion Architecture

Tab completion involves distinct concerns with different rates of change:

| Concern | Question | Example |
|---------|----------|---------|
| **What arguments does a command need?** | Which positions expect which types? | `convert` needs a recipe at position 1 and a unit at position 2 |
| **What values are available?** | Where do recipe titles, unit names come from? | Recipe titles from services; unit names from `Unit` enum |
| **How to format completions?** | How are candidates presented? | Names with spaces need quotes |

Consider where each concern belongs and document your reasoning in your `REFLECTION.md`.

---

## Implementation Task

Once you have a plan, implement your design. The command reference and full example session are on the [Command Reference page](/assignments/Appendices/cyb5-command-reference).

### Command Summary

Below are all the commands in a convenient table. The full reference and details for each commands are on the [Command Reference page](/assignments/Appendices/cyb5-command-reference.md).

| Category | Command | Description |
|----------|---------|-------------|
| **Library** | `collections` | List all recipe collections |
| | `collection create <name>` | Create a new personal collection |
| | `recipes <collection>` | List recipes in a collection |
| **Recipe** | `show <recipe>` | Display a recipe |
| | `search <ingredient>` | Find recipes containing an ingredient |
| | `import json <file> <coll>` | Import recipe from JSON file |
| | `delete <recipe>` | Delete a recipe |
| **Tools** | `scale <recipe> <servings>` | Scale recipe to target servings |
| **General** | `help [command]` | Show help (or help for a specific command) |
| | `quit` / `exit` | Exit the application |

### JLine: Rich Terminal Interaction

Your CLI must use [JLine 3](https://github.com/jline/jline3) for terminal interaction. JLine provides:

- **Line editing** — arrow keys, backspace, home/end, etc.
- **Command history** — up/down arrows to recall previous commands
- **Tab completion** — auto-complete command names, collection names, recipe titles
- **Styled output** — colors and formatting for readable output

#### How CLI Input Parsing Works

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

Single-word arguments don't need quotes

`show Pancakes` and `show "Pancakes"` are equivalent. Quotes are only needed when an argument contains spaces.

:::

:::tip 

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

### Error Handling

Error messages must be **actionable** — tell the user what went wrong and what they can do about it. Exact error messages for each command are specified in the [Command Reference](/assignments/Appendices/cyb5-command-reference).

#### Ambiguous Match Format

When a user-provided name matches multiple recipes, display the matches with short IDs (first 8 characters of the recipe's internal ID) and prompt the user to be more specific:

```text
Multiple recipes match 'Cookies':
  1. Chocolate Chip Cookies  [ab3fc891]  (Holiday Favorites)
  2. Oatmeal Raisin Cookies  [7c2e04d6]  (Joy of Cooking)
Please specify the full recipe name, or use a short ID (e.g. 'show ab3fc891').
```

The command is **not re-prompted** — the user must re-enter with a more specific name or short ID.

**Recipe lookup order:** If the argument has fewer than 3 characters, match by title only (case-insensitive substring). If 3 or more characters, first try matching as a short ID prefix; if no match, fall back to title matching.

### Tab Completion

Your CLI must provide tab completion for:

1. **Command names** — `sc` + Tab suggests `scale`; `col` suggests `collection`, `collections`
2. **Recipe titles and short IDs** — for `show`, `delete`, and `scale`
3. **Collection names** — for `recipes` and the collection argument of `import json`
4. **Conversion rule identifiers** — after `conversion remove`, Tab suggests existing rule identifiers

Use JLine's [`Completer` interface](https://jline.org/docs/tab-completion#custom-completers). A combination of `AggregateCompleter` and `StringsCompleter` may be helpful.

### Testing Requirements

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

---

## Reflection

**Do not use AI to write your reflection.** Your answers must be your own.

Update `REFLECTION.md` to address:

## TODO: Replace question 1-4 with something else relevant to commands and CLI

1. **Applying Boundary Heuristics:** Which of the four L18 heuristics most influenced your service layer design? Give a concrete example: describe a specific boundary you drew (or chose not to draw) and explain which heuristic(s) informed that decision. If multiple heuristics pointed in different directions, how did you resolve the tension?

2. **ADR Writing Experience:** Did documenting your decisions change how you thought about them? Was there a moment where writing the "Consequences" section made you reconsider a choice? How useful do you think ADRs would be on a team project vs. a solo assignment?

3. **Transformation vs. Persistence:** A4's `RecipeService.scaleRecipe()` always saved. Your design needed to support "preview before save." Describe concretely how your service layer handles this differently. What methods exist? How does the CLI compose them? What would break if you tried to bolt this onto A4's interface?

4. **Cook Mode State Management:** Where does cook mode state (current step, original recipe) live in your architecture — in the CLI controller, in a service, in a dedicated session object? What tradeoffs did you consider? Could the same state management approach work for a future "meal planning session" for the Planner actor?

5. **E2E Testing Experience:** Compare E2E tests with a dumb terminal to A4's mock-based approach. Which bugs does E2E testing catch that mocks might miss? Were there situations where you wished you had finer-grained unit tests? What's your takeaway about when to use each approach?

6. **AI Collaboration:** Which parts of the CLI did AI help you build most effectively? Where did you need to think independently? Did AI help or hinder your architectural thinking — for example, did it suggest designs that violated the boundary heuristics?

---

## Grading

**Total: 100 points** (50 implementation [38 automated + 12 manual] + 50 design documentation & reflection), minus up to −30 for design quality (floor of 0).

### Automated Testing (38 points)

Run `./gradlew test` locally to verify before submitting.

#### Library Commands (38 points) (missing 10 points)

| Component | Points |
|-----------|--------|
| `help` (list and per-command) | 3 |
| `collections` | 3 |
| `collection create` | 3 |
| `recipes <collection>` | 3 |
| Data persistence (`cyb-library.json` load/save) | 3 |
| `show <recipe>` | 2 |
| `search <ingredient>` | 3 |
| `import json` | 3 |
| `delete <recipe>` | 3 |
| `scale` | 2 |

### Manual Demo Tests (12 points) (missing 8 points, consider at least one more demo)

Run `./gradlew test --tests "*ManualDemoTest"` to generate output files in `build/manual-demo-output/`. Graders review these for formatting and visual layout.

| Test | Output File | Points | Grading Criteria |
|------|-------------|--------|------------------|
| Recipe Display & Transform | `recipe-transform-demo.txt` | 4 | Decorative borders (═══); bullet points (•); scale/convert comparison tables with column headers, arrows (→), and alignment; vague ingredients show "to taste" |

### Manual Grading — Design Quality (up to −30 points)

#### Service Layer Design (up to −15) (all of this is gone)

#### CLI Architecture (up to −10)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| Giant switch/if-else dispatcher | −5 | All commands in one method instead of a principled command architecture |
| Domain logic in CLI layer | −5 | CLI code creates domain objects, does arithmetic, parses ingredients, etc. |
| No separation of formatting | −3 | Output formatting mixed into command logic instead of dedicated formatters/views |
| Copy-paste code across commands | −3 | Same formatting or error handling logic duplicated across commands |

#### Code Quality (up to −5)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| Poor error messages | −2 | Generic errors without actionable guidance |
| Missing Javadoc | −2 | Public classes and methods lack documentation |
| Poor naming/style | −1 | Unclear variable names; inconsistent formatting |

### Design Documentation (30 points) (missing all of these points due to no ADRs)

### Reflection Questions (20 points)

6 questions × ~3-4 points each. See [Reflection](#reflection) for full prompts. Answers should demonstrate genuine reflection on your design process, not just describe what you built.

---

## Submission

```text
├── src/
│   ├── main/java/app/cookyourbooks/...
│   └── test/java/app/cookyourbooks/...  (provided — do not modify)
└── REFLECTION.md
```

Ensure `./gradlew build` and `./gradlew test` succeed before submitting. Submission limit: 15 per rolling 24-hour period.
