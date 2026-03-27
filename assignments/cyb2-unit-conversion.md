---
title: "Assignment 2: Unit Conversion, Recipe and Instruction Classes"
sidebar_position: 3
image: /img/assignments/web/a2.png
---

## Overview

Welcome to the **CookYourBooks** project! Over the course of the semester, you'll be building a comprehensive recipe management application that helps users digitize, organize, and work with their recipe collections. This application will eventually support importing recipes from various sources (including OCR from photos), storing them in a structured format, and providing both command-line and graphical interfaces for managing a personal recipe library.

In this assignment, you'll expand an existing CookYourBooks domain model by implementing **unit conversion**, **recipe scaling**, and the core **recipe structure**. Building on given `Quantity` and `Ingredient` hierarchies, you'll create a flexible conversion system that supports standard metric/imperial conversions, ingredient-specific density conversions (like "1 cup flour = 125 grams"), and custom "house" overrides.

![Assignment 2: Unit Conversion, Recipe and Instruction Classes](/img/assignments/web/a2.png)

**The core challenge is designing how domain objects and the `ConversionRegistry` service work together** to enable recipe transformations. The `ConversionRegistry` intelligently selects conversion rules based on priority (house > recipe > standard) and specificity (ingredient-specific > generic).

You'll implement the conversion service and the `Recipe` and `Instruction` domain classes. **Critically, you must design the API for recipe transformations yourself:**
- Should `Recipe` have additional transformation methods? If so, what should their signatures and specifications be?
- How do transformation operations maintain loose coupling with the service layer?

**How you achieve this is up to you.** Your design decisions will determine extensibility for future requirements like recipe export formats, display customizations, and bulk conversions.

**Due:** ???, May ???, 2026 at 11:59 PM Boston Time

**Prerequisites:** This assignment builds on provided code and your understanding of Java concepts from Assignment 1. 

## Learning Outcomes

By completing this assignment, you will demonstrate proficiency in:

- **Designing for changeability** by creating modular, loosely-coupled components ([L7: Coupling and Cohesion](/lecture-notes/l7-design-for-change))
- **Applying information hiding** to encapsulate design decisions that are likely to change ([L6: Modularity and Information Hiding](/lecture-notes/l6-immutability-abstraction))
- **Implementing immutable transformations** that return new objects rather than mutating existing ones
- **Designing method specifications** with clear preconditions and postconditions ([L4: Specifications and Contracts](/lecture-notes/l4-specs-contracts))
- **Implementing `equals()` and `hashCode()`** correctly for value objects

## AI Policy for This Assignment

**AI coding assistants (such as GitHub Copilot, ChatGPT, Claude, etc.) should NOT be used for this assignment.**

This assignment focuses on design decisions that require understanding tradeoffs—something that benefits from working through the problem yourself. You may:
- Use official Java documentation
- Consult your textbook and course materials
- Ask questions in office hours or on the course discussion board
- Discuss high-level approaches with classmates (but write your own code)

