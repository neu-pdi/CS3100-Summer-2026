# Learning Objectives

By the end of this lab, you will be able to:

- Identify what belongs in the **domain** versus **infrastructure** within a feature area, and explain *why* mixing them hurts testability
- Design **port interfaces** that use only domain types and can be trivially stubbed for tests
- Critically evaluate code (whether AI-generated or manually written)
- Explain how **dependency injection** eliminates the `DatabaseConnection` singleton and what the resulting composition root looks like
- Communicate design decisions using a structured narrative: *"I chose X because Y. I considered Z, but X is better for this situation because..."*

## Before You Begin

The repository includes:
- `src/` — starter Java files with the current tangled SceneItAll code
- `REFLECTION.md` — where all your written analysis goes
- `diagrams/` — folder for your port/adapter diagrams

:::tip GitHub Copilot

GitHub Copilot is used in Parts 2 and 3. You can use both **inline completions** (Tab to accept) and **Copilot Chat** (`Ctrl+I` / `Cmd+I` or the chat panel). [GitHub Copilot Chat](https://github.com/copilot) is also available in a browser.

- **Part 2:** Design manually first, then use Copilot to verify your work
- **Part 3:** Use Copilot as your primary design tool

:::

---

## Prompting Copilot for Design Tasks (Reference for Parts 2-3)

Here's the key difference between a weak prompt and a strong one for architectural work:

| Weak Prompt | Why It Fails | Stronger Prompt |
|-------------|-------------|-----------------|
| "Extract an interface from this class" | Copilot will mirror the class's current methods, including infrastructure-specific ones | "Extract an interface that represents what the *domain* needs from device state — use only domain types, not Zigbee SDK types" |
| "Refactor to use dependency injection" | Copilot may add DI but leave singletons or add a service locator | "Refactor to use constructor injection. Remove all calls to `getInstance()`. The class should not access any global state." |
| "Generate a repository interface" | May expose storage-specific implementation details in the interface | "Generate a repository interface using only domain types. The interface should have no knowledge of how data is stored." |

**The pattern:** Specify the *design goal* (what principle you're following), the *constraints* (what should be absent from the output), and the *vocabulary* (domain types, not infrastructure types).

---

# 2 The Scenario: SceneItAll's Growing Monolith

SceneItAll has been a single Java application — one `build.gradle`, one `src/` tree, one deployment. It started small, but now it has multiple feature areas that are starting to tangle. For this lab, we'll focus on **two** of them:

1. **Device Management** — Adding, removing, and configuring IoT devices (cameras, thermostats, lights, sensors). Checking device health. Processing firmware update requests.
2. **Automation Rules** — Users create rules like "if motion detected after 10pm, turn on porch light and send alert." Rules reference devices, user preferences, and time.

*(The full system also has Notification, Analytics, and User Management features, but we'll keep our scope narrow today.)*

Right now, these features are jumbled together — classes from different features import each other freely, there's a `DatabaseConnection` singleton that everything uses, and the `AutomationRuleEngine` reaches directly into a hardware SDK to check device states.

Here's an example of what a piece of the current code looks like (also in `src/AutomationRuleEngine.java` in your repo):

```java
public class AutomationRuleEngine {
    public void evaluate(String homeId) {
        List<AutomationRule> rules = DatabaseConnection.getInstance()
                .loadRules(homeId);

        ZigbeeGateway gateway = ZigbeeGateway.getGlobalInstance();

        for (AutomationRule rule : rules) {
            DeviceState state = gateway.readState(rule.getTriggerDeviceId());
            if (rule.conditionMet(state)) {
                List<User> users = DatabaseConnection.getInstance()
                        .loadUsersForHome(rule.getHomeId());
                for (User user : users) {
                    List<NotificationPreference> prefs = DatabaseConnection.getInstance()
                            .loadNotificationPreferences(user.getId());
                    for (NotificationPreference pref : prefs) {
                        if (pref.isEnabled()) {
                            // More code to send the alert
                        }
                    }
                    if (prefs.isEmpty()) {
                        notificationService.sendAlert(user.getId(), rule.getAlertMessage(), NotificationChannel.PUSH);
                    }
                }
            }
        }
    }
}
```

## 2.1 The Constraints

- This is a **single deployable application** — one JAR, one `main()`. We're not splitting into separate servers.
- The codebase must be **testable without real IoT hardware** — you need to be able to test business logic (e.g., "should this automation rule fire?") with test doubles, not a live Zigbee network.
- All dependencies between modules should flow through **interfaces**, not concrete classes or singletons.

---

# 3 Part 1: Understand the Architecture — Individual Work 

Before forming pairs, work through these exercises **on your own**. The goal is to develop your own analysis of the code — you'll bring these observations to your partner when you pair up.

## 3.1 Exercise: Dissect AutomationRuleEngine

Look at the `AutomationRuleEngine.evaluate()` code above. Annotate each block manually (no Copilot yet):

1. Which lines are **domain logic** — the actual business decision being made?
2. Which lines are **infrastructure** — database access, hardware calls, HTTP?
3. The `conditionMet(state)` method is on `AutomationRule`. Is that domain or infrastructure? Why?
4. What makes this code **hard to test**? Which parts hurt *controllability*? Which parts hurt *observability*?

Record your annotations in `REFLECTION.md` (Question 1). **Do this before pairing up** — having your own analysis first is how you'll know what's worth discussing with your partner.

## 3.2 Exercise: What Would You Need to Stub?

The goal of hexagonal architecture is to make each feature's core logic testable *in isolation* — without spinning up real hardware, real network services, or a real data store.

For each of our two focus areas (**Device Management** and **Automation Rules**), complete this sentence:

> **"To test [feature]'s core business logic in isolation, I would need to stub out _____ ."**

Use these observations in your answer to Question 1.


## 3.3 Pair Formation and Soft Skill Introduction

Find a partner you haven't worked with recently. Before starting Part 2, spend 2 minutes on this:

**Share your Part 1 observation** using this sentence frame:
> *"In AutomationRuleEngine, I noticed [X], which means [consequence for testability]."*

**Soft skill for today: Communicating Technical Decisions**

Throughout Parts 2 and 3, whenever you make or defend a design choice, practice this format:
> *"I chose [design element] because [reason]. I considered [alternative], but [my choice] is better for this situation because [specific reason]."*

Your partner's job when listening: ask *"Why did you prioritize that?"* — not to challenge, but to draw out more of your reasoning.

Record your partner's name in `REFLECTION.md`.

---

# 4 Part 2: Fix the DatabaseConnection Singleton 

The `DatabaseConnection` singleton is SceneItAll's biggest design problem — and also the most concrete place to start learning hexagonal architecture. Every feature area reaches for it directly, which means nothing can be tested in isolation.

In this part, you'll **design the replacement manually first** (with your partner), then use **Copilot to verify and refine** your design.

## 4.1 The Problem: One Giant Singleton

```java
// Current code — in src/DatabaseConnection.java
public class DatabaseConnection {
    private static DatabaseConnection instance;

    public static DatabaseConnection getInstance() {
        if (instance == null) {
            instance = new DatabaseConnection(); // connects to production data store
        }
        return instance;
    }

    // Methods for every feature area — one giant object everyone shares:
    public List<AutomationRule> loadRules(String homeId) { /* ... */ }
    public void saveRule(AutomationRule rule) { /* ... */ }
    public List<IoTDevice> loadDevices(String homeId) { /* ... */ }
    public void saveDevice(IoTDevice device) { /* ... */ }
    public DeviceHealth checkDeviceHealth(String deviceId) { /* ... */ }
    // ... and many more
}
```

## 4.2 Exercise: Discover the Coupling

Before designing a fix, let's see how severe the problem is. The `DatabaseConnection` singleton is used throughout the codebase. Here are two examples:

**In `DeviceManager.java`:**
```java
public class DeviceManager {
    public void addDevice(String homeId, IoTDevice device) {
        // Singleton call — can't test without a real database!
        DatabaseConnection.getInstance().saveDevice(device);
        // ...
    }
}
```

**In `AutomationRuleEngine.java`:**
```java
public void evaluate(String homeId) {
    // Singleton call — can't test without a real database!
    List<AutomationRule> rules = DatabaseConnection.getInstance().loadRules(homeId);
    // ...
}
```

**Now use VS Code to find all references:**

1. Open `src/DatabaseConnection.java` in VS Code
2. Right-click on `getInstance` and select **"Find All References"** (or press `Shift+F12`)
3. Count how many files call this method

Take note of how many files reference this method — you'll use this observation in your discussion.

## 4.3 Exercise: Diagnose the Problem

With your partner discuss these three questions **before designing any replacement**:

1. From [L17](https://neu-pdi.github.io/CS3100-Spring-2026/lecture-notes/l17-creation-patterns): what are the **three problems** with singletons? Give a concrete example of each in the context of `DatabaseConnection`.
2. From [L16](https://neu-pdi.github.io/CS3100-Spring-2026/lecture-notes/l16-testing2): does this singleton hurt **observability**, **controllability**, or both? Explain specifically.
3. If two tests run concurrently and both call `DatabaseConnection.getInstance()`, what could go wrong?

## 4.4 Exercise: Design Repository Interfaces — Manual First

Now for the fix. You'll design new repository interfaces that will replace `DatabaseConnection` for our two focus areas: **Device Management** and **Automation Rules**. Then you'll refactor `DeviceManager` to actually use your interface — so you can see the difference between the singleton approach and dependency injection.

**Step 1: Manual Design (with your partner, no Copilot yet)**

For each of the two feature areas, design a repository interface. Ask yourselves:
- What operations does this feature area need from data storage?
- What domain types should the interface use? (Not infrastructure types!)
- How narrow can we make this interface while still being useful?
- How, if at all, should the domain types be adjusted?

Sketch your interfaces on paper or in a scratch file. For example, you might design:

```java
// For Device Management
public interface DeviceRepository {
    // What operations does DeviceManager actually need?
}

// For Automation Rules
public interface RuleRepository {
    // What operations does AutomationRuleEngine actually need?
}
```

**Step 2: Verify with Copilot**

Once you have a draft, use Copilot to check your design:
> *"I'm replacing this DatabaseConnection singleton with dependency injection. Here's my draft interface for [DeviceRepository/RuleRepository]. Does this interface correctly express what the domain needs for data access? Does it leak any storage-specific implementation details? Suggest improvements."*

Compare Copilot's feedback to your manual design. Did it catch anything you missed? Did it suggest anything that actually *violates* hexagonal principles (like adding infrastructure types)?

**Record in `REFLECTION.md` (Question 2):** Your final interface designs with reasoning.

## 4.5 Exercise: Create In-Memory Implementation

For your `DeviceRepository` interface, create an `InMemoryDeviceRepository` implementation that uses a `HashMap` for storage. This is what you'd use in tests instead of the real database.

You can use Copilot for this:
> *"Generate an `InMemoryDeviceRepository` class that implements `DeviceRepository` using a `HashMap`. It should have no dependencies on `DatabaseConnection` or any external systems."*

Evaluate the result:
- Does it implement your interface correctly?
- Does it have any calls to `DatabaseConnection`? (It shouldn't — that's the whole point!)
- Could you use this in a unit test that runs in milliseconds?

You'll use this implementation in the next exercise.

## 4.6 Exercise: Refactor DeviceManager to Use Your Interface

Now apply your design. Modify `DeviceManager` to use constructor injection instead of the singleton:

1. Add a constructor parameter for `DeviceRepository`
2. Store it as a private field
3. Replace all `DatabaseConnection.getInstance()` calls with your repository field
4. Remove the import for `DatabaseConnection`

You can use Copilot:
> *"Refactor this class to accept DeviceRepository via constructor injection. Replace all DatabaseConnection.getInstance() calls. The class should have no static dependencies."*

Evaluate the result:
- Does `DeviceManager` still have any `getInstance()` calls? (It shouldn't!)
- Could you now instantiate `DeviceManager` in a test with your `InMemoryDeviceRepository`?

**The key insight:** After this refactoring, you can test `DeviceManager` without any database — just pass in your in-memory implementation. That's the power of dependency injection.

Record your refactored `DeviceManager` in `REFLECTION.md` (Question 3).

# 5 Part 3: Design Ports for AutomationRuleEngine — Copilot Focus

Now that you've tackled the `DatabaseConnection` singleton (which affects data access across the system), let's apply hexagonal architecture to the `AutomationRuleEngine` itself. This class has **multiple infrastructure dependencies** beyond just the database — it also reaches directly into hardware SDKs and HTTP clients.

In this part, you'll use **Copilot as your primary design tool** and practice evaluating AI-generated output against hexagonal principles.

### What Makes a Good Port

```java
// Good port: uses domain types, defined by what the DOMAIN needs
public interface DeviceStatePort {
    DeviceState getCurrentState(String deviceId);
}

// Bad port: leaks infrastructure types into the interface
public interface ZigbeeInterface {
    ZigbeeFrame sendFrame(byte[] payload);  // What the heck is a "ZigbeeFrame"???? It must be infrastructure!
}
```

A good port: uses **domain types** not infrastructure types; is **narrow** (only what's needed); can be **trivially stubbed** for tests.

## 5.1 Exercise: Use Copilot to Design Ports

Look back at the `AutomationRuleEngine.evaluate()` code from Part 1. It has three infrastructure dependencies:

1. **Data access** (you already designed a repository interface for this in Part 2!)
2. **Device state reads** — the `ZigbeeGateway.getGlobalInstance()` call
3. **Notification sending** — the direct `HttpClient` call

Use Copilot to generate port interfaces for the device state and notification dependencies:

> *"I'm applying hexagonal architecture to this class. Identify the external dependencies and generate Java interface definitions for each one as ports. Each interface should use only domain types — no SDK types like ZigbeeFrame, no infrastructure types like HttpResponse."*

**Evaluate Copilot's output:**
- Does each interface use domain types or infrastructure types?
- Is it narrow enough to be stubbed with a lambda in a test?
- Did Copilot miss any dependencies?

If Copilot gets it wrong, write a follow-up prompt — for example:
> *"The `readState` method returns a `ZigbeeFrame`. That's an infrastructure type. Rewrite the interface so it returns `DeviceState` instead, where `DeviceState` is a domain object."*

Record your final port interfaces in `REFLECTION.md` (Question 4). Note any problems with Copilot's first attempt.

## 5.2 Exercise: Diagram Your Ports

Create a **Mermaid diagram** showing the hexagonal architecture for **Automation Rules** — the domain, port interfaces, at least one production adapter, and one test double.

Ask Copilot to generate a Mermaid diagram:
> *"Generate a Mermaid diagram showing the hexagonal architecture for AutomationRuleEngine with the port interfaces we designed. Show the domain in the center, ports as interfaces, production adapters on one side, and test doubles on the other."*

Save the result in `diagrams/automation-rules.md`. Check that your diagram correctly shows:
- Adapters depending on ports (arrows point inward)
- Test doubles implementing the same ports as production adapters
- The domain depending only on port interfaces, not on adapters

> 💡 **Mermaid hint** if Copilot needs guidance:
> ```mermaid
> graph LR
>     subgraph Domain["Automation Rules Domain"]
>         RE[AutomationRuleEngine]
>         RP[RuleRepositoryPort <<interface>>]
>         DS[DeviceStatePort <<interface>>]
>     end
>     ...
> ```

Save your diagram in `diagrams/automation-rules.md`.

## 5.3 Exercise: Design the Composition Root

If we inject all these dependencies, *someone* has to wire them up. In [L17](https://neu-pdi.github.io/CS3100-Spring-2026/lecture-notes/l17-creation-patterns) we called this the **composition root**.

Use Copilot:
> *"Show me what `SceneItAllApplication.main()` should look like after applying dependency injection throughout. It should create all the production adapter implementations for DeviceManager and AutomationRuleEngine, then wire them in via constructor injection. There should be no calls to any `getInstance()` methods anywhere."*

Evaluate the result:
- Does it still contain any `getInstance()` calls? (Flag them if so.)
- Is it clear that this is the **only** place in the codebase that knows about concrete implementations?


Verify the composition root has no `getInstance()` calls.

# 6 Part 4: Design Review and Reflection

## 6.1 Exercise: Explain a Decision to Another Pair

Find another pair and share screens or swap `REFLECTION.md` files. Each person explains **one key design decision** using the structured format:

> *"I chose [design element] because [reason]. I considered [alternative], but my choice is better for this situation because [specific reason connecting to testability or hexagonal architecture principles]."*

The listener's role: ask *"Why did you prioritize that quality attribute?"* and *"What would break if you'd gone with the alternative?"*

## 6.2 Exercise: Technical Review

With the other pair, review each other's port interfaces:

1. **Infrastructure leakage check:** Do any port interfaces mention infrastructure types (HTTP, Zigbee, AWS, SMTP, or storage-specific details)?
2. **Singleton check:** Does the composition root have any `getInstance()` calls remaining?
3. **Testability check:** For each port, ask: "Could this be stubbed with a lambda or a simple in-memory class?" If not, what makes it hard to stub?

Record one observation in `REFLECTION.md` (Question 5).

## 6.3 Exercise: Thinking About a New Feature Area

Throughout this lab, we focused on two feature areas: **Device Management** and **Automation Rules**. But SceneItAll also has other features we didn't touch: Notifications, Analytics, and User Management.

**Think about adding a new feature area** — for example, **Analytics & Reporting** (which queries historical device data, generates usage reports, and calculates trends).

In `REFLECTION.md` (Question 6), answer:

- What ports (interfaces) would the Analytics domain need?
- Would Analytics share any ports with Device Management or Automation Rules, or would it need entirely new ones?
- How would you add Analytics to the composition root you designed in Part 3?

**You don't need to write any code** — just think through how the hexagonal architecture pattern would extend to this new area.


# 7 Reflection

Complete these questions in `REFLECTION.md` as you work through the lab.

**Partner's Name:** _______________

1. **Domain vs Infrastructure:** In `AutomationRuleEngine.evaluate()`, which lines are domain logic and which are infrastructure? What specifically hurts testability (controllability or observability)?

2. **Repository Interface Design:** Your final `DeviceRepository` and `RuleRepository` interfaces, with reasoning: *"I defined [interface] as [description] because [reason]."*

3. **Refactored DeviceManager:** Your refactored class using constructor injection. Confirm: no `getInstance()` calls remain, and you can now instantiate it with `InMemoryDeviceRepository` for testing.

4. **Port Interfaces:** Your final port interfaces for device state and notification. Did Copilot's first attempt use infrastructure types? What did you fix?

5. **Peer Review Finding:** One thing you noticed reviewing another pair's work — an infrastructure leak, a clean port design, or a remaining singleton. What would you change or keep?

6. **Extending the Architecture:** What ports would Analytics & Reporting need? Would it share any with Device Management or Automation Rules?

7. **Meta (pick one):**
   - *Connections:* How does one of your design decisions connect to a concept from L7-L17?
   - *Communication:* Did explaining a decision out loud clarify your thinking?
   - *AI tools:* How did manual-first (Part 2) compare to Copilot-first (Part 3)?

## Submission Checklist


Before your final submission, ensure:

- [ ] Part 1: You've classified infrastructure vs. domain in AutomationRuleEngine (individual work)
- [ ] Part 2: You've diagnosed the `DatabaseConnection` singleton, designed repository interfaces, and refactored `DeviceManager` to use constructor injection
- [ ] Part 3: You've used Copilot to design ports for AutomationRuleEngine + composition root
- [ ] Part 4: You've explained at least one design decision to another pair and reflected on adding a new feature area
- [ ] `REFLECTION.md` is complete with all 7 questions answered
- [ ] Your Mermaid diagram is saved in `diagrams/automation-rules.md`
- [ ] All changes are committed and pushed to GitHub
