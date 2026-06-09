## Command Design Pattern

### 1

Select the option below that best supports the following statement: *The command design pattern promotes changeability (future changes can be accommodated without extensive changes to existing code)*:

    * Creating a command interface means all future operations can be implemented using methods that have the same signature.
    * Any future operations can be implemented only using existing command objects, so no existing code will have to be changed.
    * A new operation in the future can be implemented using most of the new code in its own class, with minimal changes to code that uses command objects (C)
    * Any future operations can be implemented without any changes to existing services, thanks to the use of the command design pattern

### 2

Consider this code that uses the command design pattern to streamline a CLI:

```java

public ThermostatCommand process(String command) {
    String[] parts = command.split(" ");
    ThermostatCommand commandObject = null;
    if (parts[0].equals("create")) {
        commandObject = new CreateThermostatCommand(parts[1],Integer.parseInt(parts[2]));
    } else if (parts[0].equals("increment")) {
        commandObject = new ChangeTemperatureCommand(parts[1],TemperatureChangeType.Increment);
    } else if (parts[0].equals("decrement")) {
        commandObject = new ChangeTemperatureCommand(parts[1],TemperatureChangeType.Decrement);
    } else if (parts[0].equals("get")) {
        //System.out.println(service.getTemperature(parts[1]));
        commandObject = new GetTemperatureCommand(parts[1]);
    } else if (parts[0].equals("addmonitor")) {
        //service.enableMonitoring(parts[1], new PrintMonitorAdapter());
        commandObject = new AddMonitorCommand(parts[1],new PrintMonitorAdapter());
    }
    return commandObject;

}

```

Paul believes he can make this code even shorter. His idea is to store command objects in a `Map<String,ThermostatCommand>` object. Then the above method can be rewritten as:

```java
private Map<String,ThermostatCommand> commandMap;

...

public ThermostatCommand process(String command) {
    String[] parts = command.split(" ");
    ThermostatCommand commandObject = null;
    //get the corresponding pre-made command object, or return null
    commandObject = commandMap.getOrDefault(parts[0],null);
    return commandObject;
}

```

Select all options below that either make this design infeasible, or undesirable (Each correct answer will get you points, each wrong answer will be a deduction)

    * Although this method is short, code overall is not necessarily shorter: extra code must be written to populate this map (C)
    * This won't work because command objects cannot be "pre-made" and put into the map. (C)
    * This code is significantly less readable because the reader must know how a map lookup works.
    * This code is significantly slower than the first implementation.

## Fuzzy Testing

### 1 

Paul was given a class below: 

```java
//numerator be any number. Denominator can be either positive or negative
public record Fraction(int numerator,int denominator) implements Comparable<Fraction> {
    
    public Fraction {
        if (denominator==0) {
            throw new IllegalArgumentException("Denominator cannot be 0");
        }
    }

/**
 * Two fractions are equal if they evaluate to the same decimal value. 
 * Note that two equal fractions need not have the same values for 
 * numerator and denominator (e.g. 1/2 and 2/4)
 */
    public boolean equals(Object o) {
        if (o==this) {
            return true;
        }
        if (o instanceof Fraction f) {
            //a/b == c/d if ad = bc
            return this.numerator * f.denominator == f.numerator * this.denominator;
        }
        return false;
    }

    public int hashCode() {
        ...
    }

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

    * This test is not deterministic: it is difficult to replicate a failure (C)
    * This test will execute too slowly for it to be useful
    * This test only uses positive numbers for the fractions
    * This test may encounter unexpected exceptions and therefore may fail for unexpected reasons (C)

### 2

Paul was given a class below: 

```java
//numerator be any number. Denominator can be either positive or negative
public record Fraction(int numerator,int denominator) implements Comparable<Fraction> {
    
    public Fraction {
        if (denominator==0) {
            throw new IllegalArgumentException("Denominator cannot be 0");
        }
    }

/**
 * Two fractions are equal if they evaluate to the same decimal value. 
 * Note that two equal fractions need not have the same values for 
 * numerator and denominator (e.g. 1/2 and 2/4)
 */
    public boolean equals(Object o) {
        if (o==this) {
            return true;
        }
        if (o instanceof Fraction f) {
            //a/b == c/d if ad = bc
            return this.numerator * f.denominator == f.numerator * this.denominator;
        }
        return false;
    }

    public int hashCode() {
        ...
    }

}

```

Paul decides to test the `equals` method using a fuzzy test, as below:

```java
@Test
public void testEquals() {
    //create a random number generator
    Random r = new Random(300);

    for (int i=0;i<100000;i+=1) {
        int a = r.nextInt();
        int b = r.nextInt();
        int c = r.nextInt();
        int d = r.nextInt();

        if (b==0) {
            b = 1;
        }

        if (d==0) {
            d = 1;
        }

        Fraction f1 = new Fraction(a,b);
        Fraction f2 = new Fraction(c,d);

        assertEquals(a*d==b*c,f1.equals(f2));
    }
}

