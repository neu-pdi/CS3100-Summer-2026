---
title: "Group Assignment 2: Graphical User Interface"
sidebar_position: 6
---


# 1 Overview

In this assignment, you'll build a graphical user interface (GUI) as a second **driving adapter** for CookYourBooks. This GUI will expose the same functionality: manage a recipe library, import recipes and scale ingredients.

**Prerequisites:** This assignment builds on a GA1 sample implementation (provided). In fact, we saw we need to create a new controller for GUIs. You should be familiar with the following

- the `RecipeService` facade given in GA1
- JavaFx as shown in [the GUI lecture](/lecture-notes/l29-gui1)
- MVVM and TestFx in [the MVVM and E2E Testing lecture](/lecture-notes/l30-gui2)


# 2 Learning Objectives

By completing this assignment, you will demonstrate proficiency in:

- Designing a graphical user interface that is reasonably well-put together, functional and user-friendly
- Using the Model-View-ViewModel (MVVM) architecture to create a program with a graphical user interface that is also testing-friendly
- Using JavaFX to build a graphical user interface
- Writing end-to-end tests to test your application when run through the GUI

---

# 3 Provided code

We have provided an implementation of GA1, giving you a fully functional CLI. Additionally we have provided just enough starter code
to launch an empty GUI.

## 3.1 Stub FXML file

We have provided an FXML file, `cyb-view.fxml` to ensure the handout code can launch a GUI. You are free to replace this with your own
FXML file or remove it outright. Make sure the `start` method in `CookYourBooksGUI` is updated to use your FXML once you do so. Otherwise,
no GUI will launch.

## 3.2 New package and stub

We have created a new package `app.cookyourbooks.gui` where you place all of the code related to wiring and running your GUI.

Within that package we also provided a stub controller class, `CookYourBooksGUIController`. The class is a stub in the truest-sense: it is empty.
You will implement your controller in this class. You are free to rename the class, but make sure that name is changed everywhere in the
project. We highly suggest using the `Rename Symbol` option (F2 on keyboard) on the name of the class to make that change everywhere.

## 3.3 Application Wiring

The provided `CookYourBooksGUI` main class creates the repositories and service and launches a very basic GUI. You are responsible for the following:

- Wiring the service to your view-model
- Ensuring the `FXMLLoader` is loading your FXML view
- Wiring the view-model to your controller

```java
public class CookYourBooksGUI extends Application {
  public void start(Stage stage) throws Exception {
    Path libraryPath = Path.of("cyb-library.json");
    CybLibrary library = CybLibrary.load(libraryPath);
    RecipeRepository recipeRepo = library.getRecipeRepository();
    RecipeCollectionRepository collRepo = library.getCollectionRepository();
    RecipeService recipeService = new RecipeServiceImpl(recipeRepo, collRepo);
    RecipeServiceViewModel serviceViewModel = 
      new RecipeServiceViewModelImpl(recipeService);

    FXMLLoader fxmlLoader = getFxmlLoader("cyb-view.fxml");
    Scene scene = new Scene(fxmlLoader.load());
    CookYourBooksGUIController controller = 
      (CookYourBooksGUIController) fxmlLoader.getController();
    controller.setViewModel(serviceViewModel);

    stage.setTitle("CookYourBooks");
    stage.setScene(scene);
    stage.show();
  }

  private FXMLLoader getFxmlLoader(String fxmlPath) {
    return new FXMLLoader(
        Objects.requireNonNull(
            CookYourBooksGUI.class.getClassLoader().getResource(fxmlPath),
            "Cannot find resource: " + fxmlPath));
  }

  public static void main(String[] args) {
    launch(args);
  }
}
```

## 3.4 How to run

You can run the CookYourBooks application in CLI or GUI mode through Gradle using the following commands: 

| Mode | Gradle Command |
|------|----------------|
| CLI  | `./gradlew cli`  |
| GUI  | `./gradlew gui`  |
| default (gui) | `./gradlew run` |

For the CLI, the formatting will look strange because Gradle insists on printing that it is still running after the
program prints. However, the CLI is indeed reading from `System.in` and processing your commands.

# 4 What to Do

## 4.1 Expected Features

