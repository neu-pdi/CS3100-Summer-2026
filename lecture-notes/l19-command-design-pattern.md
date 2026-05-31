---
sidebar_position: 19
lecture_number: 19
title: "Command Design Pattern"
---

* [ Old Design (.zip)](/code/lectures/l19-command-design-pattern/ThermostatsBeforeCommands.zip)
* [ New Design (.zip)](/code/lectures/l19-command-design-pattern/ThermostatsCommandDesign.zip)
 

# 1 Context of the example program

Consider a simple program that allow creating and manipulating thermostats in a smart home. This example was first seen in [the architectural design lecture, to illustrate the hexagonal architecture](lectures/l18-design-architecture.md), and is included here with three changes:

1. A controller that drives the application is included.
2. The controller is capable of taking inputs from any `InputStream` object and transmits output to any view that extends `PrintStream`. This facilitates injecting suitable input and output streams into the controller and promotes testability.
3. A new method in the service: get the ids of all existing thermostats.

We first summarize its capabilities here:

1. Create a new thermostat with a string id and an initial starting temperature.
2. Increase the temperature of a specific thermostat by one degree, given its id.
3. Decrease the temperature of a specific thermostat by one degree, given its id.
4. Get (and print) the temperature of a specific thermostat, given its id.
5. Monitor a specific thermostat. Any subsequent changes in its temperature would automatically produce a printed notification.
6. Save the id and temperature of each thermostat to a text file.

This program offers a command-line interface (CLI). Once the program starts, the user can type in one of the following instructions to execute the operations above. These instructions are (in the same order above):

1. `create <id> <temperature>`
2. `increment <id>`
3. `decrement <id>`
4. `get <id>`
5. `monitor <id>`
6. `save <filepath>`
7. `exit`: Exit the program gracefully

These instructions are parsed in the provided `ThermostatTextScriptProcessor` class and are executed using the provided `SmarthouseServicePort` service, implemented in the `SmarthouseServiceImpl` class.

The code for the parsing of these instructions was initially written as follows:

```java
public class ThermostatTextScriptProcessor {

    ...

    public void process(String command) {
        String[] parts = command.split(" ");
        if (parts[0].equals("create")) {
            service.createThermostat(parts[1], Integer.parseInt(parts[2]));
        } else if (parts[0].equals("increment")) {
            service.incrementTemperature(parts[1]);
        } else if (parts[0].equals("decrement")) {
            service.decrementTemperature(parts[1]);
        } else if (parts[0].equals("get")) {
            System.out.println(service.getTemperature(parts[1]));
        } else if (parts[0].equals("monitor")) {
            service.monitor(parts[1], new PrintMonitorAdapter());
        } else if (parts[0].equals("save")) {
            try {
                service.saveAll(new TextfilePersistAdapter(parts[1]));
            } catch (IOException e) {
                System.out.println("Error saving to file: "+e.getMessage());
            }
        } else {
            System.out.println("Unknown command: "+command);
        }
    }
}

```

# 2 Enhancing the application

We wish to add some new features to this program, and expose them through the CLI. Let us see how this changes our code.

## 2.1 Enhancement 1: Help 

Consider a simple enhancement: we would like to support the instruction `help` that would simply print the above menu of instructions at any time. The program already does this, but in the controller's `control` method.

We could easily do this by modifying the parsing as follows:

```java

public class ThermostatTextScriptProcessor {

    ...

    public void process(String command) {
        String[] parts = command.split(" ");
        if (parts[0].equals("create")) {
            service.createThermostat(parts[1], Integer.parseInt(parts[2]));
        } else if (parts[0].equals("increment")) {
            service.incrementTemperature(parts[1]);
        } else if (parts[0].equals("decrement")) {
            service.decrementTemperature(parts[1]);
        } else if (parts[0].equals("get")) {
            System.out.println(service.getTemperature(parts[1]));
        } else if (parts[0].equals("monitor")) {
            service.monitor(parts[1], new PrintMonitorAdapter());
        } else if (parts[0].equals("save")) {
            try {
                service.saveAll(new TextfilePersistAdapter(parts[1]));
            } catch (IOException e) {
                System.out.println("Error saving to file: "+e.getMessage());
            }
        } else if (parts[0].equals("help")) {
            printMenu();
        } else {
            System.out.println("Unknown command: "+command);
        }
    }

    private void printMenu() {
        ...
    }
}
```

We accomplished this easily by adding another case to the `if-else-if` ladder in the `process` method of the parser class.

## 2.2 Enhancement 2: Remove monitoring

We wish to add a complementary feature to `monitor`: remove the monitors placed on a thermostat. We wish to expose this through the CLI through the instruction `removemonitors <id>`. 

