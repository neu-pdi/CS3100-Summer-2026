# Quiz 1 Practice Exam

**Topics Covered:** Lectures 1-8
**Time Limit:** 65 minutes
**Format:** Multiple Choice (18 questions)
**Version:** Practice

---

## Instructions

- Select the best answer for each question.
- All questions are worth equal points.
- You may not use notes, books, or any electronic devices during the actual exam.

---

## Questions

### Question 1
Which statement best describes how Java achieves "write once, run anywhere"?

- a) Java source code is directly interpreted by the operating system
- b) Java source code is compiled to bytecode, which runs on the JVM available for each platform
- c) Java programs must be recompiled for each target operating system
- d) Java uses only ahead-of-time compilation to native machine code

---

### Question 2
Consider this code: `Quantity q = new ExactQuantity(2.5, Unit.CUP);`. The compiler verifies that `ExactQuantity` is assignable to `Quantity`. This is an example of:

- a) Dynamic typing - the type is checked when the program runs
- b) Static typing - the type is checked at compile time before the program runs
- c) Duck typing - any object with similar methods would work
- d) No type checking occurs

---

### Question 3
In CookYourBooks, `ExactQuantity`, `FractionalQuantity`, and `RangeQuantity` all extend `Quantity`. According to the Liskov Substitution Principle:

- a) Each subclass can implement `toDecimal()` to return any value it wants
- b) Each subclass must be usable anywhere a `Quantity` is expected without breaking the program
- c) Subclasses must have identical implementations of all methods
- d) Only `ExactQuantity` can be used where `Quantity` is expected

---

### Question 4
Why is `Quantity` declared as an abstract class rather than a regular class?

- a) Abstract classes use less memory
- b) It has abstract methods like `toDecimal()` that subclasses must implement, and it should not be instantiated directly
- c) Java requires all parent classes to be abstract
- d) It makes the class immutable

---

### Question 5
What distinguishes checked exceptions (e.g., `IOException`) from unchecked exceptions (e.g., `IllegalArgumentException`)?

- a) Checked exceptions are faster to throw
- b) Checked exceptions must be declared in the method signature or caught; unchecked exceptions do not
- c) Unchecked exceptions cannot be caught
- d) Checked exceptions extend `RuntimeException`

---

### Question 6
If CookYourBooks stored ingredients in a `List` without generics, what problem (if any) would occur in compiling or running the following code?

```java
List ingredients = new ArrayList();
ingredients.add(new MeasuredIngredient("flour", ...));
ingredients.add("A pinch of salt");
```

- a) Nothing; this is a fine practice
- b) Without generics, the compiler can't prevent adding wrong types, leading to potential `ClassCastException` at runtime
- c) The program runs slower
- d) `ArrayList` doesn't work without generics

---

### Question 7
In `MeasuredIngredient.hashCode()`, the name is converted to lowercase before hashing: `getName().toLowerCase()`. Why?

- a) Lowercase strings hash faster
- b) Since `equals()` compares names case-insensitively, `hashCode()` must also be case-insensitive so equal objects have equal hash codes
- c) Java requires lowercase in `hashCode()`
- d) It's just a style preference

---

### Question 8
Which of the following is NOT one of the three criteria for evaluating a good specification?

- a) Restrictiveness (rules out bad implementations)
- b) Generality (doesn't over-constrain the implementation)
- c) Efficiency (specifies performance requirements)
- d) Clarity (easy to understand)

---

### Question 9
Which specification for a `reverse(String s)` method is more general?

**Spec A:**
```
/**
 * Creates a char[] from the string `s`, iterates from the last character to the first,
 * copying each to the array, then returns a new string from the array.
 * @param s a non-null string
 */
```

**Spec B:**
```
/**
 * Returns a new string with the characters of s in reverse order.
 * @param s a non-null string
 */
```

- a) Spec A, because it's more detailed
- b) Spec B, because it defines the result without mandating a specific algorithm
- c) They are equally general
- d) Spec B, because it handles edge cases that Spec A doesn't

---