Build a graphical user interface for the CookYourBooks program, starting from the code provided to you. While the choices about layout and behavior are up to you, your graphical user interface should have the following characteristics, and obey the following constraints: 

   1. You must use JavaFX to build your graphical user interface. Code examples from [the GUI lecture](/lecture-notes/l29-gui1) should be useful. You are encouraged to use SceneBuilder to build your GUI visually.

   2. Collection features: The GUI should support the following features:
   
    * List all the recipe collections from the `RecipeCollectionRepository`. At _minimum_, users should see the titles of all the collections.
    * Display all recipes within a collection. How you display all the recipes (e.g. titles only, entire recipe details, only selected collections, hierarchical view) is up to you.
    * Create a new recipe collection.

   3. Recipe features: The GUI should support the following features:
   
    * Search recipes that have a specific ingredient.
    * Show the details of a specific recipe. The recipe can either be explicitly specified, or be selected from a displayed list or the results of the above operation.
    * Scale a specific recipe for a specified number of servings. The recipe to be scaled can either be explicitly specified, or be selected from a displayed list or the results of the above operation.
    * Import a recipe from a json file, so that it shows up in subsequent search results. The imported recipe must be added to a collection specified by the user.
    * Delete a specific recipe. A deleted recipe should no longer show up in any subsequently displayed list or search result, unless it is imported back in.

   4. Any error conditions should be suitably displayed to the user, through pop-up messages or clearly visible text as appropriate. Under no circumstances should an operation result in the program crashing. For example, searching for recipes with a blank string or scaling a recipe with no servings should not crash the program but _must_ display a visible user-friendly error.

   5. Each user interaction or user input must be reasonably user-friendly. Examples that show undesirable usability are (but not limited to):
        
    * Forcing the user to type in the path to a file
    * Forcing the user to provide an input in an error-prone way, when there is a better way that is possible (selecting from a list rather than typing).

       Examples of desirable usability are (but not limited to):
    
    * Menu bars with menu items (e.g. File menu)
    * Buttons that clearly state their purpose
    * Pop-up windows with clear context and instruction to enter values
    
       We do not expect snazzy, sophisticated user-friendly programs. Our standard is: can a user unfamiliar with your code and technical documentation operate the program correctly **without reading your code and technical documentation.**

   6. The GUI should be reasonably proportioned and labeled. Use text labels to clearly indicate what input is expected. Gray out widgets that the user should not be allowed to use at specific points in time (if applicable). Weirdly sized regions, text that is hard to read, unbalanced GUI layout will all cause point deductions.

   7. The GUI should specify suitable accessible text for all widgets appropriately.

   8. Your GUI should not look or feel like a "CLI in a window". An example of this would be a window with a text field for the user to type in the CLI command, a sequence of pop-up windows to take in one text input at a time, etc.
   
   9. None of this should interfere with the "CLI mode". That is, at any time it should be possible to run the application successfully in the cli mode. See [How to Run](#34-how-to-run) for details on how to run your application in CLI or GUI mode. We have already setup Gradle to allow you to do this.

You are allowed to use any widgets from JavaFX exposed in SceneBuilder in your GUI. Below we will briefly explain some widgets you might find helpful for this assignment. We recommend the following for more JavaFX documentation on these and other widgets. 

- [the official OpenJavaFX documentation](https://openjfx.io/javadoc/21/)
- [collection of resources and tutorials on Pawtograder discussion board](https://app.pawtograder.com/course/554/discussion/8137)

We highly suggest drafting a prototype GUI as a team on a whiteboard or on paper. This allows you all to decide on the following before splitting work:

- the `fx:id` and type of each widget
- any methods in your controller you need to expose as event handlers
- the fully qualified name of your controller (the _really long_ name that will start with `app.cookyourbooks.` and end with your controller's class name)

Make sure to consider at least one other alternative for exposing your features in your GUI. Not only will you reflect on this in your [Reflection](#8-reflection), by considering even an unlikely alternative, you strengthen the argument for your final decision.

### 4.1.1 Dialogs in JavaFX

Sometimes, programs with GUIs open up small windows to either notify the user or ask for some input. These are called `Dialog`s. In JavaFx, `Dialog` is generic, meaning it is `Dialog<R>`. The type parameter `R` represents the data you retrieve from the `Dialog`.

This assignment covers the three dialog types that may help you. If you wish to create your own `Dialog`, please read the [`Dialog` JavaFX documentation](https://openjfx.io/javadoc/21/javafx.controls/javafx/scene/control/Dialog.html) and heed its warnings.

#### `Alert` for notifications and errors

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
#### `TextInputDialogs` for contextual text

`TextInputDialog` represents a pop-up window with a `TextField` and a confirmation button.

```java
// This type of Dialog always returns String data
Dialog<String> nameDialog = new TextInputDialog();

// This text will appear on the window to give context.
nameDialog.setContextText("What is your name?"); 

// We can access the accessible text and give it a meaningful description
nameDialog.getEditor().accessibleText().set("Field to enter name");

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

#### `ChoiceDialog` for choosing from a fixed list

`ChoiceDialog` creates a pop-up window with a `ComboBox` and a confirmation button. Unlike `TextInputDialog`, `ChoiceDialog` is fully generic,
so you can get any data type you wish. You can also get properties for the list of items used for the dialog and the selected item. See
[the documentation for `ChoiceDialog`](https://openjfx.io/javadoc/21/javafx.controls/javafx/scene/control/ChoiceDialog.html) for all methods.

```java
// First element is the selected default item, the rest are
// the possible options
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
### 4.1.2 `FileChooser` in JavaFX

When applications with GUIs ask users to load a file, they usually open a window like Finder or Explorer. In JavaFX, this is the `FileChooser`. Unlike `Dialog`s, which can be launched with no other information, `FileChooser` needs a reference to the main `Stage` of your application. In exchange, you get the
actual `File` object the user selected (see [the `File` documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/File.html) for information on getting a `Path` from the object or any necessary operations).

Below is a small snippet of what we can do with a `FileChooser`. 
See [the documentation of `FileChooser`](https://openjfx.io/javadoc/21/javafx.graphics/javafx/stage/FileChooser.html)
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

The test suite is exactly the same as the previous assignment, meaning it only tests the CLI. This allows you to quickly check if the CLI is still working
as you implement your GUI.

Since this assignment requires you to design your own GUI and view-model, we cannot reasonably provide you with any new tests. You are expected to test your GUI
and related code yourself. While **comprehensive** testing of graphical user interfaces is beyond the scope of this assignment, you are expected to test the following aspects:

* Is the correct action taken by the domain when the appropriate user input is given?
* Is the wiring correct (e.g. is/are the correct method(s) called from your action handlers in your model/view-model)?
* At least one end-to-end test using TestFX, the required test being the user journey we describe in [Required E2E Testing](#52-required-e2e-testing)

All of your tests for the GUI must belong in `src/test/app/cookyourbooks/gui`. We have provided a very bare skeleton class `CookYourBooksGUITest` for your E2E tests.

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

E2E tests are most useful for complete user journeys. For this assignment, you are required to write one E2E test for the following journey that exercises a good amount of your expected operations.

**User journey: Scale a recipe within a collection**

For setup, make sure you have already created a collection with at least three recipes, each with non-null servings and then perform the following,
asserting the state of the model is correct after each user action

1. User starts the application with the GUI (no user action required)
2. User selects a `RecipeCollection` from the `RecipeCollectionRepository`
3. User selects a `Recipe` from the chosen collection
4. Scale the recipe to 2x its servings and display it

**Hint**: If you have `TextField`s, you will need to tell TestFx to write text. Below is an example code snippet to to do just that.

```java
// Recall findByAccessibleText is a method we created in the GUI lecture
TextField nameField = findByAccessibleText("Field to enter name");
clickOn(nameField);
write("My name");

// Accessible option to confirm the text.
// Useful if this is a dialog window
type("KeyCode.ENTER");
```

You may find the [TestFx documentation](https://testfx.github.io/TestFX/docs/javadoc/testfx-core/javadoc/org.testfx/org/testfx/api/FxRobot.html) helpful. Note the link sends you to a class called `FxRobot`. This is actually the **superclass** of the `ApplicationTest` class you extend to write your E2E tests. Therefore the methods in this class are exactly the methods you would call to interact with your GUI.

## 5.3 Setup for manual testing

Unlike prior assignments, graders will need to manually use your GUI to test functionality. To assist them in grading and you in anticipating what they will see,
we have provided a `grading-test-library.json` file. Remember that the `CybLibrary` persists with every operation, so any changes made with your GUI _will edit_ the backing JSON file. 

With that in mind, we suggest copying this file and renaming the copy to `cyb-library.json`. The GUI and CLI both know to look for this file without any changes to the code. Then if you want to do a fresh run, you can always make a new copy.

# 6 AI Policy

AI coding assistants are encouraged. In this assignment AI should be helpful in the following ways:

1. Explore ways in which your CLI and GUI code co-exist harmoniously (e.g. they do not duplicate code).
2. Identify the appropriate GUI widgets for each task. JavaFx has many widgets. While we showed you some earlier, it can help to narrow down possible widgets
for certain operations. AI can assist in helping you navigate that space. Combine that with the resources mentioned earlier to get previews of these
widgets and evaluate whether those suggestions are valid for your design choices.
3. Assist with writing E2E tests. As always, make sure you describe the tasks and contexts clearly. You will need to evaluate that
the given test is using proper accessibility text to get the correct widgets in your GUI.


# 7 Expectation of Group Work

We expect all group members to contribute equitably in the project. We highly recommend using branching, code reviews and pull requests for these assignments. 

Specifically, we expect:

* Each group member to file at least one pull request (PR) in the Git repo
* Each group member to place at least one comment on a PR that they did not file.

We will be verifying this during grading.

Please see the [previous assignment description](/assignments/cyb5-service-architecture#7-expectation-of-group-work) for details on how to file and work with PRs. 


# 8 Reflection

**Do not use AI to write your reflection.** Your answers must be your own.

Update `REFLECTION.md` to address:

1. **Design of GUI:** How did the group converge upon the design (layout) of the GUI? Provide at least one example of an operation for which multiple alternatives in the GUI were considered and one was chosen.

2. **Group Contributions:** For each group member, provide at least two bullet points describing how they contributed to the project. As this is part of the reflection for the entire group, we assume some consensus will be reached within the group about this. In case there are differences, we encourage individual group members to reach out to the instructor directly via email. Such emails will not influence the grade for the assignment, except in extreme cases where a group member simply did not contribute.

3. **AI usage:** Which parts of this assignment did you use AI help for? Was AI usage different for each group member (it is OK for this to happen)? If so, specify how each member used AI.

---

# 9 Grading

**Total points: ** 80 pts (58 implementation [44 manual + 14 for E2E test] + 22 reflection and group contribtion points), minus up to −41 for design quality (floor of 0)

## 9.1 Implementation (58 pts total)

### 9.1.1 Manual Testing (44 pts)

This assignment allows you to decide your own interfaces for the view-model and your own GUI design. Therefore, graders will test
your GUI _manually_. What follows are all the scenarios they will test manually and how much each scenario is worth.

| Scenario | Points |
| ---- | ----- |
| Displays existing collections | 6 |
| Create a collection | 4 |
| Import a recipe from JSON to a collection specified by the user | 8 |
| Search for a recipe with an ingredient known in one recipe | 4 |
| Search for a recipe with an ingredient in no recipe (points possible if UI disallows this) | 2 |
| Select a recipe in a collection and see its full details | 4 |
| Scale a recipe for a larger number of servings | 4 |
| Scale a recipe for a smaller but valid number of servings | 2 |
| Cause an error in the GUI to see how errors are displayed (points possible if UI disallows this) | 4 |
| Delete a recipe and check it no longer appears in any collection | 4 |
| Delete a recipe and check it no longer appears in a search | 2 |

### 9.1.2 E2E Test (14 pts)

You are required to write at least one E2E test as specified in [Required E2E Testing](#52-required-e2e-testing). Grading will be split between seeing the test perform specific actions and the test verifying expected behaviors for each action.

| Test Action | Points |
| ---- | ----- |
| Test selects a RecipeCollection | 2 |
| Test selects a Recipe from the chosen collection and it displays | 2 |
| Test scales the recipe to 2x its servings | 3 |

| Test Verification | Points |
| ---- | ----- |
| Assert the correct collection was selected.| 2 |
| Assert the correct recipe is chosen | 2 |
| Assert the recipe is correctly scaled | 3 |

## 9.2 Design Quality (up to -41)

### 9.2.1 User Interface Design (up to -24)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| GUI acts as CLI | -24 | GUI is a visual CLI (e.g. user types in CLI commands into a `TextField`) |
| Missing accessibility text for widgets | -2 each (up to -6) | Buttons without accessible text _and_ unclear text, `ListView`s or other widgets without accessibleText describing purpose |
| Non-user friendly design | -3 per feature this applies to (up to -24) | User needs advance knowledge of CYB to use a feature |

### 9.2.2 View-Model and Controller Design (up to -12)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| View-model is aware of JavaFX widgets | -5 | View-model should not be aware of view directly |
| View-model is aware of controller | -3 | View-model should not be aware of the controller |
| Recipe class was modified for view purposes | -3 | Domain core should not be aware of JavaFX |
| RecipeCollection class was modified for view purposes | -3 | Domain core should not be aware of JavaFX |

### 9.2.3 Code Quality (up to −5)

| Issue | Max Deduction | Description |
|-------|---------------|-------------|
| Poor error messages | −2 | Generic errors without actionable guidance |
| Missing Javadoc | −2 | Public classes and methods lack documentation |
| Poor naming/style | −1 | Unclear variable names; inconsistent formatting |

## 9.3 Reflections (12 pts)

3 questions × 4 points each. See [Reflection](#8-reflection) for full prompts. Answers should demonstrate genuine reflection on your design process, not just describe what you built.

## 9.4 Evidence of Group Work (10 points)

This part will be graded for each member individually. These are the same requirements listed [in the Expectation of Group Work section](#7-expectation-of-group-work).

* At least one PR per group member: 5 points
* At least one comment with a code review on a PR filed by another group member: 5 points
