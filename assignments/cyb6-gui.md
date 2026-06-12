---
title: "Group Assignment 2: JavaFX GUI"
sidebar_position: 6
---


# 1 Overview

In this assignment, you'll build a graphical user interface for CookYourBooks to augment the CLI that you created previously. This GUI will expose the same functionality: manage a recipe library, import recipes and scale ingredients.


**Prerequisites:** This assignment builds on the handout code from GA1 as this assignment does not need a CLI. In fact, we saw we need to create a new controller for GUIs. You should be familiar with TODO.


# 2 Learning Objectives

By completing this assignment, you will demonstrate proficiency in:

- Designing a graphical user interface that is reasonably well-put together, functional and user-friendly
- Using the Model-View-ViewModel (MVVM) architecture to create a program with a graphical user interface that is also testing-friendly
- Using JavaFX to build a graphical user interface
- Writing end-to-end tests to test your application when run through the GUI

---

# 3 Provided code

TODO

# 4 What to Do

## 4.1 Expected Features

Build a graphical user interface for the CookYourBooks program, starting from the code provided to you. While the choices about layout and behavior are up to you, your graphical user interface should have the following characteristics, and obey the following constraints: 

   1. You must use JavaFX to build your graphical user interface. Code examples from lecture should be useful. You are encouraged to use SceneBuilder to build your GUI visually.

   2. Collection features: The GUI should support the following features:
   
    * List all the recipe collections from the `RecipeCollectionRepository`
    * Display all recipes within a collection
    * Create a new recipe collection.

   3. Recipe features: The GUI should support the following features:
   
    * Search recipes that have a specific ingredient.
    * Show the details of a specific recipe. The recipe can either be explicitly specified, or be selected from a displayed list or the results of the above operation.
    * Scale a specific recipe for a specified number of servings. The recipe to be scaled can either be explicitly specified, or be selected from a displayed list or the results of the above operation.
    * Import a recipe from a json file, so that it shows up in subsequent search results. Optionally, add an imported recipe in a specified collection.
    * Delete a specific recipe. A deleted recipe should no longer show up in any subsequently displayed list or search result, unless it is imported back in.

   4. Any error conditions should be suitably displayed to the user, through pop-up messages or clearly visible text as appropriate. Under no circumstances should an operation result in the program crashing.

   5. Each user interaction or user input must be reasonably user-friendly. Examples that show undesirable usability are (but not limited to):
        
    * Forcing the user to type in the path to a file
    * Forcing the user to provide an input in an error-prone way, when there is a better way that is possible (selecting from a list rather than typing).
    
   We do not expect snazzy, sophisticated user-friendly programs. Our standard is: can a user unfamiliar with your code and technical documentation operate the program correctly **without reading your code and technical documentation?**
   6. The GUI should be reasonably proportioned and labeled. Use text labels to clearly indicate what input is expected. Gray out widgets that the user should not be allowed to use at specific points in time (if applicable). Weirdly sized regions, text that is hard to read, unbalanced GUI layout will all cause point deductions.
   7. The GUI should specify suitable accessible text for all widgets appropriately.
   8. Your GUI should not look or feel like a "CLI in a window". An example of this would be a window with a text field for the user to type in the CLI command, a sequence of pop-up windows to take in one text input at a time, etc.
   9. None of this should interfere with the "CLI mode". That is, at any time it should be possible to run the application successfully in the cli mode. See [the Gradle setup](#6-gradle-setup) for details on how to make run your application in CLI or GUI mode.

We recommend the following for more JavaFX documentation

- [the official OpenJavaFX documentation](https://openjfx.io/javadoc/21/)
- [collection of resources and tutorials on Pawtograder discussion board](https://app.pawtograder.com/course/554/discussion/8137)

We highly suggest drafting a prototype GUI as a team on a whiteboard or on paper. This allows you all to decide on the following before splitting work:

- the `fx:id` and type of each widget
- any methods in your controller you need to expose as event handlers
- the fully qualified name of your controller (the _really long_ name that will start with `app.cookyourbooks.` and end with your controller's class name)

Make sure to consider at least one other alternative for exposing your features in your GUI. Not only will you reflect on this in your [Reflection](#9-reflection), by considering even an unlikely alternative, you strengthen the argument for your final decision.

### 4.1.1 Dialogs in JavaFX

Sometimes, programs with GUIs open up small windows to either notify the user or ask for some input. These are called `Dialog`s. In JavaFx, `Dialog` is generic, meaning it is `Dialog<R>`. The type parameter `R` represents the data you retrieve from the `Dialog`.

This assignment covers the three dialog types that may help you. If you wish to create your own `Dialog`, please read the [`Dialog` JavaFX documentation](https://openjfx.io/javadoc/21/javafx.controls/javafx/scene/control/Dialog.html) and heed its warnings.

#### Alert for notifications and errors

`Alert` represents a simple notification window. When creating an `Alert`, you need to decide on the type of alert. The types are defined in the enum `AlertType`

| `AlertType` value | Purpose |
| ----------------- | ---------- |
| CONFIRMATION | Get confirmation from the user |
| ERROR | Show the user an error |
| INFORMATION | Show the user some information |
| NONE | Basically an empty/default alert window |
| WARNING | Show the user a warning |

```java
Dialog<ButtonType> errWindow = new Alert(AlertType.ERROR, "Something has gone wrong!");

// After this method, the alert pops up. 
// The user must click or close the error window.
// Then the program will continue.
errWindow.showAndWait();
```
#### TextInputDialogs for contextual text

`TextInputDialog` represents a pop-up window with a `TextField` and a confirmation button.

```java
// This type of Dialog always returns String data
Dialog<String> nameDialog = new TextInputDialog();

// This text will appear on the window to give context.
nameDialog.setContextText("What is your name?"); 

// Window now pops up, takes focus, and stops execution of the program. 
// User MUST interact with the dialog to continue execution.
// Users can either close the window or enter text and hit the confirmation button.
// In the latter case, showAndWait returns the text they input.
Optional<String> result = nameDialog.showAndWait(); 
if (result.isPresent()) {
    String name = result.get();
    ...
}
```

#### ChoiceDialog for choosing from a fixed list

`ChoiceDialog` creates a pop-up window with a `ComboBox` and a confirmation button. Unlike `TextInputDialog`, `ChoiceDialog` is fully generic,
so you can get any data type you wish. You can also get properties for the list of items used for the dialog and the selected item. See
[the documentation for `ChoiceDialog`](https://openjfx.io/javadoc/21/javafx.controls/javafx/scene/control/ChoiceDialog.html) for all methods.

```java
Dialog<Integer> numberDialog = new ChoiceDialog(0, 0, 1, 2, 3);

// This text will appear on the window to give context.
numberDialog.setContextText("Pick your favorite number."); 

// Window now pops up, takes focus, and stops execution of the program. 
// User MUST interact with the dialog to continue execution.
// Users can either close the window or pick a number and hit the confirmation button.
// Here, we are using this to detect if the user DID select something
Optional<Integer> result = numberDialog.showAndWait(); 
if (result.isPresent()) {
    // Grab the number they selected
    int number = numberDialog.getSelectedItem();
    ...
}
```
### 4.1.2 FileChooser in JavaFX

When applications with GUIs ask users to load a file, they usually open a window like Finder or Explorer. In JavaFX, this is the `FileChooser`. Unlike `Dialog`s, which can be launched with no other information, `FileChooser` needs a reference to the main `Stage` of your application. In exchange, you get the
actual `File` object the user selected (see [the `File` documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/File.html) for information on getting a `Path` from the object or any necessary operations).

Below is a small snippet of what we can do with a `FileChooser`. 
See [the documentation of `FileChooser](https://openjfx.io/javadoc/21/javafx.graphics/javafx/stage/FileChooser.html)
for more information on its methods and what it can do.

```java
Stage stage = ...; //The main window object
FileChooser chooser = new FileChooser();

// We want to only see files with the JSON extension
fileChooser.getExtensions().addAll(new ExtensionFilter("JSON files", "*.json"));

// Open the file chooser right over the main window of the app
// The program is now focused on the FileChooser until the user closes
// the FileChooser or selects a file.
File selectedFile = fileChooser.showOpenDialog(stage);
if (selectedFile != null) { // null means they closed the window
    // Do something with this file
}
```

### 4.1.3 TextAreas for showing a lot of text

Sometimes you will want to show someone a lot of text (like a recipe). We can use a `TextArea` for this purpose. A `TextArea` is a scrollable, larger version
of `TextField`. See the [`TextArea` documentation](https://openjfx.io/javadoc/21/javafx.controls/javafx/scene/control/TextArea.html) for more details.

```java
TextArea area = new TextArea();

// Disallow text to be wrapped around
area.setWrapText(false);

// Prevent the user from editing the text
area.setEditable(false);

// We can set the text to whatever String we like
area.setText("Hello there.\nHow was your day?\n\t[ ] Good.\n\t[ ] Could be better.");
```

There are other options like using `Label`s or drawing `Text`. The former is better when you know the amount of space the text needs to fill. The former involves a little know-how on how to place the text and handle font sizing.

## 4.2 View and controller
 
Carefully design the interaction between the GUI and a controller. We recommend implementing a view-model as well.

Remember a view-model interface defines **what state must be accessible** and **what commands must be supported**. 

Your view-model interface should include:
- **Observable properties** (`ObservableList`, `ObjectProperty`, `BooleanProperty`, `StringProperty`, etc.) for JavaFX binding in the View
- **Commands** (void methods) for user actions
- **Non-JavaFX accessors** for clean tests — plain Java getters that return `String`, `List<String>`, `boolean`, etc., so tests can verify state without depending on JavaFX types

### 4.2.1 Loose coupling between view-model, controller, and view

JavaFX does create some coupling between the view and the controller

- `@FXML` annotations on controller methods used as event handlers in the FXML view
- `@FXML` annotations on fields representing widgets in the FXML view
- Those fields must have the same name as the `fx:id` in the FXML view

However, that should be all the coupling required.

- view-model should have no knowledge of the controller object or its fields
- view-model should have no knowledge of the layout of the view or its components
- view should not be aware of the view-model at all

# 5 Testing

While **comprehensive** testing of graphical user interfaces is beyond the scope of this assignment, you are expected to test the following aspects:

* Is the correct action taken by the domain when the appropriate user input is given?
* Is the wiring correct (e.g. is/are the correct method(s) called from your action handlers in your model/view-model)?
* At least one end-to-end test using TestFX, the required test being the user journey we describe in [Required E2E Testing](#required-e2e-testing)

## 5.1 Testing your view-model

Recall we can unit test view-models to ensure the wiring from commands to view-model to domain objects are working.
Below we give an exaxmple of an example test of a view-model. The constructor and methods shown are merely examples: your view-model may be different and still well designed.

```java
@Test
void selectCollection_updatesRecipeList() {
    // Arrange — inject mock services via constructor
    RecipeServiceViewModel vm = new RecipeServiceModelImpl(mockRecipeService, mockCollRepo);

    // Act
    vm.selectCollection("desserts-id");

    // Assert — use non-JavaFX accessors for clean assertions
    assertThat(vm.getSelectedCollectionId()).isEqualTo("desserts-id");
    assertThat(vm.getRecipeIdsInSelectedCollection()).hasSize(5);
}
```

## 5.2 Required E2E Testing

E2E tests are most useful for complete user journeys. For this assignment, you are required to write one E2E tests for the following journey that exercises a good amount of your expected operations.

**User journey: Scale a recipe within a collection**

For setup, make sure you have already created a collection with at least three recipes, each with non-null servings:

1. User starts the application with the GUI
2. User selects a RecipeCollection from the RecipeCollectionRepository
3. User selects a Recipe from the chosen collection
4. Scale the recipe to 2x its servings
5. Save it to the chosen collection
6. Verify the new recipe was indeed saved to that collection

## 5.3 Setup for manual testing

Unlike prior assignments, graders will need to manual use your GUI to test functionality. To assist them, you must set up your program, so that when it is run, it starts in the following state:

- at least 2 distinct recipe collections
- at least 4 different recipes split between the collections
    - at least one different ingredient must appear in each recipe
    - at least one recipe needs a non-null serving amount

By populating the model ahead of time with this dummy data, graders can check features like scaling without relying on importing from JSON working in your GUI.

# 6 Gradle Setup

You can augment the `build.gradle` file so that you can run the CLI version and the GUI version of the application using different gradle tasks. Specifically, add to the `build.gradle` file following the template below:

```java

application {
    mainClass = "full packaged path to the class that has the main method for cli"
}

def requestedTasks = gradle.startParameter.taskNames

tasks.named("run", JavaExec).configure {
    if (requestedTasks.any { it == "cli" }) {
        mainClass = "full packaged path to the class that has the main method for cli"
    } else if (requestedTasks.any { it == "gui" }) {
        mainClass = "full packaged path to the class that has the main method for gui"
    }
}

tasks.register("cli") {
    group = "application"
    description = "Shortcut for run CYB in CLI mode"
    dependsOn("run")
}

tasks.register("gui") {
    group = "application"
    description = "Shortcut for run CYB in GUI mode"
    dependsOn("run")
}

```

Then to run the CookYourBooks application: 

| Mode | Gradle Command |
|------|----------------|
| CLI  | ./gradlew cli  |
| GUI  | ./gradlew gui  |
| default (cli) | ./gradlew run |


# 7 AI Policy

AI coding assistants are encouraged. In this assignment AI should be helpful in the following ways:

1. Explore ways in which your CLI and GUI code co-exist harmoniously (e.g. they do not duplicate code).
2. Identify the appropriate GUI widgets for each task.
3. Write E2E tests.


# 8 Expectation of Group Work

We expect all group members to contribute equitably in the project. We highly recommend using branching, code reviews and pull requests for these assignments. 

Specifically, we expect:

* Each group member to file at least one pull request (PR) in the Git repo
* Each group member to place at least one comment on a PR that they did not file.

We will be verifying this during grading.

Please see the [previous assignment description](/assignments/cyb5-service-architecture.md#7-expectation-of-group-work) for details on how to file and work with PRs. 


# 9 Reflection

**Do not use AI to write your reflection.** Your answers must be your own.

Update `REFLECTION.md` to address:

1. **Design of GUI:** How did the group converge upon the design (layout) of the GUI? Provide at least one example of an operation for which multiple alternatives in the GUI were considered and one was chosen.

2. **Group Contributions:** For each group member, provide at least two bullet points describing how they contributed to the project. As this is part of the reflection for the entire group, we assume some consensus will be reached within the group about this. In case there are differences, we encourage individual group members to reach out to the instructor directly via email. Such emails will not influence the grade for the assignment, except in extreme cases where a group member simply did not contribute.

3. **AI usage:** Which parts of this assignment did you use AI help for? Was AI usage different for each group member (its OK for this to happen)? If so, specify how each member used AI.

---

# 10 Grading

**Total points: ** 76 pts

## 10.1 Manual Testing (44 pts)

This assignment allows you to decide your own interfaces for the view-model and your own GUI design. Therefore, graders will test
your GUI _manually_. What follows are all the scenarios they will test manually and how much each is worth

| Scenario | Points |
| ---- | ----- |
| Create a collection | 4 |
| Import a recipe using JSON | 4 |
| Add the imported recipe to a collection | 2 |
| Search for a recipe with an ingredient known in one recipe | 4 |
| Search for a recipe with an ingredient in no recipe (points possible if UI disallows this) | 2 |
| Select a recipe in a collection and see its full details | 4 |
| Scale a recipe for a larger number of servings | 4 |
| Scale a recipe for a smaller but valid number of servings | 4 |
| Save a scaled recipe to a collection | 2 |
| Choose NOT to save a scaled recipe to a collection | 2 |
| Cause an error in the GUI to see how errors are displayed | 4 |
| Delete a recipe and check it no longer appears in any collection | 4 |
| Delete a recipe and check it no longer appears in a search | 4 |

## 10.2 E2E Test (20 pts)

You are required to write at least one E2E test as specified in [Required E2E Testing](#52-required-e2e-testing). Grading will be split between seeing the test perform specific actions and the test verifying expected behaviors for each action.

| Test Action | Points |
| ---- | ----- |
| Test selects a RecipeCollection | 2 |
| Test selects a Recipe from the chosen collection and it displays | 2 |
| Test scales the recipe to 2x its servings | 2 |
| Test saves it to the chosen collection | 2 |

| Test Verification | Points |
| ---- | ----- |
| Assert the correct collection was selected.| 2 |
| Assert the correct recipe is chosen | 2 |
| Assert the correct recipe is displayed | 2 |
| Assert the recipe is correctly scaled | 2 |
| Assert the scaled recipe is displayed | 2 |
| Assert the test saves the recipe to the correct collection | 2 |

## 10.3 User Interface Design (up to -Y)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| GUI acts as CLI | -Y | User is asked to enter CLI commands at any point |
| Invalid recipe can be input | -Y | User is allowed to select a recipe that does not exist for any command |
| Non-user friendly design | -Y | User needs advance knowledge of CYB to use a feature |

## 10.4 View-Model and Controller Design (up to -Y)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| View-model is aware of JavaFX widgets | -Y | View-model should not be aware of view directly |
| View-model is aware of controller | -Y | View-model should not be aware of the controller |
| Recipe class was modified for view purposes | -Y | Domain core should not be aware of JavaFX |
| RecipeCollection class was modified for view purposes | -Y | Domain core should not be aware of JavaFX |

## 10.5 Code Quality (up to −5)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| Poor error messages | −2 | Generic errors without actionable guidance |
| Missing Javadoc | −2 | Public classes and methods lack documentation |
| Poor naming/style | −1 | Unclear variable names; inconsistent formatting |


## 10.6 Reflections

3 questions × 4 points each. See [Reflection](#9-reflection) for full prompts. Answers should demonstrate genuine reflection on your design process, not just describe what you built.
