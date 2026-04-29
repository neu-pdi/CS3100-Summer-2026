---
title: "A5: Command Reference"
sidebar_position: 7
---

# TODO: Verify all links in this page before publishing

This page documents the required behavior, output format, and error handling for every CLI command. See the [main handout](/assignments/cyb5-service-architecture) for architecture and design requirements.

---

## General Commands

### `help` — Contextual Help

```bash
cyb> help
```

Displays all available commands grouped by category. When given a command name, shows detailed help for that command.

```bash
cyb> help scale
```

**Requirements:**
- `help` with no arguments lists all commands grouped by category (Library, Recipe, Tools, General) — see [Example Session](#example-session) for expected output
- `help <command>` shows detailed usage. The `<command>` argument is the top-level command word only (e.g., `help scale`, `help collection`, `help import`) — multi-word subcommand lookups like `help collection create` are not required
- Unknown command: `Unknown command: '<name>'. Type 'help' for a list of commands.`

### `quit` / `exit` — Exit the Application

```bash
cyb> quit
Goodbye!
```

Exits the application gracefully.

---

## Library Commands

### `collections` — List Collections

```bash
cyb> collections
```

Lists all recipe collections from the `RecipeCollectionRepository`, showing each collection's title, source type, and recipe count.

**Example output:**
```text
Collections:
  1. Holiday Favorites        [Personal]   12 recipes
  2. Joy of Cooking           [Cookbook]     8 recipes
  3. Budget Bytes             [Web]          5 recipes
```

### `collection create <name>` — Create a Personal Collection

```bash
cyb> collection create "Holiday Favorites"
```

Creates a new personal collection with the given title and saves it to the repository.

**On success:** `Created personal collection 'Holiday Favorites'.`

**Error handling:**
- Blank or empty name: Display a helpful message

### `recipes <collection>` — List Recipes in a Collection

```bash
cyb> recipes "Joy of Cooking"
```

Lists all recipes in the specified collection. Collection is identified by title (case-insensitive). If the title contains spaces, it must be quoted.

**Example output:**
```text
Joy of Cooking (8 recipes):
  1. Chocolate Chip Cookies          Serves 24 cookies
  2. Classic Pancakes                Serves 4
  3. Beef Stew                       Serves 6
  ...
```

**Requirements:**
- When a recipe has no servings information, display `No Servings` in place of the servings line. This applies wherever recipe servings are shown: `recipes`, `show`, and `cook` mode header.

**Error handling:**
- Collection not found: `Collection not found: 'Unknown Collection'. Use 'collections' to see available collections.`

### `conversions` — List House Conversions

```bash
cyb> conversions
```

Lists all house conversion rules that have been defined.

**Example output:**
```text
House Conversions (3 rules):
  1. 1 stick butter = 113 g
  2. 1 cup flour = 120 g
  3. 1 cup sugar = 200 g
```

**If no conversions defined:**
```text
No house conversions defined. Use 'conversion add' to add one.
```

### `conversion add` — Add a House Conversion

```bash
cyb> conversion add
```

Interactively prompts the user to define a new house conversion rule.

**Example interaction:**
```text
cyb> conversion add
Add House Conversion
From amount: 1
From unit: stick
Ingredient (or 'any'): butter
To amount: 113
To unit: g

Added: 1 stick butter = 113 g
```

The `Ingredient` field allows ingredient-specific conversions (e.g., 1 cup flour vs 1 cup sugar weigh differently). Use `any` for universal conversions.

**Conversion rule identifiers:** Each rule has a unique identifier formed by `{from-unit} {ingredient}` (e.g., `stick butter`, `cup flour`). For universal conversions, the identifier is `{from-unit} any` (e.g., `tbsp any`).

**Error handling:**
- Invalid numbers: `Invalid amount. Please enter a number.`
- Duplicate rule: `A conversion for 'stick butter' already exists. Remove it first to replace.`

### `conversion remove <rule>` — Remove a House Conversion

```bash
cyb> conversion remove "stick butter"
```

Removes a house conversion rule by its identifier.

**On success:**
```text
Removed conversion: 1 stick butter = 113 g
```

**Examples:**
- `conversion remove "stick butter"` — removes the ingredient-specific rule for stick of butter
- `conversion remove "tbsp any"` — removes a universal tablespoon conversion

**Error handling:**
- Rule not found: `No conversion found for 'stick butter'. Use 'conversions' to see existing rules.`

---

## Recipe Commands

### `show <recipe>` — Display a Recipe

```bash
cyb> show "Chocolate Chip Cookies"
```

Displays the full recipe: title, servings, all ingredients with quantities, and all instructions. Recipe is looked up by short ID or title (case-insensitive) across all collections. See [Ambiguous Match Format](/assignments/cyb5-service-architecture#ambiguous-match-format) for lookup details.

**Example output:**
```text
═══════════════════════════════════════
  Chocolate Chip Cookies
  Serves 24 cookies
═══════════════════════════════════════

Ingredients:
  • 2 cups flour
  • 1 cup sugar
  • 1/2 cup butter, softened
  • 2 eggs
  • 1 tsp vanilla extract
  • chocolate chips to taste

Instructions:
  1. Preheat oven to 350°F
  2. Mix dry ingredients
  3. Cream butter and sugar
  4. Combine and fold in chocolate chips
  5. Bake for 12 minutes
```

**Error handling:**
- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes by ingredient.`
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#ambiguous-match-format)

### `search <ingredient>` — Search Recipes by Ingredient

```bash
cyb> search chicken
```

Finds all recipes containing the specified ingredient (case-insensitive substring matching). Searches `RecipeRepository` only — does not separately iterate `RecipeCollectionRepository`.

**Example output:**
```text
Recipes containing 'chicken':
  1. Chicken Tikka Masala         (Joy of Cooking)
  2. Grilled Chicken Salad        (Holiday Favorites)
  3. Chicken Noodle Soup          (Budget Bytes)

Found 3 recipes.
```

**When no results:** `No recipes found containing 'artichoke'.`

### `import json <file> <collection>` — Import Recipe from JSON

```bash
cyb> import json /path/to/recipe.json "Holiday Favorites"
```

Imports a recipe from a JSON file and adds it to the specified collection. The JSON format is the same as A4/A5 (the handout provides the deserializer).

**On success:**
```text
Imported 'Grandma's Apple Pie' into 'Holiday Favorites'.
```

**Error handling:**
- File not found or unreadable: Display the error message from `ImportException`
- Collection not found: Display a helpful message suggesting the `collections` command
- Parse/format errors: Display the error message from the exception

### `delete <recipe>` — Delete a Recipe

```bash
cyb> delete "Chocolate Chip Cookies"
```

Deletes the specified recipe from the repository and removes it from all collections that contain it.

**Confirmation required:** `Delete recipe 'Chocolate Chip Cookies'? (y/n):`

**On success:** `Deleted recipe 'Chocolate Chip Cookies'.`

**Error handling:**
- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes by ingredient.`
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#ambiguous-match-format)

---

## Tools Commands

### `scale <recipe> <servings>` — Scale a Recipe

```bash
cyb> scale "Chocolate Chip Cookies" 48
```

Scales the recipe to the target serving size. Displays a side-by-side comparison of original and scaled quantities, then asks whether to save.

**Example interaction:**
```text
cyb> scale "Chocolate Chip Cookies" 48

Scaled 'Chocolate Chip Cookies' to 48 servings (2.0x):
  Ingredient                Original        Scaled
  ─────────────────────────────────────────────────
  flour                     2 cups       →  4 cups
  sugar                     1 cup        →  2 cups
  butter                    1/2 cup      →  1 cup
  eggs                      2            →  4
  vanilla extract           1 tsp        →  2 tsp
  chocolate chips           to taste        to taste

Save scaled recipe? (y/n): y
Saved scaled recipe 'Chocolate Chip Cookies (scaled to 48)'.
```

If the user declines: `Scaling discarded.`

**Requirements:**
- VagueIngredients display unchanged (e.g., "to taste")
- On save: persists the scaled recipe as a new recipe in a collection that contains the original (which collection is implementation-defined and will not be tested)
- If the recipe has no servings: `Cannot scale 'Recipe Name': no serving information available.`

**Error handling:**
- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes.`
- Invalid servings: `Invalid servings. Please provide a positive number.`
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#ambiguous-match-format)

### `convert <recipe> <unit>` — Convert Recipe Units

```bash
cyb> convert "Beef Stew" gram
```

Converts all measured ingredients to the specified unit using the `ConversionRegistry` (which includes house conversion rules). Displays the converted recipe and asks whether to save.

**Example interaction:**
```text
cyb> convert "Beef Stew" gram

Converted 'Beef Stew' to GRAM:
  Ingredient                Original        Converted
  ───────────────────────────────────────────────────
  flour                     2 cups       →  240 g
  butter                    1/2 cup      →  113.5 g
  salt                      to taste        to taste

Save converted recipe? (y/n): y
Saved converted recipe 'Beef Stew (converted to GRAM)'.
```

**Valid unit names:** Any string accepted by `Unit.parse(String s)` — `gram`, `cup`, `tsp`, `tbsp`, `oz`, `lb`, `ml`, `l`, etc.

**Error handling:**
- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes.`
- Invalid unit: `Unknown unit: 'foo'. Valid units include: gram, cup, tsp, tbsp, oz, lb, ml, l.`
- Unsupported conversion: Display the error from `UnsupportedConversionException` — e.g., `Cannot convert 'eggs' (WHOLE) to GRAM: no conversion rule available.`
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#ambiguous-match-format)

### `shopping-list <recipe1> [recipe2] ...` — Generate Shopping List

```bash
cyb> shopping-list "Chocolate Chip Cookies" "Classic Pancakes"
```

Aggregates ingredients across the specified recipes. Uses the same aggregation logic from A4 — ingredients with the same name and unit are combined; incompatible units are listed separately; vague ingredients are deduplicated by name.

**Example output:**
```text
Shopping List (2 recipes):
═══════════════════════════
  Measured Items:
    • 5 cups flour
    • 2 cups sugar
    • 10 tbsp butter
    • 4 eggs
    • 2 tsp vanilla extract
    • 2 cups milk
    • 1 tsp baking powder

  Also needed:
    • salt
    • chocolate chips

Total: 7 measured items, 2 vague items
```

**Error handling:**
- Any recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes by ingredient.`
- Any recipe with multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#ambiguous-match-format). If any argument is ambiguous or not found, the entire command is aborted — no partial shopping list is generated.

### `cook <recipe>` — Interactive Cooking Mode

```bash
cyb> cook "Chocolate Chip Cookies"
```

Enters interactive cooking mode — a step-by-step walkthrough designed for use while actually cooking.

**Example interaction:**
```text
cyb> cook "Chocolate Chip Cookies"

══════════════════════════════════════════
  COOKING: Chocolate Chip Cookies
  Serves 24 cookies
══════════════════════════════════════════

Ingredients:
  • 2 cups flour              • 2 eggs
  • 1 cup sugar               • 1 tsp vanilla extract
  • 1/2 cup butter, softened  • chocolate chips to taste

──────────────────────────────────────────
  Step 1 of 5
──────────────────────────────────────────
  Preheat oven to 350°F

  (no ingredients used in this step)

[next] [prev] [ingredients] [quit]
cook> next

──────────────────────────────────────────
  Step 2 of 5
──────────────────────────────────────────
  Mix dry ingredients

  Uses: 2 cups flour, 1 cup sugar

[next] [prev] [ingredients] [quit]
cook> ingredients

Ingredients:
  • 2 cups flour
  • 1 cup sugar
  • 1/2 cup butter, softened
  • 2 eggs
  • 1 tsp vanilla extract
  • chocolate chips to taste

cook> next
...

──────────────────────────────────────────
  Step 5 of 5
──────────────────────────────────────────
  Bake for 12 minutes

  Uses: chocolate chips to taste

[next] [prev] [ingredients] [quit]
cook> next

  Finished cooking Chocolate Chip Cookies! Enjoy!
```

**Cook mode commands:**

| Command | Action |
|---------|--------|
| `next` or `n` | Advance to next step; on last step, display completion message and exit cook mode |
| `prev` or `p` | Go back to previous step |
| `ingredients` or `i` | Show the full ingredient list |
| `quit` or `q` | Exit cooking mode |

**Requirements:**
- Display one instruction at a time with step number and total count
- Show consumed ingredients for each step — the ingredients referenced by `Instruction.ingredientRefs` (with quantities). If a step has no ingredient refs, show `(no ingredients used in this step)`
- Show the full ingredient list at the start and on demand via `ingredients`
- Pressing `prev` on the first step shows a message that you're already at the beginning
- The prompt changes to `cook>` during cooking mode
- Display available commands as hints at the bottom of each step

### `export <recipe> <file>` — Export Recipe to Markdown

```bash
cyb> export "Chocolate Chip Cookies" /path/to/cookies.md
```

Uses the provided `MarkdownExporter` to export a recipe to a Markdown file.

**On success:** `Exported 'Chocolate Chip Cookies' to /path/to/cookies.md`

**Error handling:**
- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes.`
- File I/O error: Display the error message from the exception
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#ambiguous-match-format)

---

## Example Session

```text
$ java -jar build/libs/cookyourbooks-all.jar

Welcome to CookYourBooks! Type 'help' to get started.

cyb> help

CookYourBooks Commands:
  Library:
    collections                       List all recipe collections
    collection create <name>          Create a personal collection
    recipes <collection>              List recipes in a collection
    conversions                       List house conversion rules
    conversion add                    Add a house conversion rule
    conversion remove <rule>          Remove a house conversion rule

  Recipe:
    show <recipe>                     Display a recipe
    search <ingredient>               Find recipes by ingredient
    import json <file> <collection>   Import recipe from JSON file
    delete <recipe>                   Delete a recipe

  Tools:
    scale <recipe> <servings>         Scale a recipe
    convert <recipe> <unit>           Convert recipe units
    shopping-list <r1> [r2] ...       Generate aggregated shopping list
    cook <recipe>                     Step-by-step cooking mode
    export <recipe> <file>            Export recipe to Markdown

  General:
    help [command]                    Show help (or help for a specific command)
    quit / exit                       Exit CookYourBooks

cyb> collections

Collections:
  1. Holiday Favorites        [Personal]   12 recipes
  2. Joy of Cooking           [Cookbook]     8 recipes
  3. Budget Bytes             [Web]          5 recipes

cyb> recipes "Joy of Cooking"

Joy of Cooking (8 recipes):
  1. Chocolate Chip Cookies          Serves 24 cookies
  2. Classic Pancakes                Serves 4
  3. Beef Stew                       Serves 6
  ...

cyb> cook "Classic Pancakes"

══════════════════════════════════════════
  COOKING: Classic Pancakes
  Serves 4
══════════════════════════════════════════

Ingredients:
  • 1 1/2 cups flour           • 1 egg
  • 1 cup milk                 • 2 tbsp butter, melted
  • 1 tbsp sugar               • 1 tsp baking powder

──────────────────────────────────────────
  Step 1 of 4
──────────────────────────────────────────
  Whisk together flour, sugar, and baking powder in a large bowl.

  Uses: 1 1/2 cups flour, 1 tbsp sugar, 1 tsp baking powder

[next] [prev] [ingredients] [quit]
cook> next

──────────────────────────────────────────
  Step 2 of 4
──────────────────────────────────────────
  In a separate bowl, whisk egg, milk, and melted butter.

  Uses: 1 egg, 1 cup milk, 2 tbsp butter

[next] [prev] [ingredients] [quit]
cook> next

──────────────────────────────────────────
  Step 3 of 4
──────────────────────────────────────────
  Pour wet ingredients into dry and stir until just combined.
  Do not overmix.

  (no ingredients used in this step)

[next] [prev] [ingredients] [quit]
cook> next

──────────────────────────────────────────
  Step 4 of 4
──────────────────────────────────────────
  Cook on a griddle over medium heat until bubbles form,
  then flip. Cook until golden brown.

  (no ingredients used in this step)

[next] [prev] [ingredients] [quit]
cook> next

  Finished cooking Classic Pancakes! Enjoy!

cyb> shopping-list "Classic Pancakes" "Chocolate Chip Cookies"

Shopping List (2 recipes):
═══════════════════════════
  Measured Items:
    • 5 cups flour
    • 2 cups sugar
    • 10 tbsp butter
    • 4 eggs
    • 2 tsp vanilla extract
    • 2 cups milk
    • 1 tsp baking powder

  Also needed:
    • salt
    • chocolate chips

Total: 7 measured items, 2 vague items

cyb> quit
Goodbye!
```