### Question 10
`MeasuredIngredient` overrides both `equals()` and `hashCode()`. Why is it important to override both together?

- a) The compiler enforces that both must be overridden together
- b) Equal objects must have equal hash codes for hash-based collections to work correctly
- c) `hashCode()` must call `equals()` internally to compute its value
- d) Overriding only `equals()` causes a compilation error in classes that use generics

---

### Question 11
What should `x.compareTo(y)` return if `x` is less than `y`?

- a) `true`
- b) `false`
- c) A negative integer
- d) Zero

---

### Question 12
What is the primary advantage of using a lambda expression instead of an anonymous class for a functional interface?

- a) Lambdas are faster at runtime
- b) Lambdas are more concise and reduce boilerplate code
- c) Lambdas can implement multiple methods
- d) Lambdas can access private fields that anonymous classes cannot

---

### Question 13
What does the following method reference represent?

```java
lights.sort(Comparator.comparingInt(DimmableLight::getBrightness));
```

- a) A call to `getBrightness()` on the `DimmableLight` class itself
- b) A reference to the `getBrightness` method that will be called on each `DimmableLight` instance
- c) A static method that returns brightness values
- d) A constructor reference for creating `DimmableLight` objects

---

### Question 14
Which of the following is NOT automatically provided by a Java record?

- a) A constructor that initializes all fields
- b) `equals()`, `hashCode()`, and `toString()` implementations
- c) Mutable setter methods for each field
- d) Accessor methods for each field

---

### Question 15
Consider this method signature for code that compiles and runs correctly:

```java
void notifyStudent(Submission submission) {
    sendEmail(submission.student.email, "Your submission was received");
}
```

The method only uses `submission.student.email`. What is the main problem with this design?

- a) The method cannot be tested without constructing a full `Submission` object with a `Student`
- b) The method is slower than passing a `String` directly
- c) The method violates the Liskov Substitution Principle
- d) The method cannot handle multiple submissions

---

### Question 16
A `Utility` class contains unrelated methods like `formatDate()`, `calculateTax()`, and `validateEmail()`. What is the main problem with this design?

- a) The class will run out of memory
- b) The class becomes a dumping ground that's hard to navigate, and changes to one method risk affecting unrelated functionality
- c) Java does not allow static utility methods
- d) The methods cannot be tested individually

---

### Question 17
Which SOLID principle states that "a class should have only one reason to change"?

- a) Open/Closed Principle
- b) Single Responsibility Principle
- c) Interface Segregation Principle
- d) Dependency Inversion Principle

---

### Question 18
Consider Java's I/O stream design:

```java
InputStream in = new BufferedInputStream(new FileInputStream("data.txt"));
```

`BufferedInputStream` wraps `FileInputStream`, adding buffering without modifying `FileInputStream`. What is the main advantage of this design over using inheritance (e.g., `class BufferedFileInputStream extends FileInputStream`)?

- a) The wrapper approach is faster at runtime
- b) Behaviors can be combined flexibly at runtime without creating a subclass for every combination
- c) The wrapper approach uses less memory
- d) Inheritance is not allowed for stream classes in Java

---

## Answer Key

| Q | Answer | Topic |
|---|--------|-------|
| 1 | B | L1: JVM/Bytecode |
| 2 | B | L1: Static typing |
| 3 | B | L2: Liskov Substitution Principle |
| 4 | B | L2: Purpose of abstract classes |
| 5 | B | L2: Checked vs unchecked exceptions |
| 6 | B | L3: Generics type safety |
| 7 | B | L4: hashCode consistency |
| 8 | C | L4: Specification criteria |
| 9 | B | L4: Definitional vs operational specs |
| 10 | B | L4: equals/hashCode contract |
| 11 | C | L4: Comparable contract |
| 12 | B | L5: Lambdas vs anonymous classes |
| 13 | B | L5: Method references |
| 14 | C | L5: Records |
| 15 | A | L7: Stamp coupling (problem) |
| 16 | B | L7: Coincidental cohesion (problem) |
| 17 | B | L8: Single Responsibility Principle |
| 18 | B | L8: Composition over inheritance |