---
sidebar_position: 3
---

# Lab: Polymorphism and Collections

:::info Grading: What You Need to Submit


**Option 1: Successful Completion**

- Complete Parts 1-3 of the lab
- All code compiles and runs correctly
- Push your completed work to GitHub
- Complete the reflection in `REFLECTION.md`

**Option 2: Partial Credit**
If you're unable to complete everything:
- Submit a `REFLECTION.md` documenting what you completed, where you got stuck, and what you tried
- A TA will review your submission and award credit for good-faith effort

The **Optional Extensions** are not required for full credit but are excellent practice if you finish early. You may also resubmit this lab *after* the due date for feedback (but your grade will not change).

:::

:::warning Attendance Matters

If lab leaders observe that you are **not working on the lab** during the section, or you **leave early** AND do not successfully complete the lab, you will receive **no marks**. However: if you finish the required parts of the lab and want to work on something else, just show the lab leader that you're done, and you'll be all set!


:::


## Learning Objectives

By the end of this lab, you will be able to:

- Implement methods that use polymorphism to operate on objects through supertype references
- Select appropriate collection types (List, Set, Map) based on access patterns
- Measure and compare performance characteristics of different collection implementations

## Before You Begin

**Clone the Lab Repository:** Clone your lab repository. The repository includes:

**Core Device Classes** (`net.sceneitall.iot`):
- `IoTDevice.java` — interface
- `Light.java`, `DimmableLight.java`, `TunableWhiteLight.java` — the light hierarchy
- `Fan.java` — a separate device type
- `DeviceGenerator.java` — generates test devices for performance measurement

**Part 1: Polymorphism** (`net.sceneitall.iot.labpoly.part1`):
- `SmartHomeController.java` — controller class with method stubs
- `SmartHomeControllerTest.java` — test file with starter tests

**Part 2: Collections** (`net.sceneitall.iot.labpoly.part2`):
- `CollectionsExercises.java` — where you will write code for Part 2

**Part 3: Performance** (`net.sceneitall.iot.labpoly.part3`):
- `PerformanceExercises.java` — where you will write code for Part 3

**Stretch Goals** (`net.sceneitall.iot.labpoly.stretch`):
- `CeilingFanWithLight.java` — composition example for Stretch Goal 2
- `StretchExercises.java` — generic methods exercise for Stretch Goal 3

---

## 1 Polymorphism in Action

The power of polymorphism is writing code that works with *any* subtype—even ones that don't exist yet. In this exercise, you'll implement a smart home controller that operates on devices without knowing their concrete types.

### 1.1 Implement a Device Controller

The starter code includes a `SmartHomeController` class with method stubs. Your task: implement methods that work with **any** `IoTDevice` using polymorphism.

```java
public class SmartHomeController {
    private List<IoTDevice> devices;

    public SmartHomeController() {
        this.devices = new ArrayList<>();
    }

    /**
     * Adds any IoT device to the controller.
     */
    public void addDevice(IoTDevice device) {
        // TODO: Implement this
    }

    /**
     * Calls identify() on ALL devices in the home.
     * Each device type will identify itself differently (lights flash, fans spin, etc.)
     */
    public void identifyAllDevices() {
        // TODO: Implement this
        // Hint: You don't need to know what type each device is!
    }

    /**
     * Returns a count of how many devices are currently available (connected).
     */
    public int countAvailableDevices() {
        // TODO: Implement this
        // Use the isAvailable() method from IoTDevice
    }
}
```

### 1.2 Write JUnit Tests for Your Controller

In `SmartHomeControllerTest.java`, write JUnit 5 tests that verify your implementation works with a mix of device types. This exercise will help you practice writing tests for Assignment 1.

**Example Test 1: Basic Functionality**
```java
@Test
void identifyAllDevicesWorksWithMixedDeviceTypes() {
    SmartHomeController controller = new SmartHomeController();

    // Add different device types - they should all work!
    controller.addDevice(new Fan("ceiling-fan"));
    controller.addDevice(new DimmableLight("desk-lamp", 75));  // 75 = startup brightness %
    controller.addDevice(new TunableWhiteLight("living-room", 2700, 100));  // 2700K startup color temp, 100% startup brightness

    // This should not throw any exceptions
    assertDoesNotThrow(() -> controller.identifyAllDevices());
}
```

