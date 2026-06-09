---
title: "Assignment 6: JavaFX GUI"
sidebar_position: 6
---


# 1 Overview

In this assignment, you'll build a graphical user interface for CookYourBooks to augment the CLI that you created previously. This GUI will expose the same functionality: manage a recipe library, import recipes and scale ingredients. 


**Prerequisites:** This assignment builds on the A5 sample implementation (provided). You should be familiar with TODO.


# 2 Learning Objectives

By completing this assignment, you will demonstrate proficiency in:

- Designing a graphical user interface that is reasonably well-put together, functional and user-friendly
- Using the Model-View-ViewModel (MVVM) architecture to create a program with a graphical user interface that is also testing-friendly
- Using JavaFX to build a graphical user interface
- Writing end-to-end tests to test your application when run through the GUI

---

# Provided code

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
    * Import a recipe from a json file, so that it shows up in subsequent search results. Optionally, put an imported recipe in a specified collection.
    * Delete a specific recipe. A deleted recipe should no longer show up in any displayed list or search result, unless it is imported back in.

   4. Any error conditions should be suitably displayed to the user, through pop-up messages or clearly visible text as appropriate. Under no circumstances should an operation result in the program crashing.

   5. Each user interaction or user input must be reasonably user-friendly. Examples that show undesirable usability are (but not limited to):
        
    * Forcing the user to type in the path to a file
    * Forcing the user to provide an input in an error-prone way, when there is a better way that is possible (selecting from a list rather than typing).
    
   We do not expect snazzy, sophisticated user-friendly programs. Our standard is: can a user unfamiliar with your code and technical documentation operate the program correctly **without reading your code and technical documentation?**
   6. The GUI should be reasonably proportioned and labeled. Use text labels to clearly indicate what input is expected. Gray out widgets that the user should not be allowed to use at specific points in time (if applicable). Weirdly sized regions, text that is hard to read, unbalanced GUI layout will all cause point deductions.
   7. The GUI should specify suitable accessible text for all widgets appropriately.
   8. None of this should interfere with the "CLI mode". That is, at any time it should be possible to run the application successfully in the cli mode. See below for details.
 

## 4.2 View, controller and testability
 
Carefully design the interaction between the GUI and a controller. You may choose to implement a view-model.

While comprehensive testing of graphical user interfaces is beyond the scope of this assignment, you are expected to test the following aspects:

* Is the correct action taken by the domain when the appropriate user input is given?
* Is the wiring correct (e.g. is/are the correct method(s) called from your action handlers in your model/view-model)?
* At least one end-to-end test using TestFX. Pick one of the above use cases and write an E2E test for it.

# 5 Gradle Setup

You can augment the `build.gradle` file so that you can run the CLI version and the GUI version of the application using different gradle tasks. Specifically, add to the `build.gradle` file following the template below:

```java

application {
    mainClass = "full packaged path to the class that has the main method for cli"
}

def requestedTasks = gradle.startParameter.taskNames

tasks.named("run", JavaExec).configure {
    if (requestedTasks.any { it == "cli" || it.endsWith(":echotextMvc") }) {
        mainClass = "full packaged path to the class that has the main method for cli"
    } else if (requestedTasks.any { it == "gui" || it.endsWith(":sceneitallApp") }) {
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


# 6 AI Policy

AI coding assistants are encouraged. In this assignment AI should be helpful in the following ways:

1. Explore ways in which your CLI and GUI code co-exist harmoniously (e.g. they do not duplicate code).
2. Identify the appropriate GUI widgets for each task.
3. Write E2E tests.


# 7 Expectation of Group Work

We expect all group members to contribute equitably in the project. We highly recommend using branching, code reviews and pull requests for these assignments. Specifically, we expect:

* Each group member to file at least one pull request (PR) in the Git repo
* Each group member to place at least one comment on a PR that they did not file.

We will be verifying this during grading.


Please see the previous assignment description for details on how to file and work with PRs. 


# 8 Reflection

**Do not use AI to write your reflection.** Your answers must be your own.

Update `REFLECTION.md` to address:

1. **Design of GUI:** How did the group converge upon the design (layout) of the GUI? Provide at least one example of an operation for which multiple alternatives in the GUI were considered and one was chosen. 

2. **Group Contributions:** For each group member, provide at least two bullet points describing how they contributed to the project. As this is part of the reflection for the entire group, we assume some consensus will be reached within the group about this. In case there are differences, we encourage individual group members to reach out to the instructor directly via email. Such emails will not influence the grade for the assignment, except in extreme cases where a group member simply did not contribute.

3. **AI usage:** Which parts of this assignment did you use AI help for? Was AI usage different for each group member (its OK for this to happen)? If so, specify how each member used AI.

---

# 9 Grading

TODO