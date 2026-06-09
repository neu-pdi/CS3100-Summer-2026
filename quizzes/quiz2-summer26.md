# CS 3100: Final Exam

**Course:** CS3100 -- Program Design and Implementation 2
**Format:** 23 multiple-choice/multiple-answer questions + 1 open-ended case study
**Coverage:** Cumulative
**Points:** 150 total (Part I: 92 pts • Part II: 58 pts)
**Time Limit:** 90 minutes

## Instructions

- Please do NOT separate the pages
- You may not use notes, books, or electronic devices
- You may use a cheat sheet

---

# Questions

## Part I: Multiple Choice/Answers

Many questions expect a single, best answer. Some questions have multiple answers: read the question carefully to find them.

Each question is worth 5 points.

### Question 1

Consider this code that uses the command design pattern to streamline a CLI:

```java
public ThermostatCommand process(String command) {
    String[] parts = command.split(" ");
    ThermostatCommand commandObject = null;
    if (parts[0].equals("create")) {
        commandObject = new CreateThermostatCommand(parts[1],
        Integer.parseInt(parts[2]));
    } else if (parts[0].equals("increment")) {
        commandObject = new ChangeTemperatureCommand(parts[1],
        TemperatureChangeType.Increment);
    } else if (parts[0].equals("decrement")) {
        commandObject = new ChangeTemperatureCommand(parts[1],
        TemperatureChangeType.Decrement);
    } else if (parts[0].equals("get")) {
        commandObject = new GetTemperatureCommand(parts[1]);
    } else if (parts[0].equals("addmonitor")) {
        commandObject = new AddMonitorCommand(parts[1], new 
        PrintMonitorAdapter());
    }
    return commandObject;
}
```

Paul believes he can make this code shorter by storing command objects in a `Map<String, ThermostatCommand>` and rewriting the method as:

```java
private Map<String, ThermostatCommand> commandMap;

public ThermostatCommand process(String command) {
    String[] parts = command.split(" ");
    commandObject = commandMap.getOrDefault(parts[0], null);
    return commandObject;
}
```

Select all options below that either make this design infeasible or undesirable (each correct answer will get you points, each wrong answer will cause a deduction):

- a) Although this method is short, the code overall is not necessarily shorter: extra code must be written to populate this map
- b) This won't work because command objects cannot be "pre-made" and put into the map.
- c) This code is significantly less readable because the reader must know how a map lookup works.
- d) This code is significantly slower than the first implementation.

---

### Question 2

Paul was given the following class:

```java
// numerator can be any number. Denominator can be either positive or negative
public record Fraction(int numerator,int denominator) 
                implements Comparable<Fraction> {

    public Fraction {
        if (denominator == 0) {
            throw new IllegalArgumentException("Denominator cannot be 0");
        }
    }

    /**
     * Two fractions are equal if they evaluate to the same decimal value.
     * Note that two equal fractions need not have the same values for
     * numerator and denominator (e.g. 1/2 and 2/4)
     */
    public boolean equals(Object o) {
        if (o == this) return true;
        if (o instanceof Fraction f) {
            // a/b == c/d if ad = bc
            return this.numerator * f.denominator
            == f.numerator * this.denominator;
        }
        return false;
    }

    public int hashCode() { ... }
}
```

Paul decides to test the `equals` method using a fuzzy test, as below:

```java
@Test
public void testEquals() {
    //create a random number generator
    Random r = new Random();

    for (int i=0;i<100000;i+=1) {
        int a = r.nextInt();
        int b = r.nextInt();
        int c = r.nextInt();
        int d = r.nextInt();

        Fraction f1 = new Fraction(a,b);
        Fraction f2 = new Fraction(c,d);

        assertEquals(a*d==b*c,f1.equals(f2));
    }
}

```

Select all the *limitations* of this test. (Each correct answer will get you points, each wrong answer will be a deduction)

- a) This test is not deterministic: it is difficult to replicate a failure
- b) This test will execute too slowly for it to be useful
- c) This test only uses positive numbers for the fractions
- d) This test may encounter unexpected exceptions even with small numbers and therefore may fail for unexpected reasons

---

### Question 3

Select the option below that most accurately describes `Java bytecode`.

- a) Bytecode is the operating-system-specific binary executable file that is produced when a Java application is built.
- b) Bytecode is a lower-level representation that can be executed without any modifications on any Java-supported operating system by using the JVM (the `java` program)
- c) Bytecode is Java code that is compliant with modern 64-bit operating systems (hence the name "byte" code)
- d) Bytecode is produced specifically when a Java project uses Gradle

---

