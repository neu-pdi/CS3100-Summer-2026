# Quiz 1

**Time Limit:** 60 minutes
**Format:** Multiple Choice (21 questions)

---

## Instructions

- Write your name on EVERY page of this exam.
- Select the best answer for each question on this page.
- All other exam pages will be discarded. All answers MUST be recorded on this page.
- All questions are worth equal points.
- You may not use notes, books, cheat sheet or electronic devices during the actual exam.

---

## Questions

### Question 1
In a codebase, the interface `Duration` represents a duration in time. It is implemented by the `HMSDuration` class that represent a duration in hours, minutes and seconds. In his code that extensively uses time durations, Alex uses `Duration` as the type of any fields, arguments and local variables, even though there is only one implementation of it. Is this a good choice?

- a) No, because using `HMSDuration` would make the code more easily understandable.
- b) Yes, because a fellow developer will find it easier to read the shorter interface than the longer implementation
- c) No, because if Alex used `HMSDuration` the code would work more efficiently because dispatching method calls need not be delegate till the program is run
- d) Yes, because this allows Alex to use other implementations in future without much change in his code

---

### Question 2
Consider these two ways to check a type and call a method:

```java
// Version A
if (device instanceof DimmableLight) {
    DimmableLight dimmable = (DimmableLight) device;
    dimmable.setBrightness(50);
}

// Version B
if (device instanceof DimmableLight dimmable) {
    dimmable.setBrightness(50);
}
```

Select the option that is most accurate:

- a) Version A is preferred because explicit casts are clearer
- b) Version B is not valid Java syntax
- c) Version B is preferred because it combines the type check and cast, eliminating redundancy
- d) Both versions will cause a `ClassCastException` if `device` is not a `DimmableLight`

---

### Question 3
What is the output of the following code?

```java
int primitive = 42;
Integer boxed = primitive;
System.out.println(boxed.equals(42));
```

- a) `false`
- b) Compilation error — cannot assign `int` to `Integer`
- c) `NullPointerException`
- d) `true`

---

### Question 4
When a method receives an argument that violates its preconditions (e.g., a negative value when positive is required), which exception is most appropriate?

- a) `Exception`
- b) `IllegalArgumentException`
- c) `NullPointerException`
- d) `IOException`

---

### Question 5
A specification for sort(List<Integer> items) in an interface states: "Iterates through the list using bubble sort, swapping adjacent elements until no swaps remain." What is the main problem with this specification?

- a) It is too short.
- b) It needs to be more general.
- c) It needs to be more restrictive.
- d) It does not mention the return type (which is void).

---

### Question 6
Consider this code:

```java
public class Notifier {
    public void notifyUser(User u) {
        /* sends one notification */
    }
    public void notifyGroup(List<User> users) {
        for (User u : users) {
            notifyUser(u);
        }
    }
}

public class CountingNotifier extends Notifier {
    private int sent = 0;

    @Override
    public void notifyUser(User u) {
        sent++;
        super.notifyUser(u);
    }

    @Override
    public void notifyGroup(List<User> users) {
        sent += users.size();
        super.notifyGroup(users);
    }
}
```

Suppose you create a new object: `Notifier notifier = new CountingNotifier(); `. If you call `notifier.notifyGroup(threeUsers)` where `threeUsers` is a list of 3 users, what will `sent` be?

- a) 3
- b) Impossible to say without more details
- c) 0
- d) 6

---

### Question 7

What happens when you run this code?

```java
Set<String> students = new HashSet<String>();
roster.add("Alice");
roster.add("Alicia"); 
roster.add("alice");
roster.add("");
System.out.println(roster.size());
```

- a) Prints `4`
- b) Prints `3`
- c) Prints `2`
- d) An exception is thrown

---

### Question 8
Consider this class hierarchy:

```
Object
  +toString() : String

«abstract»
Quantity
  +toString() : String

FractionalQuantity (extends Quantity)

DecimalQuantity (extends FractionalQuantity)
  +toString() : String
```

