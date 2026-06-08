---
sidebar_position: 12
image: /img/labs/web/lab12.png
---

## Learning Objectives

- Use Scene Builder to visually create an FXML layout
- Wire FXML to a Controller using `fx:id` and `@FXML` annotations
- Implement the MVC pattern with pre-built SceneItAll Model classes
- Use property binding to synchronize the View with the Model
- Write a ViewModel unit test without starting the JavaFX runtime
- Write an E2E test using TestFX with accessibility-based locators

# 1 Overview

In this lab you will use the SceneItAll domain. The starter code provides the Model classes (`Light`, `Fan`, `Shade`, `Area`, `Scene`), a ViewModel skeleton, and test scaffolding. You will fill in the View, Controller, and tests.


---

# 2 Part 1: Setup & Pair Formation


## 2.1 Get the starter project

Clone this lab's repository from Pawtograder. This is the codebase you will work on.

The project contains:

| File                                                                 | What it is                                                                                    | What you do with it                                             |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `src/main/java/sceneitall/model/`                                    | Model classes: `Light`, `Fan`, `Shade`, `Area`, `Scene`                                       | **Don't modify.** These are your domain logic.                  |
| **Reference implementation (read, don't modify):**                   |                                                                                               |                                                                 |
| `src/main/java/sceneitall/viewmodel/AreaDashboardViewModel.java`     | Complete ViewModel from GUI lecture — working example with properties, binding, `activateScene()` | **Read as reference.** This is the worked example from lecture. |
| `src/main/java/sceneitall/controller/AreaDashboardController.java`   | Complete Controller from GUI lecture — FXML wiring, initialize, handlers                              | **Read as reference.**                                          |
| `src/main/resources/area-dashboard.fxml`                             | Complete FXML from GUI lecture — the Area Dashboard layout                                            | **Read as reference.** You can run it to see a working app.     |
| `src/test/java/sceneitall/viewmodel/AreaDashboardViewModelTest.java` | Complete ViewModel tests — several examples showing the testing patterns                      | **Read as reference.**                                          |
| `src/test/java/sceneitall/AreaDashboardE2ETest.java`                 | Complete E2E test — TestFX with `findByAccessibleText()`                                      | **Read as reference.**                                          |
| **Your task (pick one, build it):**                                  |                                                                                               |                                                                 |
| `src/main/java/sceneitall/viewmodel/SceneBuilderViewModel.java`      | Skeleton — properties declared, methods are TODOs                                             | **Fill in** command methods                                     |
| `src/main/java/sceneitall/viewmodel/DeviceSetupViewModel.java`       | Skeleton — properties declared, methods are TODOs                                             | **Fill in** command methods                                     |
| `src/main/java/sceneitall/viewmodel/ScheduleViewModel.java`          | Skeleton — properties declared, methods are TODOs                                             | **Fill in** command methods                                     |
| `src/main/java/sceneitall/controller/*Controller.java`               | Empty Controller for each task                                                                | **Pick one, fill in** `@FXML` fields, `initialize()`, bindings  |
| `src/main/resources/*-task.fxml`                                     | Empty FXML for each task                                                                      | **Pick one, build your layout** in Scene Builder                |
| `src/test/java/sceneitall/viewmodel/*ViewModelTest.java`             | Test scaffold for each task — one TODO                                                        | **Write one test**                                              |
| `src/test/java/sceneitall/*E2ETest.java`                             | TestFX scaffold for each task — `start()` pre-wired                                           | **Write one test**                                              |
| **Shared:**                                                          |                                                                                               |                                                                 |
| `src/main/resources/styles.css`                                      | Dark theme (optional)                                                                | Use it or ignore it                                             |
| `src/main/java/sceneitall/SceneItAllApp.java`                        | Application class — loads your chosen FXML (change the path)                                  | **Update FXML path** to point to your task                      |

## 2.3 Use the reference implementation

Before you start building, **run the Area Dashboard** to see what a complete SceneItAll GUI looks like. 

Study how the pieces connect:

- How does `fx:id="brightnessSlider"` in the FXML map to `@FXML private Slider brightnessSlider` in the Controller?
- How does `initialize()` set up the binding?
- How does the ViewModel test call `activateScene()` without any JavaFX widgets?
- How does the E2E test find elements by `accessibleText`?

You are building a **different** task, but the patterns are identical. Use the reference to answer "how do I...?" questions as you work.

## 2.4 Install Scene Builder

Scene Builder is a standalone visual editor for FXML files. You'll use it to build your GUI layout by dragging and dropping components.

1. **Download Scene Builder** from [Gluon](https://gluonhq.com/products/scene-builder/) (free, choose your OS)
2. **Install it** — on macOS, open `.dmg` file and drag Scene Builder to Applications; on Windows, run the installer
3. **Open Scene Builder**, then go to **File → Open** or **Open Project** and select your task's `.fxml` file (e.g., `src/main/resources/scene-builder-task.fxml`)

After editing in Scene Builder, save (`Cmd+S` / `Ctrl+S`) — the FXML file updates in place. Switch back to VS Code to see the changes and write your Controller code.

:::tip AI-Assisted FXML Editing

You can also use **GitHub Copilot** to tweak your FXML files directly — for example, "add a ComboBox below the ListView with fx:id deviceComboBox and accessibleText Select device" or "change the VBox spacing to 12 and add padding." This is sometimes faster than switching between Scene Builder and VS Code for small adjustments.
:::


## 2.5 Running the app

To launch the GUI:

```bash
./gradlew run
```

This starts `SceneItAllApp`, which loads whichever FXML file is set in `SceneItAllApp.java`. By default it loads the Area Dashboard reference implementation. When you start your task, change the `FXML_PATH` constant to point to your task's FXML (e.g., `"/scene-builder-task.fxml"`).

## 2.6 Running the tests

To run all tests (ViewModel tests + E2E tests):

```bash
./gradlew test
```

To run just the ViewModel tests (fast, no GUI window):

```bash
./gradlew test --tests 'sceneitall.viewmodel.*'
```

To run just the E2E tests (launches a GUI window briefly):

```bash
./gradlew test --tests 'sceneitall.*E2ETest'
```

To run a specific test class:

```bash
./gradlew test --tests 'sceneitall.viewmodel.AreaDashboardViewModelTest'
```

## 2.7 Verify your setup

1. Open the project in VS Code
2. Open Scene Builder and use **File → Open** or **Open Project** to open `src/main/resources/area-dashboard.fxml` — you should see the Area Dashboard layout
3. Run `./gradlew run` — you should see a window titled "SceneItAll" with the Area Dashboard
4. Run `./gradlew test` — the reference tests should pass; scaffold tests should pass

:::tip NullAway and `@FXML` fields

`@FXML` fields are injected by `FXMLLoader` at runtime, after the constructor runs — so they look uninitialized to NullAway. The skeleton Controllers handle this with `@NullUnmarked` (from JSpecify) at the top of the class, which tells NullAway that null analysis
doesn't apply here because the framework handles initialization. Copy that pattern in your Controller.

For ViewModel backing-model fields (`area`, `areas`), the skeletons use `@Nullable` from JSpecify, which is accurate — those fields genuinely are null until `setArea()`/`setModel()` is called. When you implement the TODO methods, use `Objects.requireNonNull(area, "Call setArea() first")` to get a non-null local reference NullAway is happy with.
:::

:::tip Known build warnings 

You will see **some warnings** when you build — this is normal:

- **UnusedVariable / UnusedMethod** false positives on `@FXML` fields and `private` handler methods
  (called reflectively by FXMLLoader, so Error Prone can't see the usages)
- **"Unknown module: javafx.graphics"** and **"Unsupported JavaFX configuration"** during tests (harmless TestFX/module-system noise)

None of these indicate a problem with your code.
:::


---

# 3 Part 2: Build Your Area Dashboard

Pick one of the three SceneItAll design tasks below.

:::warning Not Area Dashboard

The Area Dashboard was the running example in the GUI lecture code, for which you have already seen the complete FXML, Controller, ViewModel, and tests for it. Pick a **different** task so you practice applying the patterns yourself, not reproducing lecture code. The lecture example is
there as a reference, not a template to copy.
:::

| Design Task               | What to build                                                                                                | How it differs from the lecture example                                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Scene Builder**         | Interface for creating/editing a Scene — select devices, set target states, name the scene, assign to a room | Multiple device controls in one view, creating a new domain object (`sceneitall.model.Scene`) rather than displaying existing ones. Uses `setArea(Area)` (single area). **Note:** Watch out for the name collision with `javafx.scene.Scene` — use the fully qualified name when both are in scope. |
| **Device Setup**          | Scan for devices, name one, pick a type, assign to a room, save                                              | Validation (device name required, room must be selected), new device added to Model, uses `TextField` and `DeviceType` enum not shown in reference. Uses `setModel(List<Area>)` (multiple rooms). |
| **Schedule & Automation** | Interface for creating automated rules — "at sunset, activate Evening in Living Room"                        | Multiple selection inputs with validation. Uses `setModel(List<Area>)`. **Note:** The model doesn't include scheduling/automation concepts — you'll represent rules as formatted Strings in the ViewModel's `ObservableList<String>` |



## 3.1 Phase A: Build the FXML

Your layout must include **at minimum:**

- A **title label** (e.g., room name or "Add Device")
- One **interactive control** — Slider, ComboBox, Spinner, or ToggleButton
- A **ListView** showing device statuses or scene items
- One **action Button** (e.g., "Activate Scene", "Add Device", "Save Rule")

For each component:

- Set `fx:id` in the Code panel (e.g., `brightnessSlider`)
- Set `accessibleText` in the Properties panel for any widget that doesn't have visible text. **This must match exactly** (case-sensitive) what your E2E test uses in `findByAccessibleText()`.
- Set `onAction` for your Button → `#handleYourAction`

Check that every `fx:id` follows a consistent naming convention. Check that every interactive widget has `accessibleText`. 

## 3.2 Phase B: Wire ViewModel & Controller

**Start with the ViewModel** (so the Controller can call its methods without crashing):

Fill in the ViewModel for your chosen task. Each skeleton has properties declared and TODO methods:

- **SceneBuilderViewModel:** `addDeviceToScene()`, `removeDeviceFromScene()`, `saveScene()`
- **DeviceSetupViewModel:** `scanForDevices()`, `selectDevice()`, `assignToRoom()`, `saveDevice()`
- **ScheduleViewModel:** `setTrigger()`, `setAction()`, `saveRule()`

Implement enough TODO methods for one complete user flow (e.g., add a device to a scene *and* save it). In practice this means at least 2 methods, often all of them — they tend to depend on
each other.

**Then wire the Controller:**

1. Add `@FXML` fields matching your `fx:id`s
2. In `initialize()`, **create sample data** — build Area objects with devices and/or scenes, similar to `createSampleArea()` in the reference Controller. Your ViewModel needs data to display.
3. Create the ViewModel and connect it to the model (`setArea()` or `setModel()`)
4. Bind widgets to ViewModel properties. **Use `bind()` for display-only Labels; use `bindBidirectional()` for TextFields where user input should flow back to the ViewModel.** The reference only shows `bind()` (one-way) because it only has Labels and a Slider listener — your task may need bidirectional binding for TextFields.
5. Set up listeners for ComboBox selection, slider changes, etc. (see the reference Controller's ComboBox listener pattern: `comboBox.getSelectionModel().selectedItemProperty().addListener(...)`)
6. Implement your button handler — delegate to the ViewModel
7. Your Controller skeleton already has `@NullUnmarked` at the class level — no action needed. In your ViewModel implementations, use `Objects.requireNonNull(area, "Call setArea() first")` (or `areas`) to satisfy NullAway where the backing model field is `@Nullable`.

:::warning 

Implement ViewModel methods before wiring Controller listeners If your Controller sets up listeners that call ViewModel TODO methods (like `selectDevice()` or `assignToRoom()`), those listeners will fire during `initialize()` and throw `UnsupportedOperationException`. Implement the
ViewModel methods first.
:::


## 3.3 Phase C: Run & Polish

Launch `SceneItAllApp`:

- Click your button — does the device list update?
- Drag the slider — does the value change?
- Tab through the GUI — can you reach every widget?

Fix anything that is broken. 

---

# 4 Part 3: Test

:::info Why test last? 

You might wonder: shouldn't we write tests first? In GUI development, there is a real cost to writing tests too early. If you'd written E2E tests before seeing the running app, those tests would assert on the _old_ layout and break when you polish it.

This is a key difference from domain logic testing (where test-first works great). GUI tests are expensive to write and fragile when the interface is still evolving. The professional pattern is:
**explore manually first** (including having someone else try your UI), **stabilize the design**, then **lock it down with automated tests.** ViewModel tests are more stable since they don't depend
on layout — but E2E tests should wait until you're confident in the interaction design.

:::

## 4.1 Write one ViewModel test

Open the ViewModel test file for your chosen task. The scaffold has one example test and one TODO.

Write a test that:

1. Creates a ViewModel and sets a Model with test data
2. Calls one of the command methods you implemented
3. Asserts on a property value

Examples for each task:

```java
// Scene Builder task — addDeviceToScene() reads from properties, not parameters
// testArea is built in @BeforeEach (see scaffold)
@Test
void addDeviceToScene_updatesDeviceList() {
    SceneBuilderViewModel vm = new SceneBuilderViewModel();
    vm.setArea(testArea);                              // setArea(), not setModel()
    vm.selectedDeviceProperty().set("Ceiling Light");  // set properties first
    vm.targetValueProperty().set(30);

    vm.addDeviceToScene();                             // no parameters — reads from properties

    assertThat(vm.getSceneDevices()).anyMatch(s -> s.contains("Ceiling Light"));
}

// Device Setup task — setModel() takes List<Area>, not setArea()
@Test
void assignToRoom_updatesRoomProperty() {
    DeviceSetupViewModel vm = new DeviceSetupViewModel();
    vm.setModel(List.of(new Area("Living Room"), new Area("Bedroom")));
    vm.selectDevice("New Light");                      // accepts any name, not just scanned ones

    vm.assignToRoom("Bedroom");

    assertThat(vm.assignedRoomProperty().get()).isEqualTo("Bedroom");
}

// Schedule task — setAction() takes 2 parameters (scene, area), not 3
@Test
void saveRule_addsToRuleList() {
    ScheduleViewModel vm = new ScheduleViewModel();
    vm.setModel(testAreas);
    vm.setTrigger("Sunset");
    vm.setAction("Evening", "Living Room");            // 2 params, not 3

    vm.saveRule();

    assertThat(vm.getRules()).isNotEmpty();
}
```

Run it. It should pass in milliseconds — no JavaFX runtime needed.

Open the E2E test file for your chosen task. The scaffold has `start()` pre-wired and a `findByAccessibleText()` helper. **Study `AreaDashboardE2ETest` carefully before writing your own** — it uses `interact()` to run actions on the JavaFX thread, which is more reliable than `clickOn()` for ComboBox selections and button clicks. Write a test that:

1. Finds widgets by `accessibleText` and casts them to their types (e.g., `ComboBox`, `Button`)
2. Uses `interact(() -> { ... })` to manipulate widgets programmatically
3. Calls `WaitForAsyncUtils.waitForFxEvents()` after interactions
4. Asserts on a visible result using AssertJ's `assertThat`

Examples for each task:

```java
// Scene Builder task — use interact() for reliable widget manipulation
@Test
void userCanAddDeviceToScene() {
    @SuppressWarnings("unchecked")
    ComboBox<String> deviceCombo =
        (ComboBox<String>) findByAccessibleText("Select device");
    Slider targetSlider = (Slider) findByAccessibleText("Target value");
    Button addBtn = (Button) findByAccessibleText("Add device to scene");

    interact(() -> {
        deviceCombo.getSelectionModel().select("Ceiling Light");
        targetSlider.setValue(30);
        addBtn.fire();
    });
    WaitForAsyncUtils.waitForFxEvents();

    @SuppressWarnings("unchecked")
    ListView<String> devices =
        (ListView<String>) findByAccessibleText("Devices in scene");
    assertThat(devices.getItems().stream()
        .anyMatch(s -> s.contains("Ceiling Light"))).isTrue();
}

// Device Setup task
@Test
void userCanAddNewDevice() {
    TextField nameField = (TextField) findByAccessibleText("Device name");
    @SuppressWarnings("unchecked")
    ComboBox<String> roomCombo =
        (ComboBox<String>) findByAccessibleText("Choose a room");
    Button saveBtn = (Button) findByAccessibleText("Save device");

    interact(() -> {
        nameField.setText("Desk Lamp");
        roomCombo.getSelectionModel().select("Bedroom");
        saveBtn.fire();
    });
    WaitForAsyncUtils.waitForFxEvents();

    Label status = (Label) findByAccessibleText("Status message");
    assertThat(status.getText()).contains("saved");
}

// Schedule task — note: must select trigger, scene, AND area before saving
@Test
void userCanCreateAutomationRule() {
    @SuppressWarnings("unchecked")
    ComboBox<String> triggerCombo =
        (ComboBox<String>) findByAccessibleText("Select trigger");
    @SuppressWarnings("unchecked")
    ComboBox<String> sceneCombo =
        (ComboBox<String>) findByAccessibleText("Select scene");
    @SuppressWarnings("unchecked")
    ComboBox<String> areaCombo =
        (ComboBox<String>) findByAccessibleText("Select area");
    Button saveBtn = (Button) findByAccessibleText("Save rule");

    interact(() -> {
        triggerCombo.getSelectionModel().select("Sunset");
        sceneCombo.getSelectionModel().select("Evening");
        areaCombo.getSelectionModel().select("Living Room");
        saveBtn.fire();
    });
    WaitForAsyncUtils.waitForFxEvents();

    @SuppressWarnings("unchecked")
    ListView<String> rules =
        (ListView<String>) findByAccessibleText("Automation rules");
    assertThat(rules.getItems()).isNotEmpty();
}
```

Run it. This one takes a couple seconds — it launches the real GUI.

---

# 5 Part 4: Reflection


## 5.1 Section 1: The Build

- Which design task did you choose?

## 5.2 Section 2: Testing

- Paste or screenshot your passing ViewModel test
- Paste or screenshot your passing E2E test
- Which test was easier to write? Which gave you more confidence that your code works?

---

## Submission

Submit all the code and `REFLECTION.md`.

## Grading

**Option 1:** Running GUI + both tests passing + reflection → full
credit.

**Option 2:** Submit whatever you complete along with the reflection documenting your progress, what you got stuck on, and what you learned → good-faith credit available. Attendance and genuine engagement matter more than perfection.