This feature is currently unsupported by the domain itself! Therefore this feature requires us to change the domain classes:

1. Add a method `void removeMonitors();` to the `Thermostat` interface.
2. Implement the method in the `ThermostatImpl` class.
3. Add a method `void disableMonitoring(String id);` to the `SmarthouseServicePort` interface.
4. Implement the method in the `SmarthouseServiceImpl` class.

:::note Code Modification

Note that by directly modifying existing classes and interfaces, we violated the Open-Closed SOLID principle. The more appropriate way would have been to create extended interfaces and classes to add this functionality. We chose to directly modify to keep this change brief and to avoid maintaining separate interfaces and classes that otherwise have no reason to co-exist with existing interfaces and classes.

:::

With this change, we can now modify the parser to support this new instruction:

```java
public class ThermostatTextScriptProcessor {

    ...

    public void process(String command) {
        String[] parts = command.split(" ");
        ...
        .. else if (parts[0].equals("removemonitors")) {
            service.disableMonitoring(parts[1]);
        } else if (...)
        ...
    }
    ...
}

```

Notice what happens: with every feature supported by the program, the parser that parses the instruction entered through the CLI has to be modified by adding one more case. This has the following negative consequences:

1. The growth of this class is non-linear. In some cases it added more code to the parser itself (`printMenu`) and in other cases it adds just three more lines (`removemonitors` calling a single service method like others).
2. The growth is unwieldy. Some `if` statements are longer than others. 
3. The class is harder to debug. Imagine having a bug in the 10th case out of 33 possibilities!
4. The class becomes less cohesive. For example the `help` feature added `printMenu` in this class although it did not strictly belong there. What else will other features bring into this class?

# 3 Design Improvements

We now iteratively improve the design of this example by addressing the above limitations.

## 3.1 The Command Design Pattern

Recall the structure of the `process` method:

```java
public class ThermostatTextScriptProcessor {

    ...

    public void process(String command) {
        String[] parts = command.split(" ");
        if (parts[0].equals("create")) {
            ...
        } else if (parts[0].equals("increment")) {
            ...
        } else if (parts[0].equals("decrement")) {
            ...
        } ...
    }
}

```

First we ensure that each new instruction grows this method *uniformly*. We take a cue from the `help` enhancement above: we added a new private helper method `printMenu` that contained the details of what must be done when `help` is received as input. Similarly imagine if we added one helper method per case:

```java
public class ThermostatTextScriptProcessor {

    ...

    public void process(String command) {
        String[] parts = command.split(" ");
        if (parts[0].equals("create")) {
            createHelper(...);
        } else if (parts[0].equals("increment")) {
            incrementHelper(...);
        } else if (parts[0].equals("decrement")) {
            decrementHelper(...);
        } ...
    }
}

```

Since some of these methods operate upon the service and/or transmit output to the view, we pass the service object and the `PrintStream` object to them as arguments.

We can now characterize each such helper method as follows: *Take the service object, the view object and possibly additional pieces of data, and execute a set of operations on the service*. Note that although the operations that each helper method executes are different (e.g. create a new thermostat, increment temperature, etc.), all of the helper methods can be characterized this way. Since the methods differ *only by name* we can unify them under a single interface that has a method of the same signature: `void execute(SmarthouseServicePort service,PrintStream view);`. 

Design-wise, how can we justify the purpose of such an interface? It represents a high-level command: a set of operations that must be executed. This is an example of the *command* design pattern. This pattern unifies different sets of operations under one umbrella, so that they can be treated uniformly. 


```java

/**
 * This interface represents a basic command. A command encapsulates all
 * the instructions for an "atomic" operation within this application.
 * 
 * A command may just comprise of instructions for the service or 
 * may ask the view to display things or both.
 */
public interface ThermostatCommand {
    void execute(SmarthouseServicePort service,PrintStream view);
}

```

We then implement this interface, once for each text instruction (instead of creating a separate helper method for each of them). Each implementation could take additional data during instantiation. 