```

When the professor docks points because Paul did not test for cases where the fraction is zero, Paul countered saying that surely the test picked at least one such case because he tried 100000 times. Should Paul get the points back?

    * Yes, precisely because of the choice of a large sample size, 100000.
    * No, the test does not guarantee that a specific input is tested (C)
    * Yes, because the way the `assertEquals` is written will work if either `f1` or `f2` is zero.
    * No, because he chose the wrong seed for the random number generator.


## User Centered Design

### 1

Determined to do better after the last project that had several last-minute overhauls, Paul has decided to embrace user-centered design in the next project. However after a couple of iterations, he receives pushback from his team. They observe that the users are not consistent in their feedback about how some features should work, and as a result the project is not going as fast as it would without user-centered design. What conclusions should Paul draw from this?

    * User-centered design has increased overhead and may not apply to all projects
    * Involving users throughout the project has increased volatility risk: the project would have otherwise run more smoothly and would be successful
    * Inconsistency in user feedback signals that involving users has surfaced volatility risk that always existed but otherwise may have gone undetected. (C)
    * Users are not sure what they want. Domain experts should be brought in to advise the users on what will work best for them.
### 2

State Farm Insurance, a large insurance company, has hired a contractor firm to design, implement and maintain a smart phone app for their insurance customers to avail of roadside assistance. This will be a 6 month project. The contractor company includes a term in their contract: they wish to meet with some State Farm customers every two weeks for the first 2 months and at least monthly for the rest of the project. State Farm is hesitant because this would require more costs: finding and incentivizing a group of customers to do this. Select all the possible reasons why State Farm Insurance should agree to this despite the extra cost (Each correct answer will get some credit, each wrong answer will get a deduction):

    * The contractor is well-known in their community for on-time completion of projects. State Farm should not let this opportunity go.
    * Meeting with the users regularly will significantly increase the probability that the contractor will deliver a user-friendly app that the users will adopt. (C)
    * Meeting with the users will reduce risk of the contractor misunderstanding or missing what the users need. (C)
    * The contractor has former employees from State Farm, so presumably they have an advantage over other contractors.

### 3

In the CYB application, a team wants to unit-test recipe-scaling logic without starting the application using the JavaFX GUI. Which design decision enables this?

    * Implementing event handlers as anonymous classes rather than lambdas for easier subclassing
    * Using FXML so the controller can be loaded and instantiated without requiring a Stage
    * Keeping all business logic in the Model as plain Java classes with no UI dependencies (C)
    * Registering all callbacks on the JavaFX Application Thread so tests can synchronize reliably

## Accessibility and Inclusivity

### 1

In MVC for CookYourBooks, recipe scaling now also recalculates nutritional totals. Where should the recalculation logic be implemented?

    * The View (FXML file), because nutritional totals will be displayed and formatted there
    * Both the Controller and the View, splitting responsibility to avoid overloading either layer
    * The Controller, because it coordinates all data flow between View and Model
    * The Model (`Recipe.java`), because business logic belongs in the Model (C)

### 2

Version A uses a custom `<div>` styled to look like a button. Version B uses a native `<button>` element. Which version is more accessible for a visually impaired user, and which POUR principle *best* explains why?

    * Version A, under Perceivable — custom-styled components give designers full visual and structural control over the interface
    * Version B, under Robust — native semantic elements automatically expose their role and state to assistive technologies via accessibility APIs (C)
    * Version A, under Operable — CSS-styled divs have lower rendering overhead and therefore respond more quickly to keyboard input
    * Version B, under Understandable — native button elements use familiar language and behavior that better matches the user's mental model


## Concurrency

### 1

Ellen is adding a feature to SceneItAll enabling users to check the total energy usage by clicking on a button. Each device is then asked its current energy usage so the total can be calculated and reported. Which of the following steps in this use-case should be done in a background thread (as opposed to the JavaFX thread)?

    * Handle the button click to make the request (i.e. the handler function for the button click)
    * Create a popup enabling cancelling the request
    * Contact the devices and total their responses (C)
    * Display the result

### 2

Ellen wants to build an application with a responsive GUI. She knows that operations that touch the GUI must be run in the JavaFX thread, and high-latency (slow) operations should be run in a background thread. Which of these operations can be done equally well on either type of thread?

    * Changing the display between dark mode and light mode
    * Cutting power to all devices
    * Using `LocalTime.now()` to check the time of day (C)
    * Backing up all data to a server

## Concurrency 2

### 1

A SceneItAll developer needs to run Zigbee commands in a `DeviceCommandSender` class that should inherit some functionality from `HubComponent`. Which approach correctly runs the command in a separate thread?

    * `class DeviceCommandSender extends HubComponent implements Runnable`, override `run()`, and pass an instance to `new Thread(...).start()` (C)
    * `class DeviceCommandSender extends Thread, HubComponent` and override `run()` — Java supports multiple inheritance here
    * `class DeviceCommandSender extends Thread` and override `run()`, dropping the required `HubComponent` superclass
    * `class DeviceCommandSender extends HubComponent`, annotate `run()` with `@Threaded`, and call `.start()`

### 2

A `StepCounter` has `private int steps = 0` and `stepAhead()` does `steps++`. Ten threads each call `stepAhead()` once. Why might `getSteps()` return less than 10?

    * `int` is not valid for shared mutable fields; only `long` or `AtomicInteger` supports safe multi-threaded reads
    * Java guarantees `int` reads are atomic, so the problem must be a visibility issue from CPU cache coherence delays
    * The JVM silently rounds down concurrent increments for performance, discarding some writes when contention is high
    * `steps++` is not atomic — it reads, increments, and writes in three steps, so two threads may read the same stale value (C)

## Performance

### 1

Version A searches a `List<Device>` with a for-each loop. Version B uses `HashMap.get()`. As the number of devices grows, how do these two versions behave?

    * Both versions slow down similarly
    * Version A is far slower than Version B (C)
    * Version B is far slower than Version A
    * Which version is faster depends on whether `ArrayList` or `LinkedList` was used in Version A

### 2

Version A searches an `ArrayList<Device>` with a for-each loop, which internally uses an iterator. Version B uses a `LinkedList<Device>` with a for-each loop. Neither list is sorted in any way. As the number of devices grow, how do these two versions behave?

    * Both versions slow down similarly (C)
    * Version A is far slower than Version B
    * Version B is far slower than Version A
    * None of the above

## Java setup (JVM, compilation and interpretation)

### 1

Java promises "write once, run anywhere". This means that code written in Java can be executed on any Java-supported operating system, and one does not have to maintain separate versions of the same application for each operating system. Select the most accurate option below that describes how Java accomplishes this.

    * Java provides a library that allows creating an installer for each Java-supported operating system without having to rewrite the Java source code
    * The bytecode generated by the Java compiler (javac) can be executed on a JVM (java) running on any Java-supported operating system without any changes to it (C)
    * Through a build system such as Gradle, Java streamlines and simplifies maintaining the same application on multiple operating systems.
    * The JDK provides multiple versions of each of its inbuilt classes, and the JVM on a specific operating system automatically selects the correct one when running the application.

### 2

Select the option below that most accurately describes `Java bytecode`.

    * Bytecode is the operating-system-specific binary executable file that is produced when a Java application is built.
    * Bytecode is a lower-level representation that can be executed without any modifications on any Java-supported operating system by using the JVM (the `java` program) (C)
    * Bytecode is Java code that is compliant with modern 64-bit operating systems (hence the name "byte" code)
    * Bytecode is produced specifically when a Java project uses Gradle

## General Java coding

### 1

Consider the following Java code:

```java
void doubleValue(int x) {
    x = x * 2;
}

