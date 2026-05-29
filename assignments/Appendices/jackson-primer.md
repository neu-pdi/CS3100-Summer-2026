---
title: 'Jackson and JSON Primer'
sidebar_position: 6
---


# 1 JSON and Jackson Primer

This page provides background on JSON and the Jackson library for students who haven't worked with JSON serialization before.

## 1.1 What is JSON?

**JSON (JavaScript Object Notation)** is a lightweight text format for storing and exchanging data.
Despite "JavaScript" in the name, JSON is language-independent and has become the de facto standard for data interchange on the web and in modern applications.

A JSON document is plain text that humans can read and machines can parse reasonably efficiently. It is so pervasive, that even if you haven't worked with it before, you have probably seen it before.
Here's an example:

```json
{
  "title": "Chocolate Chip Cookies",
  "servings": 24,
  "author": "Grandma",
  "tags": ["dessert", "baking", "cookies"],
  "published": true,
  "rating": null
}
```

**JSON supports six data types:**

| Type    | Example                   | Java Equivalent                |
| ------- | ------------------------- | ------------------------------ |
| String  | `"hello"`                 | `String`                       |
| Number  | `42`, `3.14`, `-7`        | `int`, `double`, `BigDecimal`  |
| Boolean | `true`, `false`           | `boolean`                      |
| Null    | `null`                    | `null`                         |
| Array   | `[1, 2, 3]`, `["a", "b"]` | `List<T>`, arrays              |
| Object  | `{"key": "value"}`        | Java objects, `Map<String, T>` |

**Key syntax rules:**

- Strings must use double quotes (`"hello"`, not `'hello'`)
- Object keys must be strings (`{"name": "value"}`, not `{name: "value"}`)
- No trailing commas (`[1, 2, 3]`, not `[1, 2, 3,]`)
- No comments (unlike Java, JSON has no comment syntax)

## 1.2 Why JSON Became Popular

JSON emerged in the early 2000s as a simpler alternative to XML (another popular data format at the
time). Its rise to dominance came from several factors:

1. **Human-readable:** Unlike binary formats, we can open a JSON file in any text editor and understand its structure immediately.

2. **Lightweight:** JSON has minimal syntax overhead compared to XML. Compare:

   ```xml
   <recipe><title>Cookies</title><servings>24</servings></recipe>
   ```

   ```json
   { "title": "Cookies", "servings": 24 }
   ```

3. **Native to JavaScript:** Web browsers can parse JSON directly with `JSON.parse()`, making it
   ideal for web APIs.

4. **Schema flexibility:** JSON doesn't require a predefined schema, making it easy to evolve data
   formats over time. This is a stark contrast to XML, which requires a predefined schema.

Today, JSON is used for:

- Data exchange between services (e.g. APIs)
- Configuration files (e.g. VS Code settings)
- Document databases (e.g. MongoDB stores JSON-like documents)

## 1.3 Jackson: Java's JSON Library

**Jackson** is the most widely-used JSON library for Java. It handles serialization (Java objects → JSON) and deserialization (JSON → Java objects).

:::note Simpler Examples Online

If you search for Jackson tutorials, you will find simpler-looking examples using mutable classes with no-arg constructors and setters. These approaches won't work for this assignment because your domain
classes must be immutable (final fields, no setters). The patterns below are what you need.

:::

:::note Working with Jackson in Gradle

To work with Jackson in a Gradle project, add the following to build.gradle:

```json 

dependencies {
    ...

    // Jackson for JSON serialization
    implementation libs.jackson.databind
    implementation libs.jackson.core
    implementation libs.jackson.annotations
    implementation libs.jackson.jdk8      // For Optional support
    implementation libs.jackson.jsr310    // For Java 8 date/time support

}
```

:::

## 1.4 Jackson with Immutable Classes

Domain classes are often immutable—they have `final` fields and no setters. The default approach used by Jackson to create new objects from JSON is to use a no-arg constructor, and then to set each field one-by-one. However, this is not possible when your classes are immutable - the fields must be set in the constructor. Hence, we need to use the `@JsonCreator` annotation to tell Jackson how to
construct instances:

```java
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public final class Person {
    private final String name;
    private final int age;

    @JsonCreator // This tells Jackson to use this constructor to create new instances from JSON
    public Person(
            @JsonProperty("name") String name, // This tells Jackson to map the JSON field "name" to the parameter name
            @JsonProperty("age") int age) { // This tells Jackson to map the JSON field "age" to the parameter age
        if (name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank");
        }
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public int getAge() { return age; }
}
```

**How it works:**

- `@JsonCreator` tells Jackson to use this constructor for deserialization
- `@JsonProperty("name")` maps the JSON field `"name"` to this constructor parameter
- Jackson uses getters (`getName()`) to determine what fields to serialize
- Any validation logic in the constructor runs during deserialization

**Serializing and deserializing:**

The `ObjectMapper` class is used to serialize and deserialize Java objects to and from JSON.

When deserializing, we must specify the class of the object to deserialize to so that the return object is of the correct type. This type is **not** used to instantiate the object - that is done by
the `@JsonCreator` annotation, so the code below will work even if the `json` string is a subclass of `Person`.

```java
import com.fasterxml.jackson.databind.ObjectMapper;

ObjectMapper mapper = new ObjectMapper();

// Serialize: Java object → JSON string
Person person = new Person("Alice", 30);
String json = mapper.writeValueAsString(person);
// Result: {"name":"Alice","age":30}

// Deserialize: JSON string → Java object
Person restored = mapper.readValue(json, Person.class);
```