```java

/**
 * This class represents a command to create a new thermostat with the specified
 * ID and the specified initial temperature.
 */
public record CreateThermostatCommand(String id,int initialTemperature) implements ThermostatCommand {
    @Override
    public void execute(SmarthouseServicePort service,PrintStream view) {
        service.createThermostat(id,initialTemperature);
    }
}

/**
 * This class represents a command to get the temperature of a thermostat with 
 * the specified ID and transmit it to the view.
 */
public record GetTemperatureCommand(String id) implements ThermostatCommand {

    @Override
    public void execute(SmarthouseServicePort service,PrintStream view) {
        int temperature = service.getTemperature(id);
        view.println(temperature);
    }

}

/**
 * This class represents a command that transmits the menu of instructions to the view.
 */
public class ListCommandsCommand implements ThermostatCommand {

    @Override
    public void execute(SmarthouseServicePort service,PrintStream view) {
        view.println("Commands:");
        view.println("  create <id> <temperature> - Create a new thermostat with the given id and temperature");
        view.println("  increment <id> - Increment the temperature of the thermostat with the given id");
        view.println("  decrement <id> - Decrement the temperature of the thermostat with the given id");
        view.println("  get <id> - Get the current temperature of the thermostat with the given id");
        view.println("  addmonitor <id> - Start monitoring changes to the thermostat with the given id");
        view.println("  removemonitors <id> - Remove monitoring of changes for the thermostat with the given id");
        view.println("  save <filename> - Save all thermostats to a file with the given filename");
        view.println("  help - Print this menu of commands");
        view.println("  exit - Exit the program");
    }

}


```


Now our parser does not have to execute anything: it merely creates and return the appropriate `ThermostatCommand` object: 

```java
public class ThermostatTextScriptProcessor {

    public ThermostatCommand process(String command) {
        String[] parts = command.split(" ");
        ThermostatCommand commandObject = null;
        if (parts[0].equals("create")) {
            commandObject = new CreateThermostatCommand(parts[1],Integer.parseInt(parts[2]));
        } else if (parts[0].equals("get")) {
            commandObject = new GetTemperatureCommand(parts[1]);
        } else if (parts[0].equals("addmonitor")) {
            commandObject = new AddMonitorCommand(parts[1],new PrintMonitorAdapter());
        }
        ...
        return commandObject;

    }
}

```

## 3.2 Advantages of the command design pattern
 
**Commands promote cohesion**

The command design pattern has a *unifying* effect, making unrelated lines of code appear as if working towards the same purpose. This increases cohesion: the `process` is no longer doing *1 of 10 unrelated things*, but *creating commands*. Similarly the controller is only executing commands.

**Commands promote changeability**

Details of each command are now kept in separate classes, instead of all appearing within the controller or a single helper class such as the parser. This allows us to support new instructions without cluttering or editing the controller or parser (almost: because we do need to add code to create the command object...).

**Commands align with program features**

Note that the `SmarthouseServicePort` offers methods that correspond to how the domain objects can be manipulated, but not necessarily *how* these manipulations may be used by the user. In contrast the commands align with *how* the program is used through the CLI (or a GUI).

## 3.3 "Macro" commands

Consider a new operation: *change the temperature of all thermostats by a specified amount (positive or negative)*. While the `ThermostatServicePort` does provide methods to change the temperature of a single thermostat, it does not offer anything to change *all* of them. 

Instead of treating this as a new operation like `removemonitors` that necessitated changes to the service, we can implement this purely at the command level.

```java

/**
 * This enum represents the kinds of change to the temperature of a 
 * thermostat. It is used by the @link{ChangeTemperatureCommand} class.
 */

public enum TemperatureChangeType {
    Increment,
    Decrement
}


/**
 * This class represents a command to change the temperatures of all
 * existing thermostats by the specified increment. The increment may be
 * positive or negative, making it possible to increase or decrease the
 * temperatures of all thermostats at once.
 *
 * This is a "macro" command. No such functionality is offered by the
 * service, but this command uses multiple operations in the service to
 * implement this "meta operation". This shows the potential of using
 * commands to implement newer functionality (within limits) without
 * having to change the service at all.
 */
public record ChangeAllThermostatsCommand(int increment) implements ThermostatCommand {

    @Override
    public void execute(SmarthouseServicePort service,PrintStream view) {
        List<String> ids = service.getAllIds();
        TemperatureChangeType typeOfChange;

        if (increment<0) {
            typeOfChange = TemperatureChangeType.Decrement;
        }
        else {
            typeOfChange = TemperatureChangeType.Increment;
        }
        
        for (String id:ids) {
            ThermostatCommand command = new ChangeTemperatureCommand(id,typeOfChange);
            for (int count = 0;count < Math.abs(increment);count +=1) {
                command.execute(service,view);
            }
        }
    }
}

```

This may be characterized as a "macro": a command that uses other multiple existing operations (or commands!). Other operations that can be defined as macros include monitoring several thermostats at once, printing the temperatures of all thermostats, etc.
 

# 4 Tangent: Factory Method Sighted!

Our implementation of the parser uses another design pattern: the factory method.

Consider the `process` method in our parser:

```java

public class ThermostatTextScriptProcessor {

    public ThermostatCommand process(String command) {
      ...
    }
}

```

This method:

1. Has the primary purpose of manufacturing (creating and returning) objects.
2. Has the capability of returning several different kinds of objects.
3. Has the ability to choose at runtime which object to create and return (depending on what string is passed to it). 

These three properties characterize *factory* methods. The factory method is a useful design pattern in situations where we need to consolidate the creation of similar or related objects in a single place in our application. By doing so, if we change the way one of these objects is created or add new objects to be created, there is primarily one place in our code that needs to be edited. In this way, *factory methods promote changeability*.

Our specific implementation of the factory method can be streamlined a bit more by using a `switch` statement. 

# 5 Streamlining the CLI

When an application primarily receives text inputs (i.e. offers a CLI) we need to write code that accepts such inputs and parses them. So far we have focused on the parsing aspect, but let us review how CLI input was received by our controller:

```java

//simple scanner based input
public void control() {
    ThermostatCommand command;
    
    //welcome message
    view.println("Welcome to the Smarthouse!");
    //print the menu of commands
    new ListCommandsCommand().execute(mainService,view);
    
    ThermostatTextScriptProcessor processor = new ThermostatTextScriptProcessor();
    
    while (sc.hasNext()) {
        String line = sc.nextLine(); //read the next typed line
        if (line.equalsIgnoreCase("exit")) {
            break;
        }
        //process what was typed and get a command object 
        command = processor.process(line);
        if (command!=null) { //if a command object was returned...
            command.execute(mainService,view); //execute it
        }
    }
    sc.close();
}

```

As we can see, the `Scanner` class is quite useful in such situations, and is reasonably easy to use. However this simplistic code misses several features that a user may be accustomed to when entering text input (in a terminal):

* Have a helpful prompt before the user types something.
* Abandon what they wrote and return to the terminal (e.g. using `Ctrl + C`). Typing this in the above program will terminate the entire program.
* Support text colors and possibly syntax highlighting
* Tab-completion features (type a word partly and press tab to autocomplete it).
* Recall history of previously typed commands by using the up and down arrow keys
* Ability to test the code with some or all of the above features

The `JLine` library offers a terminal-like experience within a Java program. It can be used to write capable CLIs for Java applications. 

## 5.1 Using `JLine` within a Gradle project

We can use the `JLine` library by adding the following dependency to our `build.gradle` file.

```java

dependencies {
    //jline
    implementation 'org.jline:jline:4.0.0'
    ...
}

```

## 5.2 Rewriting our controller using `JLine`

Here is an example of our controller for the thermostat application using `JLine`:

```java
//jline without completer
public void control2() {
    ThermostatCommand command;
    
    //welcome message
    view.println("Welcome to the Smarthouse!");
    //print the menu of commands
    new ListCommandsCommand().execute(mainService,view);
    
    ThermostatTextScriptProcessor processor = new ThermostatTextScriptProcessor();
    
    // Create a terminal
    Terminal terminal;
    try {
        terminal = TerminalBuilder.builder()
        .name("custom terminal")
        .streams(in,view) //use our streams, not System.in and System.out
        .system(true)
        .build();
    } catch (IOException e) {
        view.println("Cannot create terminal...quitting.");
        return;
    }

    // Create line reader
    LineReader reader =
    LineReaderBuilder.builder()
            .terminal(terminal)
            .build();

    ...
}
```

The steps are as follows:

1. Create a terminal: this allows us to specify the terminal properties, allow use of custom `InputStream` and `OutputStream` instead of the default `System.in` and `System.out`, etc.
2. Use the terminal to create a `LineReader`. The line reader is used to read user input line-by-line.

This application is *JUnit-ready* because our controller already has the ability to work with any `InputStream` and `PrintStream`.

## 5.3 Tab-completion using `JLine`

Our application uses several instructions: `create`, `get`, `monitor`, `removemonitors`, etc. It would be nice if the user could just type `crea` and press tab to get `create`. JLine supports this functionality by using a *completer*.

A completer is a helper object that can be connected to the line reader. When the tab is pressed, the line reader reads the characters typed in so far, and feeds it to the completer object. The completer then reports with "completed" suggestions based on how it is configured.

In our application, we need a completer that only knows the first part of each valid instruction (`create`, `get`, etc.). We can configure this as follows:

1. Get a list of all supported instructions (already supported by the parser).
2. Configure a `Completer` object with the above.
3. Pass the `Completer` object to the line reader.

```java

public void control() {
  ...
  Terminal terminal;
  // Create a terminal
  ...

  //create a completer for all the commands supported by this program
  String [] commandStrings = processor.getAllCommandNames();

  // Create line reader
  LineReader reader =
  LineReaderBuilder.builder()
          .terminal(terminal)
          .completer(new StringsCompleter(commandStrings)) //completer
          .build();

  ...
}

```