int quantity = 10;
doubleValue(quantity);
System.out.println(quantity);
```

What is printed?

    * 20
    * 5
    * 10 (C)
    * A compilation error occurs because reassigning a parameter inside a method is not allowed

### 2

A developer stores serving counts for every recipe in a large recipe database using `long` (8 bytes per entry). The maximum serving count for any recipe is 500. A code reviewer suggests switching to `byte` (1 byte per entry). Why would this change be problematic?

    * `byte` values cannot be used in arithmetic operations in Java and must first be cast to `int`
    *  `byte` is a reference type, so it cannot store numeric values directly and requires autoboxing
    *  The JVM requires all numeric fields in a class to use the same type for memory alignment purposes
    *  `byte` may not be able to store serving counts in all cases (C)

### 3

Consider the following Java code:

```java
void appendIngredient(String[] ingredients, int index) {
    ingredients[index] = "salt";
}

String[] list = {"flour", "water", "sugar"};
appendIngredient(list, 1);
System.out.println(list[1]);
```

What is printed?

    * `salt` (C)
    * A `NullPointerException` is thrown at runtime because `ingredients` is null when dereferenced
    * `water`
    * A compilation error occurs because Java does not allow arrays to be used as method parameters

## Inheritance and Polymorphism

### 1

Select all the advantages of using abstract classes over interfaces (Each correct answer will get you points, each wrong answer will be a deduction)

    * Abstract classes can have mutable fields but interfaces cannot (C)
    * Abstract classes can have public methods but interfaces cannot
    * Abstract classes can have non-public abstract methods (C)
    * A class can extend multiple abstract classes but not implement multiple interfaces 

### 2

Select all the advantages of using interfaces over abstract classes (Each correct answer will get you points, each wrong answer will be a deduction)

    * Interfaces always provide a minimalistic view of objects (only what they can do) whereas abstract classes may not (C)
    * Interfaces can have public methods but abstract classes cannot
    * Interfaces can have non-public abstract methods but abstract classes cannot
    * A class cannot extend multiple abstract classes but can implement multiple interfaces (C)
  

## Dynamic dispatch

### 1

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
    }

    public CountTwo() {
        jump = 2;
    }

    public void increment() {
        counter += jump;
        jump +=1;
    }
}

public static void main(String []args) {
    Counter c2 = new CounterTwo(1);
    Counter c = new CounterOne(1);

    c2.increment();
    c.increment();
    System.out.println(c.getCount());
    c = c2;
    c.increment();
    System.out.println(c.getCount())
}

```

What is printed when this program is run?

    * 2 3
    * 3 4 
    * 2 6 (C)
    * 2 4

### 2

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
        jump +=1;
    }
}

public static void main(String []args) {
    Counter c2 = new CounterTwo(2);
    Counter c = new CounterOne(4);

    c2.increment();
    c.increment();
    System.out.println(c.getCount());
    c = c2;
    c.increment();
    System.out.println(c.getCount())
}

```

What is printed when this program is run?

    * 5 6
    * 4 5 
    * 5 7 (C)
    * 5 5

### 3

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
        count += jump;
        jump +=1;
    }
}

public static void main(String []args) {
    Counter c2 = new CounterTwo(-1);
    Counter c = new CounterOne(0);

    c2.increment();
    c.increment();
    System.out.println(c.getCount());
    c = c2;
    c.increment();
    System.out.println(c.getCount())
}

```

What is printed when this program is run?

    * 1 2
    * 2 3
    * 1 4 (C)
    * 2 5

## Data structures in Java, exceptions and file I/O

### 1

A vehicle is equipped with a GPS device that records the GPS location of the vehicle every 2 minutes when the vehicle is in operation. Prof Shesh asks students to write a class that will maintain this data in a list, and support appending new locations to that list. It also has a method that "summarizes" the journey. It does so by returning the locations at the first, one-third, two-thirds and last locations of this vehicle in a list.

Jon writes the following code:

```java

public record class GPSLocation(double longitude,double latitude);

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
        summary.add(readouts.get(readouts.size()/3));
        summary.add(readouts.get(2*readouts.size()/3));
        summary.add(readouts.get(readouts.size()-1));
        return summary;
    }
}

```

The grading rubric for this assignment was as follows:
    * 0 points: code works incorrectly
    * 1 point: code works correctly but could be more efficient
    * 2 points: code walks correctly and data represented efficiently

What grade should Jon receive?

    * 0
    * 1
    * 2 (C)

### 2

A vehicle is equipped with a GPS device that records the GPS location of the vehicle every 2 minutes when the vehicle is in operation. Prof Shesh asks students to write a class that will maintain this data in a list, and support appending new locations to that list. It also has a method that "summarizes" the journey. It does so by returning the locations at the first, one-third, two-thirds and last locations of this vehicle in a list.

Jon writes the following code:

```java

public record class GPSLocation(double longitude,double latitude);

class LocationStore {
    private List<GPSLocation> readouts;

    public LocationStore() {
        readouts = new LinkedList<GPSLocation>();
    }

    public void appendLocation(GPSLocation loc) {
        readouts.add(loc);
    }

    public List<GPSLocation> getSummary() {
        List<GPSLocation> summary = new LinkedList<GPSLocation>();
        summary.add(readouts.get(0));
        summary.add(readouts.get(readouts.size()/3));
        summary.add(readouts.get(2*readouts.size()/3));
        summary.add(readouts.get(readouts.size()-1));
        return summary;
    }
}

```

The grading rubric for this assignment was as follows: 
    * 0 points: code works incorrectly
    * 1 point: code works correctly but could be more efficient
    * 2 points: code walks correctly and data represented efficiently