**Example Test 2: Testing with assertEquals**
```java
@Test
void addDeviceIncreasesDeviceCount() {
    SmartHomeController controller = new SmartHomeController();

    // Initially, no devices
    assertEquals(0, controller.getDeviceCount(),
                 "New controller should have 0 devices");

    // Add one device
    controller.addDevice(new Fan("fan-1"));
    assertEquals(1, controller.getDeviceCount(),
                 "After adding 1 device, count should be 1");

    // Add another device (50 = startup brightness %)
    controller.addDevice(new DimmableLight("light-1", 50));
    assertEquals(2, controller.getDeviceCount(),
                 "After adding 2 devices, count should be 2");
}
```

**Example Test 3: Testing Edge Cases**
```java
@Test
void countAvailableDevicesOnlyCountsAvailableDevices() {
    SmartHomeController controller = new SmartHomeController();

    // Create devices with different availability states
    Fan fan = new Fan("fan-1");
    DimmableLight light = new DimmableLight("light-1", 100);  // 100 = startup brightness %

    fan.setAvailability(true);   // Available
    light.setAvailability(false); // Not available

    controller.addDevice(fan);
    controller.addDevice(light);

    // Only the fan should be counted as available
    assertEquals(1, controller.countAvailableDevices(),
                 "Should only count available devices");
}
```

**Now You Try: Complete These Tests**
```java
@Test
void countAvailableDevicesCountsAllDeviceTypes() {
    SmartHomeController controller = new SmartHomeController();

    // TODO: Add at least 3 different device types (Fan, DimmableLight, TunableWhiteLight)
    // Make sure all are available
    // Use assertEquals to verify the count matches the number you added
}

@Test
void countAvailableDevicesReturnsZeroWhenEmpty() {
    // TODO: Test that a new controller returns 0 available devices
    // Use assertEquals to verify this
}

@Test
void identifyAllDevicesWorksWithEmptyController() {
    // TODO: Test that calling identifyAllDevices on an empty controller doesn't crash
    // Use assertDoesNotThrow
}
```

**Run your Part 1 tests** using VS Code's Test Explorer:
1. Open the Testing sidebar (flask icon in the left sidebar, or `Cmd+Shift+P` → "Testing: Focus on Test Explorer View")
2. Expand `SmartHomeControllerTest`
3. Click the play button (▶) next to individual tests or the entire class

:::tip Command Line Alternative
You can also run tests from the terminal:
```bash
# macOS/Linux
./gradlew test --tests "net.sceneitall.iot.labpoly.part1.*"

# Windows
.\gradlew.bat test --tests "net.sceneitall.iot.labpoly.part1.*"
```
Since Parts 2 and 3 aren't implemented yet, running all tests will show failures. The commands above run only Part 1 tests.
:::

**Key insight:** Your `identifyAllDevices()` method doesn't contain any `if (device instanceof Fan)` checks—it just calls `identify()` and the JVM figures out which implementation to run. That's polymorphism at work.

**JUnit 5 cheat sheet**


| Assertion | Use Case | Example |
|-----------|----------|---------|
| `assertEquals(expected, actual, message)` | Check if two values are equal | `assertEquals(5, list.size(), "List should have 5 items")` |
| `assertNotEquals(unexpected, actual, message)` | Check if two values are different | `assertNotEquals(0, device.getId(), "ID should not be 0")` |
| `assertTrue(condition, message)` | Check if a condition is true | `assertTrue(device.isAvailable(), "Device should be available")` |
| `assertFalse(condition, message)` | Check if a condition is false | `assertFalse(list.isEmpty(), "List should not be empty")` |
| `assertNull(object, message)` | Check if an object is null | `assertNull(controller.findDevice("missing"), "Should return null")` |
| `assertNotNull(object, message)` | Check if an object is not null | `assertNotNull(device, "Device should not be null")` |
| `assertThrows(ExceptionType.class, executable)` | Verify an exception is thrown | `assertThrows(IllegalArgumentException.class, () -> device.setBrightness(-1))` |
| `assertDoesNotThrow(executable)` | Verify no exception is thrown | `assertDoesNotThrow(() -> controller.identifyAllDevices())` |
| `assertSame(expected, actual, message)` | Check if two references point to the same object | `assertSame(device1, controller.getDevice(0))` |
| `assertNotSame(unexpected, actual, message)` | Check if two references point to different objects | `assertNotSame(device1, device2, "Should be different instances")` |