Report any AI usage in the [Reflection](#reflection) section.

### Grading Infrastructure Security

Your code executes in a containerized environment with filesystem and network access. **Do not attempt to access, exfiltrate, or reverse-engineer grading infrastructure, instructor test suites, or other non-distributed course materials.** All submissions are recorded in an immutable audit trail, and we have automated tooling to detect such attempts. Violations will be referred to OSCCR. See the [syllabus](/syllabus#grading-infrastructure-security) for full details.

If something seems wrong with the autograder, **ask us**—don't try to debug it yourself by inspecting the grading environment.

## Technical Specifications

### Package Organization

This assignment uses a package structure that organizes classes by responsibility:

```
src/main/java/app/cookyourbooks/
├── model/           # Core domain entities
│   ├── Quantity.java              # PROVIDED - fully implemented
│   ├── ExactQuantity.java         # PROVIDED - fully implemented
│   ├── FractionalQuantity.java    # PROVIDED - fully implemented
│   ├── RangeQuantity.java         # PROVIDED - fully implemented
│   ├── Unit.java                  # PROVIDED - fully implemented
│   ├── UnitSystem.java            # PROVIDED - fully implemented
│   ├── UnitDimension.java         # PROVIDED - fully implemented
│   ├── Ingredient.java            # PROVIDED - fully implemented
│   ├── MeasuredIngredient.java    # PROVIDED - fully implemented
│   ├── VagueIngredient.java       # PROVIDED - fully implemented
│   ├── IngredientRef.java         # PROVIDED - mostly complete (record)
│   ├── Instruction.java           # STUB - implement this
│   └── Recipe.java                # STUB - implement this
├── conversion/      # Unit conversion logic
│   ├── ConversionRule.java        # STUB - implement this (record)
│   ├── ConversionRulePriority.java   # PROVIDED - fully implemented (enum)
│   ├── ConversionRegistry.java    # PROVIDED - interface definition only
│   ├── LayeredConversionRegistry.java  # STUB - implement this
│   └── StandardConversions.java   # PROVIDED - fully implemented
└── exception/       # Custom exceptions
    └── UnsupportedConversionException.java  # PROVIDED - fully implemented
```

**Starter Code:** All classes exist with proper Javadoc and method signatures. Classes marked **STUB** have method bodies that throw `UnsupportedOperationException`—you must implement them. Classes marked **PROVIDED** are fully functional.

### Provided Code for Ingredients and Quantities

When inheriting a new codebase, you need to know two things:
1. What is already implemented for you
2. What does the already implemented code actually solve or cover

Below is a table of the provided interfaces, classes, and their purposes in the current codebase. Read through both the table and the documentation of these to understand what they represent in the codebase.

| Provided                  | Purpose                                                 | Example |
| ---                       | ---                                                     | --- |
| `Ingredient.java`         | Interface representing a single ingredient in a recipe  |     |
| `MeasuredIngredient.java` | Represents an ingredient with a preciese quantity       | "2.5 cups flour", "100 grams sugar", "3 whole eggs" |
| `VagueIngredient.java`    | Represnts an ingredient withour precise quantity        | "salt to taste", "a pinch of pepper", "water as needed" |
| `Unit.java`               | Interface representing a unit of measurement            | "grams", "cups", "pinch" |
| `UnitSystem.java`         | An enum representing the unit system used for a quantity | IMPERIAL", "METRIC", "HOUSE" |
| `UnitDimension.java`      | An enum representing what the unit represents | "WEIGHT", "DIMENSION". "COUNT", "OTHER"  |
| `Quantity.java`           | Interface representing a quantity, coupled with a unit | |
| `ExactQuantity.java`      | Reepresents a single precise amount                     | "2.5 cups", "100 grams" |
| `FractionalQuantity.java` | Represents an amount in fractions                       | "1/2 cup", "2 1/3 tablespoons" |
| `RangeQuantity.java`      | Represents a range of amounts                           | "2-3 cups", "100-150 grams" |

### Design Task: Transforming Recipes

In this section, we focus on what **your code** should handle. From here on out, we may have provided some pieces (e.g. semi-complete classes, starter or complete tests), but it will be your responsibility to make sure your code meets this specification and you have tested that code thoroughly.

#### Unit Conversion

Unit conversion in cooking is more complex than simple mathematical ratios. Consider these scenarios:

1. **Standard conversions** follow fixed ratios: 1 cup = 236.588 mL, 1 pound = 453.592 grams (provided in `StandardConversions.java`)
2. **Ingredient-specific conversions** account for density: 1 cup of flour ≠ 1 cup of honey in weight
3. **House overrides** reflect personal preferences or equipment: "In my kitchen, 1 oz = 30 mL" (rounded for convenience)

Your conversion system must support all three, with this **priority order** (highest to lowest):
1. **House conversions** - User-defined overrides that always take precedence
2. **Recipe-specific conversions** - Conversions defined within a particular recipe
3. **Global conversions** - Standard conversions available to all recipes

Within a priority level, your system must prefer more specific rules (those that specify an ingredient name) over generic rules (those that do not specify an ingredient name). If multiple rules with the same priority level apply, your system must prefer the rule that was added first.

Conversions may span different dimensions when appropriate ingredient context is provided:
- Volume ↔ Volume (cups to mL): Always possible within same dimension
- Weight ↔ Weight (oz to grams): Always possible within same dimension
- Volume ↔ Weight (cups to grams): Requires ingredient-specific density information (e.g., "1 liter of water = 1 kilogram of water")
- Count ↔ Weight (whole eggs to grams): Requires ingredient-specific information

**Impossible conversions** (e.g., weight to volume without density information) should throw an `UnsupportedConversionException` (a checked exception provided in the handout code).

#### Recipe Transformations

Your implementation must support three types of recipe transformations (defined as methods on the `Recipe` class):

1. **Scale by multiplier**: Scale all `MeasuredIngredient` quantities by a factor (e.g., 2x doubles everything). `VagueIngredient`s remain unchanged. Any servings (if present) should also scale.

2. **Scale to ingredient target**: Scale a recipe as defined above, but choosing a scaling factor such that a specific ingredient reaches a target amount.
   For example, say a recipe has "2 cups flour". Scaling this recipe to "500g flour" requires:
     - Converting the ingredient's current quantity (2 cups) to the target unit (grams) using a density conversion rule: 2 cups × 125 g/cup = 250g
     - Calculating the scale factor: 500g / 250g = 2.0
     - Scaling the entire recipe by that factor
   Some additional requirements follow:
     - Notice the target ingredient ends up in the target unit (grams in the example above). Other ingredients that can be converted to the target unit should also be converted to the target unit as well.
       Continuing the example, if the recipe has "1 cup white sugar", then it must also be converted to "250g white sugar" when scaling the recipe to "500g flour".
     - Scaling must handle cross-dimension conversions (cups ↔ grams) when conversion rules exist.
     - Scaling must use recipe-specific conversion rules at `RECIPE` priority.

3. **Convert to unit**: Convert all `MeasuredIngredient` quantities to a target unit. `VagueIngredient`s remain unchanged. Servings are never converted.
   - Conversion must automatically use recipe-specific conversion rules at `RECIPE` priority
   - Conversion should throw `UnsupportedConversionException` if any `MeasuredIngredient` cannot be converted

**Design considerations:**
- All transformations must maintain immutability (return new objects).
- Transformations must also update any `IngredientRef`s in instructions.
- Quantity type behavior: `RangeQuantity` stays `RangeQuantity`, fractional quantities become `ExactQuantity`.

### Service Interface: ConversionRegistry

The `ConversionRegistry` interface (provided) defines the various methods for managing conversion rules and converting quantities with those rules in the priority order mentioned earlier. You must implement it in a class called `LayeredConversionRegistry`.

**Your implementation (`LayeredConversionRegistry`)** must handle all of the following:
1. **Rule storage** organized by priority level
2. **Rule matching** that respects both priority and specificity
3. **Conversion execution** that throws appropriate exceptions when conversions fail
4. **Immutable operations** where each `withRule`/`withRules` creates a new registry

See the full interface documentation in the source code. You must implement that interface.

### Design Details

In this section, we outline what your design is required to handle and list what you are allowed to do as part of your design. Make sure your implementation follows these requirements and constraints for full credit on the assignment!

#### Design Requirements

This section outlines at a high-level what your design is required to do. Failure to adhere to these will result in loss of design points.

**What you MUST do in your design:**
- **Immutability:** All domain objects (`Recipe`, `Instruction`, `Quantity` subclasses) and the `ConversionRegistry` must be immutable. Transformation methods must return **new** objects.
- **Information hiding:** Internal representation of any class should not be exposed through the API or visible to the code outside of that class
- **Defensive copying:** Getters returning collections must return unmodifiable views or copies
- **Null safety:** Use `@NonNull` and `@Nullable` annotations from JSpecify to document nullability (we provide package-level default NullMarked annotation). You do **not** need to add runtime null checks for `@NonNull` parameters—the annotations serve as documentation and enable static analysis tools.
- **Documentation:** Javadoc for all public classes, methods, constructors with `@param`, `@return`, `@throws` tags. Use good specifications that demonstrate restrictiveness, generality, and clarity.

**What you CAN do in your design:**
- ✅ **Add new public methods** to domain classes (`Recipe`, `MeasuredIngredient`, `Quantity`, etc.)
- ✅ **Add new private methods and fields** to domain classes
- ✅ **Create new classes** in the `model`, `conversion`, or other packages
- ✅ **Create new interfaces** if your design requires them
- ✅ **Add helper/utility classes** for transformation logic

**What you CANNOT do in your design:**
- ❌ **Modify existing method signatures** in provided classes (changing parameters, return types, or throws clauses)
- ❌ **Modify the `ConversionRegistry` interface** (you implement it, but cannot change it)
- ❌ **Remove or rename existing methods** from provided classes
- ❌ **Change existing constructors** in provided stub classes
- ❌ **Modify provided interfaces** (`ConversionRegistry`) or enums (`ConversionRulePriority`)

### Implementation Details

**Read the handout code!** The starter code includes complete Javadoc and method signatures for all classes. The specifications below provide high-level context, but **you should read the source files** for detailed contracts, preconditions, and postconditions. As software engineers, we do spend more time reading code and understanding it than writing it. Reading code and deciding on a concrete plan saves us a lot of time when writing code~

#### Implementation Order

The starter code provides stubs for all classes that compile but throw `UnsupportedOperationException`. This allows you to implement incrementally while keeping the project in a compilable state. The `Recipe` transformation method signatures (`scale()`, `scaleToTarget()`, `convert()`) are defined in the stub—you must implement them. What follows is a step by step suggestion for how to tackle the assignment. If this is the first time working with this much code, we suggest following these steps closely and reflecting on why we chose these steps in this order to handle the assignment.

1. Complete the Foundation Classes.
  - Implement the `IngredientRef` record, which is mostly complete but missing a couple of key pieces.
  - Implement the `Instruction` and `Recipe` classes, including their `equals()` and `hashCode()` methods.
     - For `Instruction`, two instructions are considered equal if they have the same number of steps, same text, and reference the same ingredients.
     - For `Recipe`, implement the basic getters, `equals()`, and`hashCode()`. Two recipes are considered equal if the have the same title, servings, ingredients  (in order), and conversion rules (in order).
     - **Hint**: the `Ingredient` and `Quantity` hierarchies we gave you already implement `equals()` and `hashCode()`. Furthermore, the `ConversionRule` record **automatically generates** the correct `equals()` and `hashCode()`. How can you depend on these methods to implement the required `equals()` and `hashCode()` methods?
  - As you implement, test your implementation with our **sample tests** with `./gradlew test --tests InstructionTest` and `./gradlew test --tests RecipeTest`.
2. Implement the `ConversionRule` record.
  - You can **wait to implement convert()** until you have made a conscious design decision about **how** you will implement it in the later steps.
  - Test your implementation with `./gradlew test --tests ConversionRuleTest`. We have provided complete tests for you here. The autograder will run these to verify your implementation as well, so doing well on these locally is a good sign!
3. Plan out how transformations will work. Specifically go through the following steps.
  - Review the required transformation types
  - Decide where will your transformation methods go and what their method signatures will be.
  - Consider what helper methods you might need to implement those transformation methods.
4. Implement and test the scaling transformations in `Multiplier`. You will need to add or enhance the tests in `RecipeTest.java` related to scaling behavior.
5. Implement and test conversion with `LayeredConversionRegistry`.
  - We suggest starting with building the collection of rules first, then work on the `convert()` methods. Keep in mind the priority ordering mentioned in [the prior section](???)
  - Use the `ConversionRegistry` interface when testing your implementation. Make sure your tests cover the specification requirements for conversions from [the prior section](???) We have you some to start but you **must** write your own.
  - Run your tests with `./gradlew test --tests ConversionRegistryTest`. 
6. Implement scaling an ingredient to a specific target and amount.
  - As a rule of thumb, return to the example of conversion from [the prior section](???) for a regular case. Then consider the exceptional cases, like ingredients appearing multiple times.
  - Add or enhance the tests in `RecipeTest.java` to check correctness locally. Again, we always test as we go.
  - **Hint:** You will find your `ConversionRegistry` very useful to actually convert the units. If you depend on the `ConversionRegistry` to do its job, what is left for you to handle?
7. Finally, implement the conversion for the entire recipe. This means all `MeasuredIngredient` quantities are converted to whatever target unit is provided. If any conversion fails, you **must** throw the `UnsupportedConversionException`.
  - Reminder that recipe-specific conversion rules should be at `RECIPE` priority.
  - Make use of `ConversionRegistry.convert()` to handle actual conversions for you.
  - Enhance the tests in `RecipeTest.java` to test the expected recipe unit conversion behavior.
## Design and Implementation Hints

The `Recipe` class defines transformation methods (`scale()`, `scaleToTarget()`, `convert()`) that you must implement. As you implement these methods and the supporting classes, keep the questions in the [Reflection](reflection) open adn address them in your design.

In additon, sit down and plan how your `LayeredConversionRegistry` organizes its rules by answering the following questions.
   - What data structure efficiently supports priority-based search?
   - How do you maintain immutability while enabling rule additions?
   - How do you handle the "first added takes precedence" requirement at each priority level?

**This design decision combined with your answers to the reflection will be visible in your code structure.** There is no single "correct" design—what matters is that your design:
- Maintains good separation of concerns
- Supports the required functionality
- Follows the design constraints (no breaking changes)
- Can articulate tradeoffs in your reflection

**Most importantly:** Your choices about **what public methods to add** and **where to add them** will be the primary focus of design quality evaluation.

### Testing Requirements

Your tests should verify both individual components and the **service interface (`ConversionRegistry`)** which is the primary focus of this assignment.

Focus on testing **behavior and requirements**, not specific method signatures. If you follow the [Implementation Order](#implementation-order), you will have most if not all of the tests you will need.

#### Provided Test Files

We provide starter tests for the foundation classes and conversion components. **Run these tests as you implement each class to verify your progress.** See the [Implementation Order](#implementation-order) for *when* we suggest running each of these tests. What follows is a comprehensive list of what test files we provided and how complete they are.

- `ConversionRuleTest.java` — **complete tests** for `ConversionRule` record (constructor validation, `canConvert()`, `convert()`, equality). The autograder runs these same tests.
- `InstructionTest.java` — **sample tests** for `Instruction` class (only `toString()` tests are included). The autograder runs additional comprehensive tests not included in the handout. You are welcome to add your own tests for these classes if you find them helpful, but they are not graded.

Run individual tests with `./gradlew test --tests "TestClassName"` or **run all provided tests** with `./gradlew test`.

#### Required Test Files

You must enhance tests in the following files:

1. **`RecipeTest.java`** - Enhance the starter tests for the `scale()`, `scaleToTarget()`, and `convert()` methods. **Graded for fault-finding (20 points).** Your tests should verify:
   - Scaling by factor works correctly for `MeasuredIngredient`s
   - `VagueIngredient`s remain unchanged when scaling or converting
   - Servings are scaled appropriately
   - `IngredientRef`s in instructions are updated
   - `scaleToTarget()` finds the correct ingredient and calculates the right factor
   - `convert()` converts all `MeasuredIngredient` quantities to the target unit
   - Recipe-specific conversion rules are used at `RECIPE` priority
   - Edge cases like ingredient not found, unsupported conversions

2. **`ConversionRegistryTest.java`** - Enhance the starter tests for the `ConversionRegistry` **interface**. **Graded for fault-finding (20 points).** Your tests must use only the `ConversionRegistry` interface methods—do not test implementation-specific details of `LayeredConversionRegistry`. Your tests should cover:
   - `convert(Quantity, Unit)` — generic conversions without ingredient context
   - `convert(Quantity, Unit, String)` — ingredient-specific conversions

   For both methods, verify priority ordering (HOUSE > RECIPE > STANDARD), specificity handling (ingredient-specific > generic at same priority), correct conversion mechanics, and exception handling.

Run individual tests with `./gradlew test --tests "TestClassName"` or **run all provided tests** with `./gradlew test`.

As on assignment 1, your tests must **not** depend on any of your own implementation details. The tests must utilize only the public APIs as provided in the assignment handout.


## Reflection

Update `REFLECTION.md` to address:

1. **API Design & Coupling:** Why are transformation methods on `Recipe` rather than in a separate service? What type of coupling exists between `Recipe` and `ConversionRegistry`, and how does the design keep it loose?

2. **Responsibility Assignment:** Where did you put the logic for transforming ingredients? Did you add helper methods to domain classes? How did you decide what belongs where?

3. **Information Hiding:** What design decisions are hidden behind the `ConversionRegistry` interface? What could change in `LayeredConversionRegistry` without affecting code that uses the interface?

4. **Immutability:** What are the benefits and costs of requiring immutable `Recipe` objects? How did immutability affect your transformation implementation?

5. **Extensibility:** Pick one future requirement (e.g., bulk conversion to metric, export with unit preferences, a `RecipeBook` class). How well does your design support it? What would need to change?

6. **AI Usage:** (Ungraded) Did you use AI assistance? If so, describe how and reflect on whether it helped or hindered your learning of design principles.


## Quality Requirements

Your submission should demonstrate:

- **Correctness**: Code compiles, follows specifications, passes tests
- **Design Quality**: Appropriate use of interfaces, immutability, information hiding
- **Testing**: Meaningful tests that verify behavior and detect faults
- **Documentation**: Clear Javadoc with preconditions, postconditions, and design rationale
- **Code Quality**: Clean, readable code following course style conventions

## Grading Rubric (100 points)

### Automated Grading — Implementation Correctness (50 points)

#### Model Layer Foundation (10 points)

- `IngredientRef` (2 points)
- `Instruction` (4 points)
- `Recipe` basic functionality (4 points) — constructor, getters, equals/hashCode, immutability

#### Conversion Components (16 points)

- `ConversionRule` (6 points)
- `LayeredConversionRegistry` (10 points)

#### Recipe Transformations (24 points)

- `Recipe.scale()` (12 points)
- `Recipe.scaleToTarget()` (7 points)
- `Recipe.convert()` (5 points)

---

### Automated Grading — Test Quality (40 points)

Tests are graded on fault-finding ability against instructor mutants.

#### RecipeTest.java — Recipe Transformations (20 points)

- `scale()` (8 points)
- `scaleToTarget()` (6 points)
- `convert()` (6 points)

#### ConversionRegistryTest.java — Conversion Service (20 points)

- `convert(Quantity, Unit)` (10 points)
- `convert(Quantity, Unit, String)` (10 points)

---

### Reflection (10 points)

- API Design & Coupling (2 points)
- Responsibility Assignment (2 points)
- Information Hiding (2 points)
- Immutability (2 points)
- Extensibility (2 points)

---

### Manual Grading — Subtractive (max -20 points)

- Coupling & Separation of Concerns (max -6 points)
- Information Hiding (max -4 points)
- Immutability Violations (max -4 points)
- Documentation & Specifications (max -3 points)
- Code Quality (max -3 points)

### Summary

| Category | Points |
|----------|--------|
| Implementation Correctness | 50 |
| Test Quality (fault-finding) | 40 |
| Reflection | 10 |
| **Total** | **100** |
| Manual Grading (subtractive) | up to -20 |
| **Final Score Range** | **80–100** |

Note: Students who pass all automated tests and write good reflections earn 100 points. Excellent design quality means no deductions (score stays at 100). Poor design choices result in deductions down to a minimum of 80 points.

## Submission

Submit via Pawtograder (via GitHub). As with assignment 1, there is a limit of 15 submissions per-24-hour period. Submissions that receive a score of "0" will not count towards your limit.

Good luck! Remember: understanding the design decisions in the provided code and articulating tradeoffs in your reflection are necessary to receive full marks - not just passing the tests.