What grade should Jon receive?

    * 0
    * 1 (C)
    * 2

## Specifications and Contracts

### 1

A team is writing a specification for a `findDevice` method. Developer A writes:

> *"Iterates through each device in the list from index 0 upward; if the device's ID matches `targetId`, immediately returns that device; if the end of the list is reached without a match, throws `NoSuchElementException`."*


Developer B writes:

> *"Returns a device from the list whose ID equals `targetId`."*
> `@throws NoSuchElementException if no device has the given ID`

Which specification quality property (from the set: clarity, restrictiveness, generality) does Developer B's version improve upon?

    *  Restrictiveness, because Developer B's version clarifies the required behavior when `targetId` is null
    *  Clarity, because the `@throws` tag Developer B adds describes the behavior more clearly
    *  Generality, because Developer B's version omits the traversal order, allowing any correct implementation strategy (C)
    * Generality, because Developer B's version removes the exception clause entirely, permitting implementations that return null

### 2

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

    * It would cause a `StackOverflowError` because `TunableWhiteLight.equals` would call `DimmableLight.equals` recursively
    *  It would cause `instanceof` to always return `false` when comparing objects of different subclasses
    *  It would prevent `hashCode` from compiling, because `hashCode` must have the same parameter types as `equals`
    *  It would break the symmetry or transitivity of `equals`, since the result would differ depending on which object's `equals` is invoked (C)

## Comparison

A student writes a `Product` class that represents a product on amazon. Upon searching on the website, a list of relevant products is identified and displayed. The user can arrange this list by price, product name and average reviews. All of these arrangements are achieved by sort the list. Which is the best way to compare two products?

    * `Product` should implement `Comparable`: the class is now self-contained
    * `Product` should implement custom methods, one for each of price, name, average reviews, etc.
    * `Product` should remain as-is. One or more `Comparator` objects should be implemented (C)
    * A separate class with several custom methods should be implemented, one each for comparing two products by a specific field.


## hashCode and equals

### 1

For a class, a student overrides `hashCode` correctly and then overrides `equals` that implements the logic "two objects are equal if their hashcode methods return the same value". What is the problem with this logic?

    * It is possible for two distinct objects to return the same hashcode (C)
    * The equals method is not consistent with hashcode
    * The only problem that may occur is if a subclass overrides equals but not hash code
    * The only problem that may occur is if a subclass overrides both equals and hashcode

### 2

A developer overrides `hashCode` in a class `X` but forgets to override `equals`, leaving `equals` as the default `Object.equals` (reference equality). What is the most likely observable consequence when two distinct `X` objects with identical fields are added to a `HashSet<X>`?

    * Both objects always appear as separate entries, because the default `equals` uses reference identity and considers the two objects distinct (C)
    * A `HashSet` uses only `hashCode` for deduplication, so the two objects will correctly be treated as one entry in the set
    * The compiler will reject the code with an error because `equals` and `hashCode` must always be overridden together in Java
    * The `HashSet` will throw an `IllegalStateException` when the second object is added, detecting the contract violation at runtime

## Serialization and Persistence

### 1

In an assignment this semester, you implement JSON serialization using the Jackson library. Specifically you added annotations such as ```@JsonTypeInfo``` and ```@JsonProperty``` to your domain classes. At the end of the semester, Ellen is thinking more deeply about this implementation. Select all statements below made by Ellen that are true (Each correct option you select will earn you more points, each wrong option will cause a deduction):

    * Only JSON files produced by Jackson during serialization of an object can be used to deserialize it. A manually typed JSON file that accurately complies with the expected structure produced by Jackson during serialization will still not work.
    * The domain classes that use such annotations are strongly coupled to a specific JSON serialization. Forgoing JSON in favor of another format of serialization in the future will require extensive changes in code. (C)
    * The existing classes are effectively "locked in". Subclasses cannot be written in the future because that would require changes to these annotations.
    * This code may break if there is a bug in the Jackson library, now or in the future. (C)

### 2

In an assignment this semester, you implement JSON serialization using the Jackson library. Specifically you added annotations such as ```@JsonTypeInfo``` and ```@JsonProperty``` to your domain classes. At the end of the semester, Ellen is thinking more deeply about this implementation. Select all statements below made by Ellen that are false (Each correct option you select will earn you more points, each wrong option will cause a deduction):

    * Only JSON files produced by Jackson during serialization of an object can be used to deserialize it. A manually typed JSON file that accurately complies with the expected structure produced by Jackson during serialization will still not work. (C)
    * The domain classes that use such annotations are strongly coupled to a specific JSON serialization. Forgoing JSON in favor of another format of serialization in the future will require extensive changes in code.
    * The existing classes are effectively "locked in". Subclasses cannot be written in the future because that would require changes to these annotations. (C)
    * This code may break if there is a bug in the Jackson library, now or in the future.


## SOLID principles

### 1

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

    * Single Responsibility Principle, because `BrokenLight` is both a light and an error reporter
    * Interface Segregation Principle, because the `Light` interface is too large and should be split into separate `Switchable` and `Dimmable` interfaces
    * Open/Closed Principle, because `BrokenLight` modifies the behavior of the existing `Light` class
    * Liskov Substitution Principle, because a `BrokenLight` cannot be used wherever a `Light` is expected without breaking the caller (C)



### 2

A developer writes the following class:

```java
public interface Shape {
    double area();
    Shape resize(float scaleFactor);
}

public class AbstractShape implements Shape {
    ...
    protected boolean sameCircle(Circle other) {
        return false;
    }

    protected boolean sameRectangle(Rectangle other) {
        return false;
    }

}

public class Circle extends AbstractShape {
    ...
    public boolean equals(Object o) {
        if (this==o) {
            return true;
        }
        if (o instanceof Circle other) {
            return other.sameCircle(this);
        }
        return false;
    }
    public boolean sameCircle(Circle other) {
        return this.getRadius()==other.getRadius();
    }
}

public class Rectangle extends AbstractShape {
    //similar implementations of equals and equalsRectangle as above
}



```