### Question 4

A developer stores serving counts for every recipe in a large recipe database using `long` (8 bytes per entry). The maximum serving count for any recipe is 500. A code reviewer suggests switching to `byte` (1 byte per entry). Why would this change be problematic?

- a) `byte` values cannot be used in arithmetic operations in Java and must first be cast to `int`
- b) `byte` is a reference type, so it cannot store numeric values directly and requires autoboxing
- c) The JVM requires all numeric fields in a class to use the same type for memory alignment purposes
- d) `byte` may not be able to store serving counts in all cases

---

### Question 5

Select all the advantages of using abstract classes over interfaces (each correct answer will get you points, each wrong answer will cause a deduction):

- a) Abstract classes can have mutable fields but interfaces cannot
- b) Abstract classes can have public methods but interfaces cannot
- c) Abstract classes can have non-public abstract methods
- d) A class can extend multiple abstract classes but not implement multiple interfaces

---

### Question 6

You are given the following code:

```java
public abstract class Counter {
    protected int counter;

    public Counter(int initial) {
        counter = initial;
    }

    public int getCounter() {
        return counter;
    }

    public abstract void increment();
}

public class CounterOne extends Counter {

    public CounterOne(int initial) {
        super(initial);
    }

    public void increment() {
        counter += 1;
    }
}

public class CounterTwo extends CounterOne {
    private int jump;

    public CounterTwo(int initial) {
        super(initial);
        jump = 2;
    }

    public void increment() {
        counter += jump;
        jump += 1;
    }
}

public static void main(String[] args) {
    Counter c2 = new CounterTwo(1);
    Counter c = new CounterOne(1);

    c2.increment();
    c.increment();
    System.out.print(c.getCounter());
    c = c2;
    c.increment();
    System.out.print(" and " c.getCounter());
}
```

What is printed when this program is run?

- a) 2 and 3
- b) 3 and 4
- c) 2 and 6
- d) 2 and 4

---

### Question 7

A vehicle is equipped with a GPS device that records the GPS location of the vehicle every 2 minutes when the vehicle is in operation. Prof Shesh asks students to write a class that will maintain this data in a list, and support appending new locations to that list. It also has a method that "summarizes" the journey by returning the locations at the first, one-third, two-thirds and last locations of this vehicle in a list.

A student writes the following code:

```java
public record class GPSLocation(double longitude, double latitude);

class LocationStore {
    private List<GPSLocation> readouts;

    public LocationStore() {
        readouts = new ArrayList<GPSLocation>();
    }

    public void appendLocation(GPSLocation loc) {
        readouts.add(loc);
    }

    public List<GPSLocation> getSummary() {
        List<GPSLocation> summary = new ArrayList<GPSLocation>();
        summary.add(readouts.get(0));
        summary.add(readouts.get(readouts.size() / 3));
        summary.add(readouts.get(2 * readouts.size() / 3));
        summary.add(readouts.get(readouts.size() - 1));
        return summary;
    }
}
```

The grading rubric: 0 = code works incorrectly; 1 = code works correctly but could be more efficient (works faster and/or takes less space); 2 = code works correctly and data represented efficiently. What grade should this student receive?

- a) 0
- b) 1
- c) 2

---

### Question 8

Consider this `equals` implementation for a `DimmableLight`:

```java
@Override
public boolean equals(@Nullable Object obj) {
    if (this == obj) return true;
    if (!(obj instanceof DimmableLight other)) return false;
    return this.brightness == other.brightness && this.on == other.on;
}
```

A teammate suggests also overriding `equals` in `TunableWhiteLight` (which extends `DimmableLight`) so that a `TunableWhiteLight` and a `DimmableLight` with the same `brightness` and `on` values are considered equal. What is the primary risk of this approach?

- a) It would cause a `StackOverflowError` because `TunableWhiteLight.equals` would call `DimmableLight.equals` recursively
- b) It would cause `instanceof` to always return `false` when comparing objects of different subclasses
- c) It would prevent `hashCode` from compiling, because `hashCode` must have the same parameter types as `equals`
- d) It would break the symmetry or transitivity of `equals`, since the result would differ depending on which object's `equals` is invoked

---

### Question 9

A developer overrides `hashCode` in a class `X` but forgets to override `equals`, leaving `equals` as the default `Object.equals` (reference equality). What is the most likely observable consequence when two distinct `X` objects with identical fields are added to a `HashSet<X>`?