**Working with collections:**

```java
// Serializing a list works directly
List<Person> people = List.of(new Person("Alice", 30), new Person("Bob", 25));
String json = mapper.writeValueAsString(people);
// Result: [{"name":"Alice","age":30},{"name":"Bob","age":25}]

// Deserializing a list requires TypeReference (due to Java type erasure)
List<Person> restored = mapper.readValue(json, new TypeReference<List<Person>>() {});
```

## 1.5 Handling Optional Fields

For backwards compatibility reasons, Java's `Optional<T>` needs special handling. Register the `Jdk8Module` with the `ObjectMapper`:

```java
ObjectMapper mapper = new ObjectMapper();
mapper.registerModule(new Jdk8Module());
```

The starter code provides stub files for `JsonRecipeRepository` and `JsonRecipeCollectionRepository` with the `ObjectMapper` configuration already set up.

Now `Optional` fields work correctly:

```java
public class Recipe {
    private final String title;
    private final Optional<String> author;

    @JsonCreator
    public Recipe(
            @JsonProperty("title") String title,
            @JsonProperty("author") Optional<String> author) {
        this.title = title;
        this.author = author != null ? author : Optional.empty();
    }

    // getters...
}

// Serialization
Recipe r1 = new Recipe("Cookies", Optional.of("Grandma"));
// {"title":"Cookies","author":"Grandma"}

Recipe r2 = new Recipe("Cookies", Optional.empty());
// {"title":"Cookies","author":null}  or  {"title":"Cookies"} depending on config
```

## 1.6 Handling Polymorphism (Inheritance)

When we have a class hierarchy like `Quantity` with subclasses
`ExactQuantity`, `FractionalQuantity`, and `RangeQuantity`, Jackson needs to know which subclass to instantiate during deserialization.

**The problem:**

```java
// How to know which concrete Quantity subclass to instantiate?
{"amount": 2.5, "unit": "CUP"}
```

**The solution:** Add type annotations to the base class and use `@JsonCreator` on subclasses.

```java
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.annotation.JsonSubTypes;

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type") // This tells Jackson to add a "type" field to the JSON
@JsonSubTypes({
    @JsonSubTypes.Type(value = ExactQuantity.class, name = "exact"), // This tells Jackson to map JSON objects with a "type" field of "exact" to the ExactQuantity class
    @JsonSubTypes.Type(value = FractionalQuantity.class, name = "fractional"), // This tells Jackson to map JSON objects with a "type" field of "fractional" to the FractionalQuantity class
    @JsonSubTypes.Type(value = RangeQuantity.class, name = "range") // This tells Jackson to map JSON objects with a "type" field of "range" to the RangeQuantity class
})
public abstract class Quantity {
    // ...
}
```

**How it works:**

- `@JsonTypeInfo(property = "type")` tells Jackson to add a `"type"` field to the JSON
- `@JsonSubTypes` maps each type name to its corresponding Java class
- When deserializing, Jackson reads the `"type"` field first to determine which class to instantiate

This produces JSON like:

```json
{"type": "exact", "amount": 2.5, "unit": "CUP"}
{"type": "fractional", "numerator": 1, "denominator": 2, "unit": "CUP"}
{"type": "range", "min": 2, "max": 3, "unit": "CUP"}
```

## 1.7 Common Errors and Solutions

| Error                                                     | Cause                               | Solution                                             |
| --------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------- |
| `InvalidDefinitionException: Cannot construct instance`   | No suitable constructor             | Add `@JsonCreator` to constructor                    |
| `UnrecognizedPropertyException: Unrecognized field "xyz"` | JSON has field our class does not   | Add the field, or configure mapper to ignore unknown |
| `InvalidTypeIdException: Missing type id`                 | Polymorphic type without type field | Ensure `@JsonTypeInfo` is configured                 |
| `JsonMappingException: No serializer found`               | Private fields without getters      | Add getters, or configure field visibility           |

**Ignoring unknown properties** (useful during development):

```java
mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
```

## 1.8 Testing JSON Round-Trips

A round-trip test verifies that serialization and deserialization preserve all data:

```java
@Test
void recipeRoundTrip() throws Exception {
    ObjectMapper mapper = createObjectMapper();

    Recipe original = new Recipe(
        "test-id",
        "Chocolate Cake",
        new ExactQuantity(8, Unit.SERVING),
        List.of(new MeasuredIngredient("flour", new ExactQuantity(2, Unit.CUP), null, null)),
        List.of(new Instruction(1, "Mix ingredients", List.of())),
        List.of()
    );

    // Serialize to JSON
    String json = mapper.writeValueAsString(original);

    // Deserialize back
    Recipe restored = mapper.readValue(json, Recipe.class);

    // Verify equality
    assertEquals(original, restored);
}
```

## 1.9 Further Reading

- [Jackson Project Home](https://github.com/FasterXML/jackson) — Official documentation
- [Baeldung Jackson Tutorial](https://www.baeldung.com/jackson) — Comprehensive tutorial series
- [JSON Specification](https://www.json.org/) — The official JSON format specification

:::tip Ask AI Assistant

Jackson configuration can be tricky. This is a great place to use an AI assistant:

- "How do I configure Jackson to serialize LocalDate as a string?"
- "My deserialization is failing with [error]. What's wrong?"
- "How do I handle a field that might be missing in the JSON?"

Just remember to understand what the generated code does before using it.

:::