Everytime a new type of shape is created, the ```AbstractShape``` class has to include a new ```sameXXX``` method in it. Which SOLID principle does this design violate?

    * Single Responsibility Principle, because `AbstractShape` mixes many different types of shapes in it
    * Dependency Inversion Principle, because `AbstractShape` depends on its subclasses (C)
    * Interface Segregation Principle, because the `sameCircle` and `sameRectangle` methods are not part of the `Shape` interface
    * Liskov Substitution Principle, because a subclass written in the future may violate the specifications of `Shape` and `AbstractShape`



## Interfaces and abstract classes

### 1
Select the most accurate statement about abstract classes and interfaces.

    * A class may extend at most one abstract class and at most one interface

    * A class may extend at most one abstract class and multiple interfaces (C)

    * A class may extend several abstract classes and multiple interfaces 

    * A class may extend at most one abstract class or multiple interfaces but not both.

### 2
Select the most accurate statement about using abstract classes and interfaces at the top of an inheritance hierarchy.

    * Use an interface if several classes have only common methods, use an abstract class if they have common methods and fields (C)

    * Whether several classes have only methods in common or both methods and fields in common, using an interface is always better than using an abstract class

    * Whether several classes have only methods in common or both methods and fields in common, using an abstract class is always better than using an interface

    * Abstract classes and interfaces are redundant: there is no advantage to using one over the other in any situation

### 3

Henry wonders if all the interfaces in his large Java program can be made into abstract classes, without any other restructuring (such as combining multiple interfaces into a single interface). Can he change all the interfaces into abstract classes without changing the behavior?

* Yes, there is no difference between an interface and an abstract class that contains only abstract methods.
* Yes, all interfaces can be converted into abstract classes, but the program would be less efficient.
* No, this won't work if any class in the original implements multiple interfaces. (C)
* No, this won't work if any interface in the original extends another interface.

## Inheritance and composition

You are given the following Java code:

```java

interface Student {...}
interface Employee {...}
class SimpleStudent implements Student {...}
class BasicEmployee implements Employee {...}

```

You have to represent a student-employee: a person that has both student and employee privileges at Northeastern University. CoPilot gives you the following choices to do this:

```java
//Option 1: inheritance
class StudentEmployee extends SimpleStudent, BasicEmployee {
    ...
    //Student and Employee methods are inherited
}

//Option 2: inheritance + composition
class StudentEmployee extends SimpleStudent {
    private Employee emp;
    ...
    //Student methods are inherited, Employee methods delegate to emp
}

//Option 3: inheritance + composition
class StudentEmployee extends BasicEmployee implements Student {
    private Student stu;
    ...
    //Employee methods are inherited, Student methods delegate to stu
}

//Option 4: pure composition
class StudentEmployee implements Student, Employee {
    private Student stu;
    private Employee emp;
    ...
    //Employee methods delegate to emp, Student methods delegate to stu
}

```

Which of the above options are closest to a correct and working `StudentEmployee` (Select all that apply):

    * 1
    * 2
    * 3 (C)
    * 4 (C)

#### 2

You are given the following Java code:

```java

interface WifiRouter {...}
interface EthernetHub {...}
class SimpleRouter implements WifiRouter {...}
class BasicHub implements EthernetHub {...}

```

You have to represent a hybrid device that acts as a wifi-router and has ethernet ports to serve as a hub (many routers on the market actually do this). CoPilot gives you the following choices to do this:

```java
//Option 1: inheritance
class RouterHubCombo extends SimpleRouter, BasicHub {
    ...
    //WifiRouter and EthernetHub methods are inherited
}

//Option 2: inheritance + composition
class RouterHubCombo extends SimpleRouter {
    private EthernetHub hub;
    ...
    //WifiRouter methods are inherited, EthernetHub methods delegate to hub
}

//Option 3: inheritance + composition
class RouterHubCombo extends BasicHub implements WifiRouter {
    private WifiRouter rtr;
    ...
    //EthernetHub methods are inherited, WifiRouter methods delegate to rtr
}

//Option 4: pure composition
class RouterHubCombo implements WifiRouter, EthernetHub {
    private WifiRouter rtr;
    private EthernetHub hub;
    ...
    //EthernetHub methods delegate to emp, WifiRouter methods delegate to hub
}

```

Which of the above options are closest to a correct and working `RouterHubCombo` (Select all that apply):

    * 1
    * 2
    * 3 (C)
    * 4 (C)


## Functional Programming

### 1

A log entry has a date, month, year and a single string message. You are provided a list of log entries as `List<LogEntry> logs`. Your objective is to assemble a list of all the messages for log entries between March 2025 and September 2025 had the word "severe" in it (case sensitive). You have the following snippets of code available to you:

    1. `.map(d->d.getMessage())`
    2. `.toList()`
    3. `.stream()`
    4. `.filter(d->d.month()>=3 && d.month()<=9 && d.year()==2025 && d.getMessage().contains("severe"))`

Specify the order of these operations after the code snippet `logs`.

    * 3, 1, 4, 2
    * 3, 4, 1, 2 (C)
    * 2, 4, 1, 3
    * 2, 1, 4, 3

### 2

A book has a title, year of publication, version number and publisher name. You are provided a list of log entries as `List<Book> books`. Your objective is to assemble a list of all book titles published by Penguin Publishing that had the word "Intelligence" in it (case sensitive). You have the following snippets of code available to you:

    1. `.map(d->d.title()())`
    2. `.toList()`
    3. `.stream()`
    4. `.filter(d->d.publisherName().contains("Penguin Publishing") && d.title().contains("Intelligence"))`

Specify the order of these operations after the code snippet `logs`.

    * 3, 1, 4, 2
    * 3, 4, 1, 2 (C)
    * 2, 4, 1, 3
    * 2, 1, 4, 3

### 3 

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

    * 2
    * 4
    * 3 (C)
    * A compilation error, because `minLength` is not declared `final`

## Functional Programming II

### 1


A team is designing a recipe search feature. They write the following functional interface:

```java
@FunctionalInterface
interface RecipePicker {
    boolean accepts(Recipe recipe);
}
```

A reviewer suggests replacing `RecipePicker` with a standard Java library type. Which standard type is the best replacement?

    * `Function<Recipe, Boolean>`
    * `Consumer<Recipe>`
    * `Predicate<Recipe>` (C)
    * `Supplier<Recipe>`

### 2


A team is designing a recipe search feature. They write the following functional interface:

```java
@FunctionalInterface
interface RecipeNamer {
    String accepts(Recipe recipe);
}
```

A reviewer suggests replacing `RecipeNamer` with a standard Java library type. Which standard type is the best replacement?

    * `Function<Recipe, String>` (C)
    * `Consumer<Recipe>`
    * `Predicate<Recipe>`
    * `Runnable<Recipe>`

## Information Hiding

### 1

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

    * Version A, because public fields allow any module to add ingredients directly without modifying `Recipe`
    *  Version B, because `Collections.unmodifiableList` already enforces the minimum-ingredient invariant at runtime
    *  Version A, because encapsulating the list in an accessor method increases coupling between `Recipe` and its callers
    *  Version B, because private fields let `Recipe` control all mutations and enforce the invariant in one place (C)

### 2

Several types of IoT device implementations exist. Most of them allow changing various properties of the device (e.g. turning on a light, changing the speed of a fan, etc.). Consider the following version of a `Room` class:

```java
public class Room {
    private List<IoTDevice> devices;
    private String name;

    public List<IoTDevice> getDevices() {
        return devices;
    }

    public String getName() { return name; }
}
```

A developer flags this implementation as problematic because they believe clients could change the devices in the list from outside the class (which is not the intent of this design). The writer of this class proposes several possible ways to address this:

- (i) `devices` is made `final`.

- (ii) `getDevices` is implemented to return a separate list that contains copies of the devices

- (iii) `getDevices` is implemented as `return new ArrayList<IoTDevice>(devices)`

What is the best fix for this problem?

    * only (i)
    * only (ii) (C)
    * only (iii)
    * Both (i) and (iii)

## Immutability

### 1

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

Select *all* the features below that contribute towards the immutability of this class. Each correct answer will get you points, each wrong answer will cause a deduction.

    * The class is marked `final`
    * The field `labels` is marked `final` (C)
    * The `String` class is immutable (C)
    * The `getLabels` method returns an array of objects that cannot change


### 2

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

    * The class is marked `final`
    * The field `labels`
    * The `String` class is a reference type
    * The `getLabels` method (C)


## Builder Pattern

#### 1

VegHut is a pizza place that specializes in vegetarian pizzas. Their system has the template of a vegetarian pizza. Such a pizza has the following attributes: size (enum with values SMALL, MEDIUM, LARGE), crust type (enum with values THIN, TRADITIONAL, DEEPDISH). It can have some or all of these toppings: onions, tomatoes, mushrooms, green pepper, jalapeno pepper, pineapple, spinach, olives, yellow peppers. Which of the following code examples shows the most effective design for creating pizzas?

    * `new Pizza(Size.SMALL,Crust.THIN,false,true,true,false)` where each boolean argument corresponds to a specific topping.

    * Several constructors: `new Pizza(Size.SMALL,Crust.THIN)` for cheese pizza, `new Pizza(Size.SMALL,Crust.THIN,"onions","tomatoes",...)` etc. for specific types of pizzas

    * `new Pizza(Size.SMALL,Crust.THIN,new String[]{"onions","tomatoes","jalapeno", ...})` an array of arbitrary length that explicitly lists toppings

    * `Pizza.builder().size(Size.SMALL).onions().tomatoes()...build()` (C)

#### 2

In the CYB project, the `PersonalCollectionImpl` class came with a builder. Here was its design:

```java

public final class PersonalCollectionImpl implements PersonalCollection {

  private PersonalCollectionImpl() {
    throw new UnsupportedOperationException("TODO: Implement PersonalCollectionImpl");
  }

  /** Returns a new builder for creating PersonalCollectionImpl instances. */
  public static Builder builder() {
    return new Builder();
  }

  @Override
  public String getId() {
    throw new UnsupportedOperationException("TODO: Implement PersonalCollectionImpl");
  }

  ...

  /** Builder for creating {@link PersonalCollectionImpl} instances. */
  public static final class Builder {

    /** Sets the unique identifier. */
    public Builder id(String id) {
      ...
      return this;
    }

    /** Sets the title (required). */
    public Builder title(String title) {
      ...
      return this;
    }

    ...
  }
}

```

What is the consequence of having the `builder()` method in the `PersonalCollectionImpl` class?

    * It is unusable: one would need a `PersonalCollectionImpl` object to call it, but creating such an object is precisely the purpose of the builder.

    * It is the only way to make the builder pattern work, because the builder class is always inside the class it is building.

    * It mandates that there is only one way to create a `PersonalCollectionImpl` object from outside this code. (C)

    * Its redundant: it provides no value but also does not cause any harm.

## Decorator Pattern

## Singleton and Static Factory Pattern

## Program Debugging

#### 1

Phil sees the following code:

```java

public class Interval {
    private final int left,right;

    public Interval(int left, int right) {
        this.left = left;
        this.right = right;
    }

    //is this value within this interval (inclusive)
    public boolean inside(int value) {
        ...
    }
}


```

How many different kinds of scenarios (not number of tests, but number of distinct cases) should Phil test for to verify the correctness of this `inside` method?

    * 1
    * 2
    * 3
    * 4
    * 5 (C)

### 2

Phil sees the following code:

```java

public class Interval {
    private final int left,right;

    public Interval(int l,int r) {
        left = l;
        right = r;
    }

    //is this value within this interval (exclusive)
    public boolean inside(int value) {
        ...
    }
}


```

How many different kinds of scenarios (not number of tests, but number of distinct cases) should Phil test for to verify the correctness of this `inside` method?

    * 1
    * 2
    * 3
    * 4
    * 5 (C)

## Write tests

### 1

Which of these testing techniques *guarantees* bug-free code?