In the above design, the existence of a method signature in a class means that class provides a body for that method.

Which `toString()` method is called below?

```java
Quantity q = new FractionalQuantity(1, 1, 2, Unit.CUP);
System.out.println(q.toString());
```


- a) `Object.toString()` (the default)
- b) `DecimalQuantity.toString()`
- c) Compilation error because `Quantity` is abstract
- d) `Quantity.toString()`

---

### Question 9
In the `IoTDevice` class hierarchy, the interface `IoTDevice` was implemented by an abstract class `BaseIoTDevice`, which in turn was extended by `Light`, `DimmableLight`, `Fan` and `Thermostat` concrete classes. What changes in code would be required if we wish to make `DimmableLight` a subclass of `Light` instead, but not change the public methods it offers in any way? Select the most accurate option.

- a) We would need to start `DimmableLight` with `public class DimmableLight extends Light, BaseIoTDevice`, but nothing else would change
- b) We would need to change every class that uses `DimmableLight`
- c) We would need to start `DimmableLight` with `public class DimmableLight extends Light`, but nothing else would change
- d) We would need to start `DimmableLight` with `public class DimmableLight extends Light implements IoTDevice`, but nothing else would change

---

### Question 10
Consider the following hierarchy:

```java
interface IoTDevice {...}
class Light implements IoTDevice{...}
class Fan implements IoTDevice{...}
class Thermostat implements IoTDevice{...}
class DimmableLight extends Light {...}
```

A smart home contains many smart devices, possibly many in a single room. We need to store all the smart device objects such that they can be searched efficiently by room (a room is identified by a unique string such as "bedroom 1", "living room" etc.). The location of a device is stored in a field inside the `BaseIoTDevice` (i.e. each device knows its location).

Which data structure would be most appropriate to represent this?

- a) `Map<String,IoTDevice>`
- b) `List<IoTDevice>`
- c) `Set<IoTDevice>`
- d) `Map<String,List<IoTDevice>>`

---

### Question 11
Compare these two designs for processing submissions in different languages:

```java
// Design A
class SubmissionService {
    void process(Submission s, String language) {
        if (language.equals("Java")) { /* Java build/test */ }
        else if (language.equals("Python")) { /* Python build/test */ }
    }
}

// Design B
interface Builder { void build(Submission s); void test(Submission s); }
class JavaBuilder implements Builder { /* ... */ }
class PythonBuilder implements Builder { /* ... */ }
class SubmissionService {
    private Builder builder;
    SubmissionService(Builder b) { this.builder = b; }
    void process(Submission s) { strategy.build(s); strategy.test(s); }
}
```

What is the main advantage of Design B over Design A?

- a) Design A cannot compile because `String` parameters are not allowed
- b) For supporting additional languages, Design B requires only adding a new class each; Design A requires modifying `SubmissionService`
- c) Design B is faster because interfaces are optimized by the JVM
- d) Design B uses less memory than Design A

---

### Question 12
What is the primary difference between a `List` and a `Set` in the Java Collections Framework?

- a) `Set` maintains insertion order while `List` does not
- b) `Set` can only contain primitive types
- c) `List` is always faster than `Set`
- d) `List` allows duplicate elements and maintains order; `Set` does not allow duplicates

---

### Question 13
When is a named method preferable to a lambda expression?

- a) When the functional interface has multiple abstract methods
- b) When using method references is not possible
- c) When the logic is complex (multiple lines) or needs documentation
- d) When the lambda body is a single expression

---

### Question 14
What does implementing the `Comparable` interface enable?

- a) Natural ordering of objects, enabling use with sorting algorithms and sorted collections like `TreeSet`
- b) Comparing objects for equality
- c) Both a and b
- d) Neither a nor b

---

### Question 15
Which feature specifically enables Java code to be written once, but run on any Java-supported platform?