**Best Practices:**
- Always include a descriptive message as the last parameter—it helps when tests fail!
- Put the expected value first, then the actual value: `assertEquals(expected, actual)`. This makes failure messages clearer.
- Use the most specific assertion available (e.g., `assertNull()` instead of `assertEquals(null, obj)`)

**Resources:**
- [JUnit 5 User Guide - Assertions](https://junit.org/junit5/docs/current/user-guide/#writing-tests-assertions)
- [JUnit 5 Assertions JavaDoc](https://junit.org/junit5/docs/current/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html)


### 1.3 Discussion — Design Questions

With a neighbor, discuss these design questions:

**Question 1: Why is `Light` abstract with no abstract methods?**

Look at the `Light` class—it's marked `abstract`, but it has no abstract methods. Everything is fully implemented!

- Why might we want to prevent someone from writing `new Light("my-light")`?
- What's the difference between `Light` as a *concept* vs `SwitchedLight` as a *concrete thing*?

**Question 2: Why don't we make `SwitchedLight` the base class?**

An alternative design: Make `SwitchedLight` the base class (not abstract), and have `DimmableLight` extend it directly.

- What would that imply about the relationship between switched and dimmable lights?
- Is a dimmable light really a "kind of" switched light, or are they siblings?
- What happens if we later want to add a light type that *isn't* switchable (e.g., always-on indicator light, or one that MUST have a gentle ramp in brightness and can't be discretely controlled)?

**Question 3: What makes a "Device"?**

Look at the `IoTDevice` interface:

- What capabilities does `IoTDevice` assume all devices have?
- What new device types could easily fit this interface? (thermostats, door locks, cameras, robot vacuums...)
- What might be awkward? (Does a smart speaker "identify" itself the same way? What about a device with multiple components like a fan with a light?)

**When you are done discussing, call a TA and discuss your answers with them.**


## 2 Collections Selection

Choosing the right collection type makes your code clearer and faster. In this section, you'll practice matching problems to collections.

### 2.1 Fix the Generics Bug

The starter code contains this problematic snippet in `CollectionsExercises.java`:

```java
// This code has a bug! Fix it using generics.
public static void demonstrateGenericsBug() {
    List devices = new ArrayList();  // Raw type warning!
    devices.add(new DimmableLight("test", 100));
    devices.add("oops, this is a string");  // No compile error...

    // This will crash at runtime!
    for (Object obj : devices) {
        Light light = (Light) obj;
        light.turnOn();
    }
}
```

**Your task:** Fix this code so the compiler catches the bug. The string should cause a compile-time error, not a runtime crash.

**After you've fixed the bug:** Comment out or remove the line `devices.add("oops, this is a string");` so your code can compile and run for the remaining lab exercises. Your fix should make the compiler reject this line—which is exactly what we want! But to continue with the rest of the lab, you'll need to remove it.

### 2.2 Choose the Right Collection

For each scenario below, choose the appropriate collection type and implement a solution in `CollectionsExercises.java`.

**Scenario A: Device Registry**

You're building a smart home system that stores devices by their unique ID (like `"living-room-main"` or `"bedroom-fan"`). You need to quickly look up a device by its ID.

```java
// TODO: Implement createDeviceRegistry()
// - Choose the right collection type
// - Add at least 3 devices with meaningful IDs
// - Return the collection
```

Questions to consider:
- Do you need to look up by key or by position?
- Do keys need to be unique?

**Scenario B: Devices by Room**

You want to track all devices in each room. A room can have multiple devices, and you need to find all devices in a given room quickly.

```java
// TODO: Implement groupDevicesByRoom()
// - What should the key type be?
// - What should the value type be?
// - Add devices to at least 2 rooms
```

**Scenario C: Online Device Tracking**

You're tracking which devices are currently online. When a device comes online, you add it. When it goes offline, you remove it. You frequently need to check "is this device online?"

```java
// TODO: Implement createOnlineDeviceTracker()
// - Choose a collection that efficiently answers "contains?" queries
// - Order doesn't matter
```

Verify your Part 2 code compiles:
```bash
# macOS/Linux
./gradlew compileJava

# Windows
.\gradlew.bat compileJava
```

### 2.3 Interactive Testing with `main()`

Part 2 does not have automated JUnit tests. Why? Because **sometimes the fastest way to test during exploratory development is to poke at your code interactively**, not to spend time writing exhaustive test suites.

We've provided a `main()` method in `CollectionsExercises.java` that demonstrates this approach:

```bash
# macOS/Linux
./gradlew runPart2

# Windows
.\gradlew.bat runPart2
```

This will:
- Print out what collections you created
- Show you their contents
- Give you commented-out code to uncomment as you implement each method

**The Philosophy:** When you're learning a new library or exploring a design, a simple `main()` method lets you:
- Quickly see what your data structures contain
- Try operations and observe results immediately
- Understand behavior before committing to a design

Once you understand what you're building, *then* you write proper tests. But for initial exploration? `main()` may be your friend.

Feel free to modify the `main()` method to test your own scenarios!

:::note No Automated Tests for Part 2
Part 2 exercises are manually verified - as long as you put some effort in, you will get marks. 
:::

**Call a TA and tell them what collection you used for Scenarios A, B and C. Briefly tell them why.**


## 3 Performance Showdown

Let's measure the performance difference between collection types. You'll compare how long it takes to **build** different collections and to **look up** elements in them.

### The Challenge

With 10,000 devices:
1. How long does it take to **build** each collection type?
2. How long does it take to **find** a device by ID?

### 3.1 Implement the Collection Builders

Complete these methods in `PerformanceExercises.java`:

**Build an ArrayList:**
```java
public static ArrayList<IoTDevice> buildArrayList(List<IoTDevice> devices) {
    ArrayList<IoTDevice> list = new ArrayList<>();
    // TODO: Add all devices to the ArrayList
    return list;
}
```

**Build a LinkedList:**
```java
public static LinkedList<IoTDevice> buildLinkedList(List<IoTDevice> devices) {
    LinkedList<IoTDevice> list = new LinkedList<>();
    // TODO: Add all devices to the LinkedList
    return list;
}
```

**Build a HashMap:**
```java
public static HashMap<String, IoTDevice> buildHashMap(List<IoTDevice> devices) {
    HashMap<String, IoTDevice> map = new HashMap<>();
    // TODO: Add all devices, using device ID as the key
    return map;
}
```

### 3.2 Implement the Lookup Methods

```java
public static IoTDevice findInArrayList(ArrayList<IoTDevice> devices, String targetId) {
    // TODO: Loop through the list, check each device's ID
    // Return the device if found, null otherwise
}

public static IoTDevice findInLinkedList(LinkedList<IoTDevice> devices, String targetId) {
    // TODO: Loop through the list, check each device's ID
    // Return the device if found, null otherwise
}

public static IoTDevice findInHashMap(HashMap<String, IoTDevice> deviceMap, String targetId) {
    // TODO: Look up the device directly by ID
}
```

### 3.3 Run the Performance Test

The starter code includes a `runPerformanceComparison()` method that:
1. Generates 10,000 devices using `DeviceGenerator`
2. Times how long it takes to build each collection
3. Performs 1,000 lookups and measures the time

Run the performance test:
```bash
# macOS/Linux
./gradlew runPart3

# Windows
.\gradlew.bat runPart3
```

**Record your results:**

| Collection | Time to Build (10K devices) | Time for 1,000 Lookups |
|------------|-----------------------------|-----------------------|
| ArrayList  | ___ ms | ___ ms |
| LinkedList | ___ ms | ___ ms |
| HashMap    | ___ ms | ___ ms |

### 3.4 Analyze the Results (Reflection)

This is a reflection exercise—no additional code required! Answer these questions in your `REFLECTION.md`:
1. Which was fastest to **build**? Which was fastest to **look up**?
2. Why is HashMap lookup faster than ArrayList/LinkedList?
3. For the build times: Were ArrayList and LinkedList similar? Why or why not?
4. If you only needed to look up devices **once**, would a HashMap still be worth it?

---

## Reflection

Complete the `REFLECTION.md` file with your answers to:

1. **Polymorphism:** In your `SmartHomeController`, why didn't you need to write any `instanceof` checks? What would happen if a new device type (like `SmartThermostat`) were added to the codebase?

2. **Collections:** For one of the scenarios in Part 2, explain why your chosen collection type was the best fit.

3. **Performance:** Record your timing results table from Section 3.3, and answer the analysis questions from Section 3.4.

4. **Collaboration:** Did you and your neighbor have different approaches in today's lab? How did you resolve disagreements? What did you learn from discussing with someone who thought differently?

---

## Optional Extensions

If you finish early, try one or more of these challenges:

### Stretch Goal 1: Performance Deep Dive

Modify the performance test to explore further:

1. **Vary collection size:** Test with 1,000, 10,000, and 100,000 devices. How does each approach scale? Does the relative performance change?

2. **Insertion at different positions:** Measure time to insert 1,000 devices at the *beginning* vs the *end* of an ArrayList vs a LinkedList. Explain the differences.

3. **Iteration performance:** Measure how long it takes to iterate through all 10,000 devices in ArrayList vs LinkedList. Which is faster? Why? (Hint: think about memory layout)

Add your findings to `REFLECTION.md` under "Optional: Performance Deep Dive."

### Stretch Goal 2: Design Patterns Analysis

The starter code includes a `CeilingFanWithLight` class that uses **composition**—it *has* a Light and *has* a Fan rather than trying to *be* both.

1. Read through `CeilingFanWithLight.java`
2. Answer in `REFLECTION.md`:
   - Why doesn't `CeilingFanWithLight` extend both `Light` and `Fan`?
   - What's the advantage of the composition approach?
   - What's a disadvantage?
   - When would inheritance be a better choice than composition?

### Stretch Goal 3: Generic Methods

Implement this generic method in `StretchExercises.java`:

```java
/**
 * Filters a list of devices to return only those of a specific type.
 *
 * Example usage:
 *   List<Light> lights = filterByType(allDevices, Light.class);
 *   List<Fan> fans = filterByType(allDevices, Fan.class);
 *
 * @param devices the list of devices to filter
 * @param type the class object representing the desired type
 * @return a new list containing only devices of the specified type
 */
public static <T extends IoTDevice> List<T> filterByType(
        List<IoTDevice> devices,
        Class<T> type) {
    // TODO: Implement this method
    // Hint: Use type.isInstance(device) to check if a device matches
}
```

Test your implementation:
```java
List<IoTDevice> allDevices = DeviceGenerator.generateMixedDevices(100);
List<Light> lights = filterByType(allDevices, Light.class);
List<Fan> fans = filterByType(allDevices, Fan.class);
System.out.println("Found " + lights.size() + " lights and " + fans.size() + " fans");
```

---

## Submission Checklist

Push your work regularly—Pawtograder will test your code each time you push. This lets you catch issues early and get feedback as you work.

Before your final submission, ensure:

- [ ] Part 1: You've implemented `SmartHomeController` and written JUnit tests for it
- [ ] Part 2: You've fixed the generics bug and implemented all 3 collection scenarios
- [ ] Part 3: You've implemented the build and lookup methods, and recorded timing results
- [ ] `REFLECTION.md` is complete with all required answers
- [ ] All tests pass: `./gradlew test` (Windows: `.\gradlew.bat test`)
- [ ] Your code compiles: `./gradlew build` (Windows: `.\gradlew.bat build`)
- [ ] All changes are committed and pushed to GitHub
