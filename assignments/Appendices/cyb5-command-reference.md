---
title: "GA1: Command Reference"
sidebar_position: 7
---

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

- When a recipe has no servings information, display `No servings` in place of the servings line. This applies wherever recipe servings are shown: `recipes`, `show`, and `cook` mode header.

**Error handling:**

- Collection not found: `Collection not found: 'Unknown Collection'. Use 'collections' to see available collections.`

---

## Recipe Commands

### `show <recipe>` — Display a Recipe

```bash
cyb> show "Chocolate Chip Cookies"
```

Displays the full recipe: title, servings, all ingredients with quantities, and all instructions. Recipe is looked up by short ID or title (case-insensitive) across all collections. See [Ambiguous Match Format](/assignments/cyb5-service-architecture#631-ambiguous-match-format) for lookup details.

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
  4. Combine and fold in chocolate chip
  5. Bake for 12 minutes
```

**Error handling:**

- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes by ingredient.`
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#631-ambiguous-match-format)

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

Imports a recipe from a JSON file and adds it to the specified collection. The JSON format is the same as A4 (the handout provides the deserializer).

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
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#631-ambiguous-match-format)

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

If the user declines: 

```text
Save scaled recipe? (y/n): n
Scaling discarded.
```

**Requirements:**

- VagueIngredients display unchanged (e.g., "to taste")
- On save: persists the scaled recipe as a new recipe in a collection that contains the original (which collection is implementation-defined and will not be tested)
- If the recipe has no servings: `Cannot scale 'Recipe Name': no serving information available.`

**Error handling:**

- Recipe not found: `Recipe not found: 'Unknown Recipe'. Use 'search' to find recipes.`
- Invalid servings: `Invalid servings. Please provide a positive number.`
- Multiple matches: Display using [ambiguous match format](/assignments/cyb5-service-architecture#631-ambiguous-match-format)

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

  Recipe:
    show <recipe>                     Display a recipe
    search <ingredient>               Find recipes by ingredient
    import json <file> <collection>   Import recipe from JSON file
    delete <recipe>                   Delete a recipe

  Tools:
    scale <recipe> <servings>         Scale a recipe

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

cyb> quit
Goodbye!
```