* all automated unit tests pass with 100% line and branch coverage
* all automated end-to-end tests pass
* all manual tests pass
* none of the above (C)

### 2

Carol had written the following simple method:

```java

...
public double absolute(double x) {
    if (x>0) {
        return x;
    }
    return -x;
}


```

The professor took points off because Carol's submission did not have a test that specifically verified that this method worked correctly when 0 is passed to it as an argument. Carol pointed to a fuzzy test that they wrote that calls this function using 10000 random numbers and claimed that this test should be considered for this case. What should be the professor's response?

    * Given that 10000 numbers were checked, Carol's reasoning is solid. Give them the points.

    * There is no guarantee that this fuzzy test specifically checked a value of 0, so do not give them the points (C)

    * 10000 numbers were not enough to guarantee this, and Carol should have checked using far more random numbers. Give partial credit for the idea.

## Test doubles

#### 1

Amit wrote the following controller for a JavaFX application.

```java
public class AreaDashboardController {

    @FXML private Label areaNameLabel;
    ...

    private Area model;  // the Controller knows the Model

    @FXML
    private void initialize() {
        // Create model.
        model = new Area("Living Room",
            List.of(new Light("Ceiling Light", 50),
                    new Shades("Shades",true),
                    new Fan("Fan", 2)));
        ...
    }

    @FXML // ignore "is never used" warning: called from FXML
    private void handleActivateScene() {
        ...
    }

    private void updateDeviceList() {
        ...
    }
}
```

Which of the following statements are true about this design?

    * This design is unacceptable because it does not use a view-model

    * This design makes it difficult to test the controller because the `Area` object is hardwired in it. (C)

    * This controller can be tested using a test double for the model.

    * None of the above.

#### 2 

In the SceneItAll application, there are two concepts: a room and a device. A room can have several devices, and each device must belong to exactly one room. The following code was written.

```java

class SimpleRoom implements Room {
    private List<Device> devices;

    public SimpleRoom() {
        devices = new ArrayList<Device>();
    }

    public addDevice(Device device) {
        devices.add(device);
    }

    public void turnOffAllDevices() {
        for (Device d:devices) {
            d.turnOff();
        }
    }

    public String getDescription() {
        ...
    }
    ...
}

class Light implements Device {
    private Room roomWhereItBelongs;

    public Light(Room r) {
        roomWhereItBelongs = r;
    }

    public String roomName() {
        return roomWhereItBelongs.getDescription();
    }
}

```

Amit and Ellen are in a 2-person team, and they agree to divide up work between themselves. Amit believes that they have no choice: the same person has to "own" (develop and test) both the above classes. Jon believes that although these classes can be developed concurrently, no testing can happen before the code is integrated. Ellen believes that all development and most testing can be done concurrently. Which of the following statements are true?

    * Amit is correct.
    * Ellen is correct. (C)
    * Jon is correct.
    * None of the above

## OO Design

### 1

There are two kinds of publication classes: `Book` and `Article`. Both classes are plain data holders, with only relevant getters and setters. Other classes, such as `CitationService` implement the logic to operate upon each kind of publication using their (possibly unique) getters. Select all the possible consequences of this design choice (Each correct answer will get you points, each wrong answer will cause a deduction)

    * It simplifies reading individual domain classes because each class exposes fewer methods, reducing cognitive load during code reviews and onboarding
    * It increases the representational gap by separating behavior from the data it operates on, making domain logic harder to locate and reason about (C)
    * It makes it easy to add new kinds of operations on publications without changing much existing code (C)
    * It makes it easy to add new kinds of publications without changing much existing code 

### 2

There are two kinds of publication classes: `Book` and `Article`. Each class stores its own fields and operations (such as producing citations according to specific citation styles). Select all the possible consequences of this design choice (Each correct answer will get you points, each wrong answer will cause a deduction)

    * It simplifies reading individual domain classes because each class exposes fewer methods, reducing cognitive load during code reviews and onboarding
    * It reduces the representational gap by co-locating data and behavior (C)
    * It makes it easy to add new kinds of operations on publications without changing much existing code
    * It makes it easy to add new kinds of publications without changing much existing code (C)

## AI Programming Agents

### 1

A developer uses a coding agent to add a new `Shade` device type. The generated code passes the existing test suite. Six months later, the routine bricks 300 devices because of an untested edge case. Which principle best explains why running the app and observing its behavior was insufficient as an evaluation strategy?

    * Coding agents have context window limits that prevent them from seeing the full codebase
    * Evaluating only execution behavior ("vibe coding") cannot detect structural defects that only surface under uncommon inputs (C)
    * AI agents cannot generate code for new domain types without being given existing implementations as examples
    * Manual testing is always insufficient; automated tests must be written before any AI-generated code can be accepted

### 2

A developer is trying to find the source of a nasty bug in their program and seeks to use AI for help. Before opening the chat interface or writing a prompt, a developer collects: (1) the unexpected behavior, (2) the expected behavior, (3) the relevant source files, and (4) a hypothesis about the root cause. According to the 6-step workflow, which step does this correspond to?

    * Engage — the developer is deciding what context to include in the prompt
    * Evaluate — the developer is comparing actual behavior against expected results
    * Identify — the developer is recognizing what information the AI will need (C)
    * Calibrate — the developer is steering the AI toward a desired outcome

### 3

Which of the following is a limitation of AI coding agents that distinguishes them from a senior developer reviewing a pull request?

    * AI agents cannot read multiple files simultaneously, so they are unable to detect cross-class design issues that span more than one source file
    * AI agents cannot access current standard library documentation, so they must rely entirely on patterns learned during training rather than verified API references
    * AI agents cannot run the project's test suite directly, so they are unable to verify whether generated code actually passes the existing automated tests
    * They lack deep understanding of your codebase's architecture and design rationale, working with surface-level patterns rather than reasoning about system-wide consequences (C)

## Test Doubles

### 1

