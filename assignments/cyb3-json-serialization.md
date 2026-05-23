---
title: 'Assignment 3: Domain Extensions and File Exporting'
sidebar_position: 4
---


## Overview

In this assignment, you'll expand the CookYourBooks application in two major directions: **domain modeling** and **exporting data to files**. You will:

- Model the different sources recipes can come from (published cookbooks, personal collections, websites) and a user's library that organizes them
- Export recipes and collections to Markdown

This assignment emphasizes **separating concerns** between your core domain logic and external concerns like storage and file formats.

**Due:** Thursday, May 28, 2026 at 9:00 PM Boston Time

**Prerequisites:** This assignment builds on the A2 sample implementation (provided). You should be familiar with `Recipe`, `Quantity`, `Ingredient`, and the conversion system from Assignment 2.

**Starter Code:** We provide all interface definitions and supporting types so you can focus on implementation and design decisions rather than transcription. See [What's Implemented For You](#whats-implemented-for-you) for details.

:::tip How to Succeed on This Assignment

This assignment has more moving parts than previous ones. Here's a pacing strategy that works:

1. **Read this handout when it's released.** Skim the whole thing to understand the scope. You don't need to understand every detail yet—just get the big picture.
2. **Look at the starter code as soon as possible.** Open the files, read through `CookbookImpl` (the reference implementation), and start connecting the handout to actual code.
3. **Post questions on the discussion board.** If something in the handout or starter code doesn't make sense, ask early—it helps everyone. Especially if something in the specification is unclear to you.
4. **Work incrementally over several days.** Don't try to do everything in one session. Let ideas settle and come back with fresh eyes.
5. **If you're stuck for more than 30 minutes on an error: STOP.** Post on the discussion board, then step away for a few hours. Banging your head against an error rarely helps.
6. **Submit early and often.** The limit is 15 per rolling 24 hours—use early submissions as free feedback from the autograder.

**The discussion board is your best resource.** Course staff can click your name to see your latest submission. Post publicly (anonymously or not)—your question helps future students too.

:::

---

## Learning Objectives

By completing this assignment, you will demonstrate proficiency in:

- **Separating concerns** by defining interfaces and implementing them independently
- **Writing comprehensive tests** that validate behavior and detect faults in complex systems

---

## Assignment Context and Concepts

### Where Recipes Come From

Recipes come from many sources, and CookYourBooks needs to handle them all:

- **Published cookbooks**: Physical or digital books with ISBN, author, publisher, and publication year.
- **Personal collections**: A family recipe binder, a folder of index cards, grandmother's handwritten notes—has a title and maybe some organization, but no formal publication metadata.
- **Websites**: Recipes scraped or imported from cooking websites—has a URL, possibly a site name, and maybe a date accessed.

Your challenge is to implement concrete classes that fulfill interface contracts for each of these. The interfaces define an inheritance hierarchy (`Cookbook`, `PersonalCollection`, `WebCollection` each extending `RecipeCollection`), and `CookbookImpl` is provided as a complete reference implementation for you to study and apply.

### Architecture: Layers and Interfaces

This assignment expands the model to hold collections of recipes and enable exporting recipes and collections to Markdown files.

The diagram below shows the complete architecture. Blue dashed classes are provided interfaces; yellow classes are what you implement. We will start including these diagrams when relevant as our codebase increases in size and complexity.

```mermaid
classDiagram
    direction TB

    class Recipe { <<from A2>> }
    class Ingredient { <<abstract, from A1>> }
    class Quantity { <<abstract, from A1>> }

    class RecipeCollection {
        <<interface, provided>>
        +getId() String
        +getTitle() String
        +getSourceType() SourceType
        +getRecipes() List~Recipe~
        +findRecipeById(String) Optional~Recipe~
        +containsRecipe(String) boolean
        +addRecipe(Recipe) RecipeCollection
        +removeRecipe(String) RecipeCollection
    }

    class Cookbook {
        <<interface, provided>>
        +getAuthor() Optional~String~
        +getIsbn() Optional~String~
        +getPublisher() Optional~String~
        +getPublicationYear() OptionalInt
    }

    class PersonalCollection {
        <<interface, provided>>
        +getDescription() Optional~String~
        +getNotes() Optional~String~
    }

    class WebCollection {
        <<interface, provided>>
        +getSourceUrl() URI
        +getDateAccessed() Optional~LocalDate~
        +getSiteName() Optional~String~
    }

    class SourceType {
        <<enum, provided>>
        PUBLISHED_BOOK
        PERSONAL
        WEBSITE
    }

    class CookbookImpl { <<provided reference>> }
    class PersonalCollectionImpl { <<you implement>> }
    class WebCollectionImpl { <<you implement>> }

    class UserLibrary {
        <<interface, provided>>
        +getCollections() List~RecipeCollection~
        +addCollection(RecipeCollection) UserLibrary
        +removeCollection(String) UserLibrary
        +findRecipesByTitle(String) List~Recipe~
        +findCollectionById(String) Optional~RecipeCollection~
        +findCollectionByTitle(String) Optional~RecipeCollection~
        +findAllCollectionsByTitle(String) List~RecipeCollection~
        +findRecipeById(String) Optional~Recipe~
    }

    class UserLibraryImpl { <<you implement>> }

    class MarkdownExporter {
        <<you implement>>
        +exportRecipe(Recipe) String
        +exportCollection(RecipeCollection) String
        +exportToFile(Recipe, Path) void
        +exportToFile(RecipeCollection, Path) void
    }

    RecipeCollection <|-- Cookbook
    RecipeCollection <|-- PersonalCollection
    RecipeCollection <|-- WebCollection
    Cookbook <|.. CookbookImpl
    PersonalCollection <|.. PersonalCollectionImpl
    WebCollection <|.. WebCollectionImpl
    RecipeCollection --> Recipe
    RecipeCollection --> SourceType
    UserLibrary --> RecipeCollection
    UserLibrary <|.. UserLibraryImpl

    style Recipe fill:#e0e0e0,stroke:#999
    style Ingredient fill:#e0e0e0,stroke:#999
    style Quantity fill:#e0e0e0,stroke:#999
    style RecipeCollection fill:#90D5FF,stroke:#4ac,stroke-width:2px,stroke-dasharray: 5 5
    style Cookbook fill:#90D5FF,stroke:#4ac,stroke-width:2px,stroke-dasharray: 5 5
    style PersonalCollection fill:#90D5FF,stroke:#4ac,stroke-width:2px,stroke-dasharray: 5 5
    style WebCollection fill:#90D5FF,stroke:#4ac,stroke-width:2px,stroke-dasharray: 5 5
    style SourceType fill:#90D5FF,stroke:#4ac,stroke-width:2px,stroke-dasharray: 5 5
    style UserLibrary fill:#90D5FF,stroke:#4ac,stroke-width:2px,stroke-dasharray: 5 5
    style CookbookImpl fill:#d4edda,stroke:#28a745
    style PersonalCollectionImpl fill:#fff3cd,stroke:#856404
    style WebCollectionImpl fill:#fff3cd,stroke:#856404
    style UserLibraryImpl fill:#fff3cd,stroke:#856404
    style MarkdownExporter fill:#fff3cd,stroke:#856404
```

**Legend:** Gray = from A1/A2 · Blue dashed = provided interfaces · Green = provided reference implementation · Yellow = you implement

### Repository Structure

```
src/
├── main/java/app/cookyourbooks/
│   ├── model/
│   │   ├── RecipeCollection.java          (PROVIDED - interface)
│   │   ├── Cookbook.java                  (PROVIDED - interface)
│   │   ├── PersonalCollection.java        (PROVIDED - interface)
│   │   ├── WebCollection.java             (PROVIDED - interface)
│   │   ├── SourceType.java                (PROVIDED - enum)
│   │   ├── UserLibrary.java               (PROVIDED - interface)
│   │   ├── CookbookImpl.java              (PROVIDED - reference, study this)
│   │   ├── PersonalCollectionImpl.java    (YOU COMPLETE)
│   │   ├── WebCollectionImpl.java         (YOU COMPLETE)
│   │   ├── UserLibraryImpl.java           (YOU COMPLETE)
│   │   └── ... (A1/A2 classes, provided)
│   └── adapters/
│       └── MarkdownExporter.java          (YOU COMPLETE)
│   └── repository/
│       └── RepositoryException.java       (PROVIDED - class)
└── test/java/app/cookyourbooks/
    ├── model/
    │   ├── RecipeCollectionTest.java      (YOU EXPAND)
    │   └── UserLibraryTest.java           (YOU EXPAND)
    └── adapters/
        └── MarkdownExporterTest.java      (YOU EXPAND)
```

### What's Implemented For You

| File | Description |
|---|---|
| `RecipeCollection.java` | Base interface for all collections |
| `Cookbook.java` | Interface for published cookbooks |
| `PersonalCollection.java` | Interface for personal collections |
| `WebCollection.java` | Interface for web-sourced collections |
| `SourceType.java` | Enum with `PUBLISHED_BOOK`, `PERSONAL`, `WEBSITE` |
| `UserLibrary.java` | Interface for user's recipe library |
| `Recipe.java` (updated) | Now includes `id` field with auto-generation |
| **`CookbookImpl.java`** | **Complete reference implementation—study this first** |
| `RepositoryException.java` | Unchecked exception for persistence and exporting failures |

**Test files:**

| File | Description |
|---|---|
| `RecipeCollectionTest.java` | Starter test file (you expand) |
| `UserLibraryTest.java` | Starter test file (you expand) |
| `MarkdownExporterTest.java` | Starter test file (you expand) |

### AI Policy for This Assignment

**AI coding assistants (such as GitHub Copilot, ChatGPT, Claude, etc.) should NOT be used for this assignment.**

This assignment focuses on learning from sample code, working with a new package, and understanding how to test against file formats. You may:

- Use official Java documentation (especially for the `Files` and `Paths` classes used later in the assignment)
- Consult any textbook and course materials
- Ask questions in office hours or on the course discussion board (especially if something is unclear in this specification)
- Discuss high-level approaches with classmates (but write your own code)

As always, planning your design and writing tests before diving into implementation allows you to check understanding, catch bugs during development,
and saves overall time in the long run.
---

## Design Task

Before writing implementation code, you need to make and document the following design decisions. Your choices here affect your entire codebase—think first, consider possible tradeoffs (i.e. pros vs. cons of your choices), then implement.

### Recipe ID Field

For true persistence in future assignments, recipes will need unique identifiers. The starter code already includes an `id` field in `Recipe`:

```java
public Recipe(
    @Nullable String id,  // null = auto-generate UUID
    String title,
    @Nullable Quantity servings,
    List<Ingredient> ingredients,
    List<Instruction> instructions,
    List<ConversionRule> conversionRules)
```

IDs are auto-generated as UUIDs (universally unique identifiers) when `null` is passed. Our programs will assume IDs contain no characters that are invalid in filenames. Auto-generated UUIDs satisfy this and guarantee a unique id for the entirety of the program's run.

### Collection Class Design

Each collection type must have a named implementation class:

| Interface | Implementation Class |
|---|---|
| `Cookbook` | `CookbookImpl` |
| `PersonalCollection` | `PersonalCollectionImpl` |
| `WebCollection` | `WebCollectionImpl` |

Furthermore, each class has different optional data it can hold onto:

| Interface | Required Data | Optional Data |
|---|---|---|
| `Cookbook` | title | author, ISBN, publisher, publication year |
| `PersonalCollection` | title | description, notes |
| `WebCollection` | title, source URL | date accessed, site name |

The constructors take in the following data:

- an `id`.
- the required `title`.
- a `List` of `Recipe`s
- the type-specific data as mentioned in the table above.

The constructors must also have the following behaviors:

- If any **required** data is missing (or blank (empty or whitespace-only) for `String` type data), the constructor **must** throw an `IllegalArgumentException` The constructors have already been annotated for you using NullAway annotations for your convenience. You must handle the rest.
- If the list of recipes contains at least 2 recipes with the same ID, the constructor **must** throw an `IllegalArgumentException`.
- If the `id` is missing, the constructor **must** create a UUID. (See `CookbookImpl` for how this is done).

**Your primary design task** is deciding how to structure `PersonalCollectionImpl` and `WebCollectionImpl`. Study `CookbookImpl` carefully—it is a complete reference that shows the immutability pattern you must follow. Then decide how to store optional fields (`Optional<String>` as the field type, or nullable with conversion in the getter?)

**Note on Optional Fields**: All optional fields in collection interfaces return `Optional<T>` to clearly signal when a value is not specified. This includes both `String` fields (e.g., `Cookbook.getAuthor()` returns `Optional<String>`) and non-`String` fields (e.g., `Cookbook.getPublicationYear()` returns `OptionalInt`, `WebCollection.getDateAccessed()` returns `Optional<LocalDate>`). Using `Optional` consistently provides type safety and forces explicit handling of missing values.

You can create an `Optional` object that is empty using `Optional.empty()`. You can also create an `Optional` object for an existing value using `Optional.of(T value)` or `Optional.ofNullable(T value)`. See the [`Optional` class Java documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html) for more information as well as `CookbookImpl` for example usage.

**Blank String Handling for WebCollection**: The `siteName` field follows the same blank string normalization as other optional `String` fields—blank strings (empty or whitespace-only) are treated as absent and `getSiteName()` must return `Optional.empty()`.

Document your approach and rationale in `REFLECTION.md`.

### Required Design Properties

Regardless of the structural decisions you make, all implementations must satisfy:

- **Immutability.** All domain objects must be immutable. Transformation methods return new instances.
- **Separation of concerns.** Domain classes must not depend on file I/O, or persistence and file exporting implementations (e.g. the `MarkdownExporter`).
- **Interface abstraction.** Code using other objects must depend on their interfaces, not the concrete class.
- **Null safety.** Use `@NonNull` / `@Nullable` from JSpecify. NullAway enforces this statically—you do not need runtime null checks for parameters.
- **Documentation.** Javadoc on all public classes and methods, including design decisions.

### Files and Paths

The `MarkdownExporter` exposes two methods to write to actual files on your file system.

#### Path

The `Path` type represents a path in your file system. Example paths include:

- `src/main/java/adapters/MarkdownExporter.java` on Mac and Unix Systems
- `src\main\java\adapters\MarkdownExporter.java` on Windows systems
- `README.md` on both

The `Path` type abstracts away the underlying file system used by an operating system, allowing programs to refer to specific files easily.

For more information and methods you can use on `Path`, see the [`Path` documentation from Java 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html).

#### Files

The `Files` class exposes **static** methods to make reading from files more convenient. Most of the methods will take in a `Path`, avoiding the use of different `InputStream` types we do not need to use. Read about all of these methods in the [`Files` documentaton from Java 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html). Here are some methods we recommend taking a look at the following for this assignment, but you are free to use others:

- `boolean exists(Path path, LinkOptions... options)` :: does the file referred to by path exist?
- `String readString(Path path) throws IOException` :: put the contents of the file referred to by path in a single String
- `void writeString(Path path, CharSequence csq, OpenOptions... options) throws IOException` :: write the contents of csq into the file referred to by Path. Note that **String** is a `CharSequence`!

**A note on argument types annotated with ...**: In `exists` and `writeString`, the last argument is annotated with `...`. In Java, we call those parameters `varargs`, or variable arguments. This means we can supply 0 or more arguments of the specified type. In this case, if we don't have any options to give to those methods, we can simply **ignore the parameter in the method** and not supply an argument for that parameter. In other words, the following can be considered valid method signatures for those methods:

    - `boolean exists(Path path)`
    - `void writeString(Path path, CharSequence csq)`

---

## Implementation Task

You have three concrete implementation areas. Work through them in order—each builds on the previous.

### What You Implement

| Your Code | Description |
|---|---|
| `PersonalCollectionImpl` | Implement following `CookbookImpl` pattern |
| `WebCollectionImpl` | Implement following `CookbookImpl` pattern |
| `UserLibraryImpl` (4 methods) | Complete the search methods |
| `MarkdownExporter` | Complete the provided stub |
| Test files | Expand all starter tests |

---


### Phase 1: Collection Classes

Implement `PersonalCollectionImpl` and `WebCollectionImpl` following the design in `CookbookImpl`.

See the [Collection Class Design](#collection-class-design) for information on the design.

#### Behavioral specifications for all collection types

Refer to the Javadoc on `RecipeCollection` for the full method-level specifications. In addition, the following behaviors must also be satisfied:

- Recipe order is preserved and significant for equality comparisons
- Two collections are equal if they have the same ID, title, source type, type-specific metadata, and recipes in the same order
- Blank optional String fields (empty or whitespace-only) are treated as absent and must return `Optional.empty()`


**What we test:**
- `equals` and `hashCode` contracts
- behaviors mentioned for each method are fulfilled by your implementations

---

### Part 2: UserLibraryImpl

`UserLibraryImpl` is a user's in-memory collection of recipe collections. A partial implementation is provided—you must implement the four search methods.

Before diving into implementation, read the Javadoc on `UserLibraryImpl`. Each method you need to complete is documented with its full behavioral specification.

**Persistence note:** `UserLibrary` is an in-memory convenience wrapper. For now, we can only export it to Markdown using the `MarkdownExporter`. Later in the project, you will parsing files containing recipes and collections, allowing you to load CookYourBooks state from prior runs and enabling persistence.

**What we test:**

- behaviors mentioned for each method are fulfilled by your implementation
- **Type preservation**: methods that return `RecipeCollection` return the proper implementation (e.g. storing a `Cookbook` and retrieving that same collection preserves the type `Cookbook`)

---

### Part 3: MarkdownExporter

Implement the missing methods in `MarkdownExporter`, carefully reading the documentation of each method before implementing.

### Part 3a: Recipe Exporter Methods

Implement `exportRecipe` and its corresponding `exportToFile` overload. Their output must conform to the following format:

```markdown
# {Recipe Title}

_Serves: {servings}_

## Ingredients

- {ingredient1.toString()}
- {ingredient2.toString()}

## Instructions

{instruction1.toString()}
{instruction2.toString()}

---

_Exported from CookYourBooks, learn more at https://www.cookyourbooks.app_
```

**Example:**

```markdown
# Chocolate Cake

_Serves: 8 whole_

## Ingredients

- 2 cups flour
- 1 cup sugar

## Instructions

1. Preheat oven to 350°F
2. Mix dry ingredients

---

_Exported from CookYourBooks, learn more at https://www.cookyourbooks.app_
```

**Format rules:**

- If the recipe has no servings, omit the `_Serves: ..._` line entirely (no extra blank line)
- Use `Ingredient.toString()` and `Instruction.toString()` (the latter includes the step number, e.g., "1. Mix ingredients")
- Include `## Ingredients` and `## Instructions` headers even if lists are empty
- Footer (`---` and the exported-from line) is always required
- Titles and ingredient names are included as-is (no Markdown escaping)
- Unix line endings (`\n`)

### Part 3b: Collection Exporter Methods

Implement `exportCollection` and its corresponding `exportToFile` overload. Their output must conform to the following format:

```markdown
## {Collection Title}

{metadata line}

---

# {Recipe 1 Title}

...recipe content without individual footer...

---

# {Recipe 2 Title}

...

---

_Exported from CookYourBooks, learn more at https://www.cookyourbooks.app_
```

**Metadata line by collection type:**

| Type | Format | Example |
|---|---|---|
| `Cookbook` | `_By: {author}_` (omit if no author) | `_By: Julia Child_` |
| `PersonalCollection` | `_{description}_` (omit if no description) | `_Family recipes passed down for generations_` |
| `WebCollection` | `_Source: {url}_` (always present) | `_Source: https://example.com/recipes_` |

**Example: Cookbook with one recipe:**

```markdown
## The Joy of Cooking

_By: Irma Rombauer_

---

# Chocolate Cake

_Serves: 8 whole_

## Ingredients

- 2 cups flour
- 1 cup sugar

## Instructions

1. Preheat oven to 350°F
2. Mix dry ingredients

---

_Exported from CookYourBooks, learn more at https://www.cookyourbooks.app_
```

**Format rules:**

- Collection title uses H2 (`##`); recipe titles use H1 (`#`)
- Metadata line is omitted entirely if the optional field is not present
- Recipes within a collection use the recipe format **without** the individual recipe footer
- Only the final recipe includes the CookYourBooks footer
- If a collection has no recipes, include only the header and metadata (no `---` separators)
- Unix line endings (`\n`)

---

### Testing Requirements

Testing follows the same model as Assignment 2.

- Write tests for all components you implement
- **Tests must be written to the interface, not your implementation**
- Your tests must pass on the instructor's reference implementation
- Your tests are run against intentionally buggy implementations (mutation testing)

**Required test files:**

| Test File | Focus |
|---|---|
| `model/RecipeCollectionTest.java` | Construction, immutable transformations, equals/hashCode |
| `model/UserLibraryTest.java` | Library operations, search across collections |
| `adapters/MarkdownExporterTest.java` | Recipe format correctness |

**Testing guidance:**

- **Format tests:** For `exportRecipe`, test exact string matches against expected Markdown
- **Edge cases:** Empty collections, absent optional fields, special characters in names
- **Error cases:** Invalid input throws appropriate exceptions

:::warning Avoid Order-Dependent Tests

Several methods have unspecified ordering: `findAll()`, `findAllByTitle()`, `UserLibrary.getCollections()`, and `UserLibrary.findRecipesByTitle()` do not guarantee any particular order.
Below is an example of a test that assumes an order and another that does not assume order (or is order-independent).

```java
//OBJECTIVE: verify that there is a recipe for Chocolate Cake in the repository

// BAD: assumes specific order
List<Recipe> results = repository.findAll();
assertEquals("Chocolate Cake", results.get(0).getTitle());

// GOOD: order-independent
List<Recipe> results = repository.findAll();
assertEquals(2, results.size());
assertTrue(results.stream().anyMatch(r -> r.getTitle().equals("Chocolate Cake")));
```

Tests that fail on correct implementations due to ordering assumptions will not receive credit.

:::


:::tip MarkdownExporter Tests Benefits from Planning

When testing the `MarkdownExporter`, consider the cases of recipes you would see For example, we could consider recipes with all fields, recipe without servings, empty ingredients/instructions, multiple ingredients, special characters, and so on. Take a moment to write down the different types of recipe objects that could be created
and manually write what the expected Markdown would be. **Remember you are allowed to share and collaborate on ideas with others**. Meet up and compare lists to see if you are missing any edge cases.
Software engineering improves when we introduce more perspectives and its a great way to learn new edge cases.

:::

::: tip Use @TempDir for tests that require files

When writing tests for methods that perform I/O, we may need temporary files to read or write to. Furthermore, we have
to clean up those temporary files when we are done. For these reasons and more, we use the `@TempDir` annotation in JUnit 
for cleaner temporary file management. Below is an example test that uses an `@TempDir` to test `exportToFile(Recipe, Path)`.

```java
@TempDir Path tempDir; // No need to initialize! JUnit will do it for you!
MarkdownExporter exporter;

@Test
void ensureTitleIsWrittenToFile() {
    Recipe recipe = new Recipe(null, "Pancake", List.of(), List.of(), List.of());

    // Find the path to this file (already existing or otherwise) in our temporary directory.
    // Since we haven't done anything, the file doesn't exist yet...
    Path pancakePath = tempDir.resolve("panckages.md");

    // ...but it will after this call!
    exporter.exportToFile(recipe, pancakePath);

    // Let's read the data and assert what we care about!
    String fileData = Files.readString(pancakePath);
    assertTrue(fileData.startsWith("# Pancake"));
}
```

`MarkdownExporterTest` already has the barebones setup for this along with a version of the above test.

:::

---

## Reflection

Complete the **6 reflection questions** in `REFLECTION.md`. Each question is worth 4 points (24 points total).

1. **Domain Model Design** — Describe your approach to implementing `PersonalCollectionImpl` and `WebCollectionImpl`.
How did you leverage the `CookbookImpl` reference implementation? What modifications did you make
for each collection type's unique metadata?
2. **Architecture and Testability** — The assignment uses interfaces (`RecipeCollection`, `RecipeRepository`) with concrete
implementations. Give a specific example from your code showing how this separation enables testing.
What would be harder to test without the interface abstraction?
3. **Searching Techniques** - Reflect on how you chose to implement the search methods in `UserLibraryImpl`. Did you use a functional style or a more iterative style and why?
4. **Test planning** - Reflect on how you came up with your test cases for Markdown tests. Report the process you used.
5. **Selecting tasks for AI Effectiveness** — Some tasks in this assignment have very low complexity. Which of those tasks would you have AI assist you with and how? What about those specific tasks would make an AI assistant valuable or beneficial?
6. **AI for Understanding Code** — In the future, you will have explicit permission to use an AI-assistant on an assignment. Given your experiences with jumping into unknown code, what are some prompts you would (or maybe have) used to understand this given starter code?

See `REFLECTION.md` for the full question prompts and grading rubric.

---

## Grading

### Automated Grading (76 points)

#### Implementation Correctness (40 points)

| Component | Points |
|---|---|
| `RecipeCollection` domain model | 12 |
| `UserLibrary` | 6 |
| `MarkdownExporter` (`exportRecipe` format correctness) | 10 |
| `MarkdownExporter` (`exportCollection` format) | 6 |
| `MarkdownExporter` (`exportToFile` file I/O) | 6 |

#### Test Suite Quality (36 points)

| Test File | Points | Notes |
|---|---|---|
| `RecipeCollectionTest.java` | 14 | Key focus: your collection implementations |
| `UserLibraryTest.java` | 8 | Test the search methods you implement |
| `MarkdownExporterTest.java` | 14 | Main challenge: Identifying all the needed cases for testing |

### Manual Grading (Subtractive, max −30 points)

| Category | Max Deduction | Criteria |
|---|---|---|
| **Architecture** | −16 | Domain depends on persistence implementations; missing interface abstractions; tight coupling |
| **Immutability** | −6 | Mutable domain objects; exposed internal collections |
| **Documentation** | −4 | Missing Javadoc; undocumented design decisions |
| **Test Quality** | −6 | Trivial tests; tests don't verify meaningful behavior |
| **Code Style** | −10 | Poor naming; overly complex logic; inconsistent style |

### Reflection (24 points)

6 questions × 4 points each. See `REFLECTION.md` for rubric.