- a) Both objects always appear as separate entries, because the default `equals` uses reference identity and considers the two objects distinct
- b) A `HashSet` uses only `hashCode` for deduplication, so the two objects will correctly be treated as one entry in the set
- c) The compiler will reject the code with an error because `equals` and `hashCode` must always be overridden together in Java
- d) The `HashSet` will throw an `IllegalStateException` when the second object is added, detecting the contract violation at runtime

---

### Question 10

A developer writes the following class:

```java
public class BrokenLight extends Light {
    @Override
    public void turnOn() {
        throw new UnsupportedOperationException("This light is broken!");
    }
}
```

Existing code that accepts a `Light` and calls `turnOn()` on it will crash when given a `BrokenLight`. Which SOLID principle does this design violate?

- a) Single Responsibility Principle, because `BrokenLight` is both a light and an error reporter
- b) Interface Segregation Principle, because the `Light` interface is too large and should be split into separate `Switchable` and `Dimmable` interfaces
- c) Open/Closed Principle, because `BrokenLight` modifies the behavior of the existing `Light` class
- d) Liskov Substitution Principle, because a `BrokenLight` cannot be used wherever a `Light` is expected without breaking the caller

---

### Question 11

Select the most accurate statement about abstract classes and interfaces.

- a) A class may extend at most one abstract class and at most one interface
- b) A class may extend at most one abstract class and implement multiple interfaces
- c) A class may extend several abstract classes and implement multiple interfaces
- d) A class may extend at most one abstract class or implement multiple interfaces but not both

---

### Question 12

You are given the following Java code:

```java
interface Student {...}
interface Employee {...}
class SimpleStudent implements Student {...}
class BasicEmployee implements Employee {...}
```

You have to represent a student-employee: a person that has both student and employee privileges at Northeastern University. Which of the following options are closest to a correct and working `StudentEmployee`? (Select all that apply. Each correct answer will earn points, each wrong answer will earn a deduction.)

```java
// Option 1: inheritance
class StudentEmployee extends SimpleStudent, BasicEmployee {
    // Student and Employee methods are inherited
}

// Option 2: inheritance + composition
class StudentEmployee extends SimpleStudent {
    private Employee emp;
    // Student methods are inherited, Employee methods delegate to emp
}

// Option 3: inheritance + composition
class StudentEmployee extends BasicEmployee implements Student {
    private Student stu;
    // Employee methods are inherited, Student methods delegate to stu
}

// Option 4: pure composition
class StudentEmployee implements Student, Employee {
    private Student stu;
    private Employee emp;
    // Employee methods delegate to emp, Student methods delegate to stu
}
```

- a) 1
- b) 2
- c) 3
- d) 4

---

### Question 13

What does the following code print?

```java
import java.util.function.Predicate;
import java.util.List;

public class Demo {
    public static void main(String[] args) {
        List<String> ingredients = List.of("salt", "sugar", "pepper", "oil");
        int minLength = 4;
        Predicate<String> longEnough = s -> s.length() >= minLength;
        long count = ingredients.stream().filter(longEnough).count();
        System.out.println(count);
    }
}
```

- a) 2
- b) 4
- c) 3
- d) A compilation error, because `minLength` is not declared `final`

---

### Question 14

A team is designing a recipe search feature. They write the following functional interface:

```java
@FunctionalInterface
interface RecipeNamer {
    String accepts(Recipe recipe);
}
```

A reviewer suggests replacing `RecipeNamer` with a standard Java library type. Which standard type is the best replacement?

- a) `Function<Recipe, String>`
- b) `Consumer<Recipe>`
- c) `Predicate<Recipe>`
- d) `Runnable<Recipe>`

---

### Question 15

Consider the following two versions of a `Recipe` class:

**Version A:**
```java
public class Recipe {
    public List<MeasuredIngredient> ingredients;
    public String name;
}
```

**Version B:**
```java
public class Recipe {
    private List<MeasuredIngredient> ingredients;
    private String name;

    public List<MeasuredIngredient> getIngredients() {
        return Collections.unmodifiableList(ingredients);
    }

    public String getName() { return name; }
}
```

A developer later needs to enforce the invariant that a `Recipe` must always have at least one ingredient. Which version makes this change easier, and why?

- a) Version A, because public fields allow any module to add ingredients directly without modifying `Recipe`
- b) Version B, because `Collections.unmodifiableList` already enforces the minimum-ingredient invariant at runtime
- c) Version A, because encapsulating the list in an accessor method increases coupling between `Recipe` and its callers
- d) Version B, because private fields let `Recipe` control all mutations and enforce the invariant in one place

---

### Question 16

The following code intends to create an immutable `Quantity` object representing a measured amount:

```java
public final class Quantity {
    private final String[] labels;

    public Quantity(String[] labels) {
        this.labels = labels;
    }

    public String[] getLabels() {
        return labels;
    }
}
```

Identify the reason why this class is *not* immutable.

- a) The class is marked `final`
- b) The field `labels`
- c) The `String` class is a reference type
- d) The `getLabels` method

---

### Question 17

Phil sees the following code:

```java
public class Interval {
    private final int left, right;

    public Interval(int left, int right) {
        this.left = left;
        this.right = right;
    }

    // is this value within this interval (exclusive)
    public boolean inside(int value) {
        ...
    }
}
```

How many different kinds of scenarios (not number of tests, but number of distinct cases) should Phil test for to verify the correctness of this `inside` method?

- a) 1
- b) 2
- c) 3
- d) 4
- e) 5

---

### Question 18

Which of these testing techniques *guarantees* bug-free code?

- a) All automated unit tests pass with 100% line and branch coverage
- b) All automated end-to-end tests pass
- c) All manual tests pass
- d) None of the other options

---

### Question 19

A student writes a `Product` class that represents a product on Amazon. A product has a name, price and an average review rating. Upon searching on the website, a list of relevant products is identified and displayed. The user can arrange this list by price, product name and average reviews. All of these arrangements are achieved by sorting the list. Which is the best way to compare two products?

- a) `Product` should implement `Comparable`: the class is now self-contained
- b) `Product` should implement custom methods, one for each of price, name, average reviews, etc.
- c) `Product` should remain as-is. One or more `Comparator` objects should be implemented
- d) A separate class with several custom methods should be implemented, one each for comparing two products by a specific field.

---

### Question 20

There are two kinds of publication classes: `Book` and `Article`. Each class stores its own fields and operations (such as producing citations according to specific citation styles). Select all the possible consequences of this design choice (each correct answer will get you points, each wrong answer will cause a deduction):

- a) It simplifies reading individual domain classes because each class exposes fewer methods, reducing cognitive load during code reviews and onboarding
- b) It reduces the representational gap by co-locating data and behavior
- c) It makes it easy to add new kinds of operations on publications without changing much existing code
- d) It makes it easy to add new kinds of publications without changing much existing code

---

### Question 21

In the hexagonal architecture, ports are interfaces that exist on the boundary of the *domain* and "everything else". A *driving* port is an interface that is implemented by the domain objects but used by external components. Which of the following is/are an implementation of a driving port? (Select all that apply)

- a) Service implementation
- b) Controller in an MVC application
- c) API used by clients to access/utilize core functionality
- d) Databases that provide data for domain objects

---

### Question 22

A developer is writing a unit test for `Stock` that calls an external API to query historical stock prices. The company is billed a fixed amount for unlimited API calls per week. Select the most prudent testing strategy for this.

- a) Use the code as-is with the API since automated tests can run quickly
- b) Write fake substitutes for the API to use for automated testing
- c) Consolidate the testing schedule so that tests are run only within specified time periods
- d) Use loggers inside the production-level `Stock` code to log steps, and test those logs

---

### Question 23

Amit has the following: a `MyList` interface that represents a list, a `MyListImpl` class that implements `MyList`. He now makes a `MyStack` interface that represents a stack and writes the following code:

```java
class MyStackImpl<T> implements MyStack<T> {
    private MyList<T> list;

    public MyStackImpl() {
        list = new MyListImpl<T>();
    }

    public void push(T object) {
        list.add(object);
    }
    ...
}
```

Select all the advantages of this design (each correct answer will get you points, each wrong answer will cause a deduction):

- a) This design controls which methods are exposed as `public` for `MyStackImpl`: none of the `MyListImpl` methods are exposed by default
- b) This design avoids the flaky inheritance problem of overriding a public method that changes the behavior of another public method that was not overridden
- c) This class can be effectively tested to ensure that it is using the list correctly
- d) This design has fewer lines of code than if inheritance was used




---


## Part II: Case Studies (1 multi-part question)

Answer each sub-part in a few sentences. Point values are shown next to each subpart.

### Case Study 1: Weather Monitoring

You are given the following class, which is part of a weather alert system:

```java
public class WeatherAlertService {
    public void checkAndAlert(String city) {
        WeatherApiClient client = new WeatherApiClient();
        double tempF = client.getCurrentTemperature(city);
        if (tempF > 100.0) {
            AlertSender sender = new AlertSender();
            sender.sendAlert(city, "Extreme heat warning: " + tempF + "°F");
        }
    }
}
```

When methods in `WeatherApiClient` are called, they in turn call a weather API to return actual temperature data. `AlertSender` sends an SMS message.