A developer is writing a unit test for `PaymentProcessor` that calls an external payment API to charge credit cards. The company is billed a fixed amount for unlimited API calls per week. Select the most prudent testing strategy for this.

    * Use the code as-is with the API since automated tests can run quickly
    * Create a test double of the API for automated testing (C)
    * Consolidate the testing schedule so that tests are run only within specified time periods
    * Use loggers inside the production-level `PaymentProcessor` code to log steps, and test those logs

### 2

A developer is writing a unit test for `Stock` that calls an external API to query historical stock prices. The company is billed a fixed amount for unlimited API calls per week. Select the most prudent testing strategy for this.

    * Use the code as-is with the API since automated tests can run quickly
    * Write fake substitutes for the API to use for automated testing (C)
    * Consolidate the testing schedule so that tests are run only within specified time periods
    * Use loggers inside the production-level `Stock` code to log steps, and test those logs

## Requirements and Risks

### 1 

A product manager says: *"The system shall use AI to automatically detect if a student's submission is academically dishonest."* A developer identifies this as high-risk. Which combination of risk dimensions does this requirement most clearly exhibit?

    * Low understanding risk ("academically dishonest" is a legally well-defined term) but high scope risk (the ML detection pipeline involves many components and integrations)

    * High understanding risk(AI ethics policies evolve frequently) and high volatility risk (the term "academically dishonest" is contested, but the scope of an ML classifier is relatively well-bounded) but none other

    * High understanding risk ("academically dishonest" is ambiguous), high scope risk (ML requires a full pipeline), and high volatility risk (legal and policy requirements are actively changing) (C)

    * High scope risk (building an ML model spans many subsystems) but low volatility risk (academic integrity standards remain stable and well-documented once formally adopted) 

### 2

A TA says: *"The system should be fair."* Following the participatory approach to requirements, what is the developer's best next step?

    * Document "fairness" as a non-functional requirement and assign it to quality assurance for validation
    * Treat "fair" as synonymous with "consistent" and add a requirement for statistical grade normalization
    * Present three existing fairness implementations from comparable systems and ask the TA to choose one
    * Ask the TA what "fair" means to them and explore specific scenarios where fairness was a problem (C)

### 3

A university registrar and an accessibility specialist are not interviewed during requirements gathering for a new student information system. What is the primary risk of omitting these stakeholders?

    * At or close to the time of deployment, the university registrar may be unable to create courses with legitimate constraints for students, the accessibility specialist may flag that grade entry system is unusable without a mouse (C)

    * The developers will miss critical domain expertise and will need to revisit and redesign core parts of the data model once those stakeholders raise concerns later

    * The system may have poor performance because, for example, the accessibility specialist may flag very slow screen readouts of several pages

    * The system may fail compliance audits because both of them are regulatory bodies that require documented sign-off before the system can be deployed

## Dependency Injection

### 1

Amit has the following: a `MyList` interface that represents a list, a `MyListImpl` class that implements `MyList`. He now makes a `MyStack` interface that represents a stack. He wishes to reuse his list interface and class and decides to favor composition over inheritance. He writes the following code:

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

Select all the advantages of this design (Each correct answer will get you points, each wrong answer will cause a deduction):

    * This design controls which methods are exposed as `public` for `MyStackImpl`: none of the `MyListImpl` methods are exposed by default (C)
    * This design avoid the flaky inheritance problem of overriding a public method that changes the behavior of another public method that was not overridden (C)
    * This class can be effectively tested to ensure that it is using the list correctly
    * This design has fewer lines of code than if inheritance was used


### 2

Amit has the following: a `MyList` interface that represents a list, a `MyListImpl` class that implements `MyList`. He now makes a `MyStack` interface that represents a stack. He wishes to reuse his list interface and class and decides to favor composition over inheritance. He writes the following code:

```java

class MyStackImpl<T> implements MyStack<T> {
    private MyList<T> list;

    public MyStackImpl(MyList<T> l) {
        list = l;
    }

    public void push(T object) {
        list.add(object);
    }
    ...
}

```

Select all the advantages of this design (Each correct answer will get you points, each wrong answer will cause a deduction):

    * This design controls which methods are exposed as `public` for `MyStackImpl`: none of the `MyListImpl` methods are exposed by default (C)
    * This design avoid the flaky inheritance problem of overriding a public method that changes the behavior of another public method that was not overridden (C)
    * This class can be effectively tested to ensure that it is using the list correctly (C)
    * This design has fewer lines of code than if inheritance was used

### 3

What is the primary disadvantage of the Service Locator pattern compared to constructor injection?

    * The Service Locator pattern requires significantly more boilerplate lines of code written at each call site
    * The Service Locator pattern is only available in frameworks and cannot be used in plain Java classes
    * Dependencies are buried in the method body rather than declared in the constructor, hiding them from callers (C)
    * The Service Locator allocates a brand-new registry instance on every lookup invocation, causing excessive memory use

## Architecture in general

#### 1
Which of the following best distinguishes an **architectural** decision from a **design** decision?

    * Architectural decisions are made by senior engineers; design decisions are delegated to the junior developer implementing the feature
    * Architectural decisions affect multiple teams across the organization; design decisions affect only the developer implementing that feature
    * Architectural decisions are expensive to reverse and constrain many later choices; design decisions can be reworked in a single coding session (C)
    * Architectural decisions specify individual method signatures; design decisions determine the overall deployment infrastructure and environment

## Hexagonal Architecture

#### 1

In the hexagonal architecture, ports are interfaces that exist on the boundary of the *domain* and "everything else". A *driving* port is an interface that is implemented by the domain objects but used by external components. Which of the following is/are an implementation of a driving port (select all that apply)?

    * Service implementation (C)
    * Controller in an MVC application
    * API used by clients to access/utilize core functionality (C)
    * Databases that provide data for domain objects

#### 2

In the hexagonal architecture, ports are interfaces that exist on the boundary of the *domain* and "everything else". A *driven* port is an interface that is implemented externally but used by domain objects. Select all examples from below that are an implementation of a driven port. (Each correct answer will get you points, each wrong answer will cause a deduction)

    * Service implementation
    * An object that provides lookup functionality needed by some business logic by using an AI agent (C)
    * API used by clients to access/utilize core functionality
    * Data access object that reads from a database (C)