- a) Platform-independent bytecode (.class files) generated once can be run using the `java` command on any platform
- b) Java is controlled by one entity (previously Sun Microsystems, now Oracle), so platform support is easier to maintain
- c) Java is interpreted from source code directly to machine code, so such an interpreter can be written for any platform
- d) Internally Java is converted into C, a much older language that enjoys native support on all platforms

---

### Question 16
In a project using NullAway, a method parameter is annotated `@Nullable String name`. What does this indicate?

- a) The annotation has no effect; it's just documentation
- b) The parameter may be null, and the method must handle that case
- c) The parameter must never be null
- d) The string will be automatically converted to empty string if null

---

### Question 17
Consider this code:

```java
public class QuantityDemo {
    static void modifyQuantity(Quantity q) {
        q = new ExactQuantity(999, Unit.GRAM);
    }

    public static void main(String[] args) {
        Quantity original = new ExactQuantity(2.5, Unit.CUP);
        modifyQuantity(original);
        System.out.println(original.toDecimal());
    }
}
```

What is printed?

- a) `999.0`
- b) Compilation error
- c) `NullPointerException`
- d) `2.5`

### Question 18
When pushing commits from their local Git repo to a remote repo on Github, Alex encounters a message from Github that the push has not succeeded and asks Alex to pull first. What does this mean?

- a) The local repo is corrupted, and the remote repo no longer accepts pushes from it
- b) The remote repo contains code that is not present in the local repo, so pushing would overwrite it
- c) This is a friendly reminder to periodically pull from the remote repo: attempting to push again should succeed
- d) Github mandates that a push can only immediately follow a pull

### Question 19
Which of the following is a valid reason to intentionally leave behavior unspecified in a public method's specification?

- a) To confuse the reader.
- b) To allow multiple valid implementations without over-constraining the implementor.
- c) To allow the implementor to choose the externally visible behavior that best suits their use case.
- d) To make the specification shorter.

### Question 20

Consider this class written by Polly:

```java
class Message {
    private long id;
    private String content;
    ...

    @Override
    public boolean equals(Object o) {
        if (this==o) {
            return true;
        }
        if (o instanceof Message other) {
            return this.hashCode() == other.hashCode();
        }
        return false;
    }

    @Override
    public int hashCode() {
        return Long.hashCode(id);
    }
}

```

Two messages should be equal if and only if they have the same ID. 

Which statement below accurately captures the nature of this implementation?

- a) The implementation of `equals` is inconsistent with the definition above and may not always work correctly
- b) The implementation of `equals` is consistent with the definition above and will always work correctly
- c) `equals` and `hashCode` are not consistent: `a.equals(b)` returning `true` may not necessarily imply `a.hashCode()==b.hashCode()`
- d) both a and c.

### Question 21

Amit writes a `Customer` class that represents a single customer. This class stores the first name, last name, unique integer id, zip code and a list of all previous orders. The overall application needs to print a list of customers in the order of their last names, zip code or the number of previous orders depending on the context (what operation was executed). What is the best way to support this?

- a) Make `Customer` implement `Comparable<Customer>`
- b) Make `Customer` implement `Comparator<Customer>`
- c) Make several `Comparator<Customer>` implementations for each of the above criteria.
- d) Make several `Comparable<Customer>` implementations for each of the above criteria.


---

## Answer Key

| Q | Answer | Topic |
|---|--------|-------|
| 1 | D | - |
| 2 | C | - |
| 3 | D | - |
| 4 | B | - |
| 5 | B | - |
| 6 | D | - |
| 7 | A | - |
| 8 | D | - |
| 9 | C | - |
| 10 | D | - |
| 11 | B | - |
| 12 | D | - |
| 13 | C | - |
| 14 | C | - |
| 15 | A | - |
| 16 | B | - |
| 17 | D | - |
| 18 | B | - |
| 19 | B | - |
| 20 | A | - |
| 21 | C | - |