A developer reports the following bug: alerts are being sent for cities that are not actually experiencing extreme heat.

You suspect the bug is in the temperature comparison logic. Specifically, that the threshold check uses `>` instead of `>=`, causing alerts to fire one degree too early.

**(a)**[7 points] A colleague suggests just running the app repeatedly with different cities until an alert fires, then checking whether the temperature was actually above 100°F. Explain why this is not a reliable debugging strategy.<!-- space: 3.5in -->

**(b)** [12 points] Another colleague suggests writing a fuzzy test for this: generate a large number of random city names and checking whether any of their temperatures was actually above 100°F. Explain why this technique too, is practically difficult to use.<!-- space: 3.5in -->

**(c)** [12 points] After thinking through the above suggestions carefully, you decide that a good strategy is to write a unit test that verifies the alert is sent when the temperature is exactly 100.0°F, and that no alert is sent when the temperature is 99.9°F. Explain why the current implementation of `WeatherAlertService` makes this test impossible to write as-is. Be specific: exactly what aspects make it so.<!-- space: 3.5in -->

**(d)** [12 points] In order to make `WeatherAlertService` testable, its design needs to change. Provide a point-wise description of the changes you would make. You do not have to write the code, just a description will suffice. <!-- space: 3.5in -->

**(e)** [15 points] Write a complete JUnit test that uses your design from Part (d) to verify specifically the scenario in Part (c). Code is expected for this part.<!-- space: 3.5in -->

**Useful example from class:** These code examples from class may be helpful to remind you of how to write a test and use Mockito (if you need to in your answers):

```java
@Test
public void activatesHeatingWhenBelowTarget() {
    // Create test double of the TemperatureSensor object
    TemperatureSensor mockSensor = mock(TemperatureSensor.class);
    
    // Configure the stub behavior: when readTemperature is called
    // with the argument "livingRoom", return 65.0
    when(mockSensor.readTemperature("livingRoom")).thenReturn(65.0);
    
    // Alternative: when readTemperature is called with any integer argument, return 65.0. Similarly there is anyInt().
    when(mockSensor.readTemperature(anyString())).thenReturn(65.0);

    // Verify: setMode was called with arguments HVACMode.HEATING
    // and "livingRoom"
    verify(mockHVAC).setMode(HVACMode.HEATING, "livingRoom");

    // Verify: activate was called with any string argument
    verify(mockHVAC).activate(anyString());

}
```

---

# Answers

## Part I: Multiple Choice/Answers

| # | Answer | Topic |
|---|--------|-------|
| 1 | a, b | Command Design Pattern -- map approach has extra setup cost and can't handle parameterized commands |
| 2 | a, d | Fuzzy Testing -- non-deterministic; may throw unexpected exceptions |
| 3 | b | Java setup -- definition of Java bytecode |
| 4 | d | General Java coding -- byte range is -128 to 127, cannot store values up to 500 |
| 5 | a, c | Inheritance and Polymorphism -- advantages of abstract classes over interfaces |
| 6 | c | Dynamic dispatch -- c starts at 1, +1=2; c2 starts at 1, +2 then +3=6 |
| 7 | c | Data structures -- ArrayList with indexed access is efficient |
| 8 | d | Specifications and Contracts -- symmetry/transitivity of equals broken across subclasses |
| 9 | a | hashCode and equals -- default equals uses reference identity; both entries kept |
| 10 | d | SOLID -- Liskov Substitution Principle |
| 11 | b | Interfaces and abstract classes -- one abstract class, multiple interfaces allowed |
| 12 | c, d | Inheritance and composition -- options 3 and 4 are valid in Java |
| 13 | c | Functional Programming -- salt(4), sugar(5), pepper(6) pass; oil(3) does not |
| 14 | a | Functional Programming II -- Function<Recipe, String> matches String-returning interface |
| 15 | d | Information Hiding -- private fields allow enforcing invariants in one place |
| 16 | d | Immutability -- getLabels exposes mutable array reference |
| 17 | e | Program Debugging -- 5 cases: below left, at left, inside, at right, above right |
| 18 | d | Write tests -- no technique guarantees bug-free code |
| 19 | c | omparison -- multiple sort orders call for multiple Comparators |
| 20 | b, d | OO Design -- co-locating data and behavior; easy to add new publication types |
| 21 | a, c | Hexagonal Architecture -- driving port implementations |
| 22 | b | Test Doubles -- use fakes to avoid real external API calls |
| 23 | a, b | Dependency Injection -- composition controls exposure and avoids flaky inheritance |

## Part II: Case Studies (1 multi-part question)

todo