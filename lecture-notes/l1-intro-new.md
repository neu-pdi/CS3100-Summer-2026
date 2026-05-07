---
sidebar_position: 1
lecture_number: 1
title: Designs and Programming Languages
image: /img/lectures/web/l1.png
---
 
   * [Python Source (.zip)](/code/lectures/l1-intro/python.zip)
   * [Java Source (.zip)](/code/lectures/l1-intro/java.zip)
   
   
# 1 Introduction
 
Computer code in any language consists of only two aspects: representation of relevant data and ways of manipulating that data. And yet, there are multiple ways to organize data and their related functionality to solve a given problem. Programming languages often better support some types of design than others, but the design has a profound impact (often independent of the programming language used to implement it) on what can or cannot be done easily and elegantly. A simple example helps to illustrate this.

# 2 Example problem: IoT Devices
 
Suppose we need to represent two kinds of smart devices: lights and fans. Each device can be given a unique (human-readable) name. But a light has a single power (for simplicity) while a fan has a single speed. Both devices can be turned on and off. Furthermore, each device has its unique way of identifying itself. For example, a light will blink twice while a fan will momentarily turn on.

Let us design and write a program that represents and operates these devices. We will consider two types of designs.
 
## 2.1 Design 1: data and functions operating on data (externally)
 
One way to design the above would be to start by representing the data. We can represent the attributes of a light and fan as two separate *compound data types* ("nouns"), informally as follows: 

```java

Light(name, power, on-status)
Fan(name, speed, on-status)
```

We can then write functions (verbs) that:

  1. Identify the device by producing and returning a string that can be printed (for now, to simulate the identification process)
  
  2. Turn the device on and off.

  3. Get the status of the device (whether it is on or off)

```java

string function identify(device)
function turn_on(device)
function turn_off(device)
boolean status(device)

```

### Example: Python
 
In Python we can represent the above design of lights and fans as dictionary records: 

```python

def createIoTDevice(type, name):
    """This function creates a dictionary that represents a generic IoT device. It has a key called "type" and another for the unique id of the device """
    device = {'type':type,'name':name,'isOn':False} 
    return device

#create a dictionary that represents a light
def createLight(name, power):
    """This function takes in the various attributes for a light and returns a dictionary with keys name and power with their respective values equal to whatever was passed to this function. It also has a key called "type" that has the value "light" """
    record = createIoTDevice("light", name)
    record['power'] = power
    return record

#create a dictionary that represents a fan
def createFan(name, speed):
    """This function takes in the various attributes for a fan and returns a dictionary with keys name and speed with their respective values equal to whatever was passed to this function. It also has a key called "type" that has the value "fan" """
    record = createIoTDevice("fan", name)
    record['speed'] = speed
    return record

```

We can instantiate them as follows: 

```python

#create an instance that represents a living room light
livingRoomLight = createLight("livingRoomLight", 100)

#create an instance that represents a fan
fan = createFan("fan", 50)

```

We can then implement functions to turn the device on or off and to check the device status as follows:  

```python

#check if the given parameter is a valid IoT device
def isIoTDevice(device):
    return (type(device) is dict) and ('type' in device) and ('name' in device) and ('isOn' in device)

#function that turns on the device
def turnOn(device):
    if isIoTDevice(device):
        device['isOn'] = True
    else:
        raise ValueError("Not a valid IoT device")

#function that turns off the device
def turnOff(device):
    if isIoTDevice(device):
        device['isOn'] = False
    else:
        raise ValueError("Not a valid IoT device")

#function that checks if the device is on
def isOn(device):
    if isIoTDevice(device):
        return device['isOn']
    else:
        raise ValueError("Not a valid IoT device")

```
We write helper functions that verify whether the dictionary passed to this function is a valid device or not.

The function to identify a device is a bit more complex, as its behavior depends on the device.

```python

#two more helper functions

#check if the given parameter is a valid light
def isLight(device):
    return (type(device) is dict) and ('type' in device) and (device['type'] == "light") and ('name' in device) and ('power' in device)

    
#check if the given parameter is a fan
def isFan(device):
    return (type(device) is dict) and ('type' in device) and (device['type'] == "fan") and ('name' in device) and ('speed' in device)
        
#function that identifies a device
def identify(device):
    if isLight(device):
        return "Light blinks at {}% power".format(device['power'])
    elif isFan(device):
        return "Fan spins at {}% speed".format(device['speed'])
    else:
        raise ValueError("Unknown device or not a valid IoT device")

```

 
We can use these functions as follows: calling `identify(livingRoomLight)` produces the string "Light blinks at 100% power", and calling `identify(fan)` produces the string "Fan spins at 50% speed".
 
## 2.2 Extending the design
 
Consider the situation of supporting an additional type of device: thermostat. A thermostat also has a name, but it has a temperature. It identifies itself as "Thermostat display on, currently at X temperature". How can this type of device be supported in this type of design?

We can represent a thermostat using another compound data type. 

```python

Thermostat(name,temperature,on-status)

```

In Python, this would translate to 

```python

#create a dictionary that represents a thermostat
def createThermostat(name, temperature):
    """This function takes in the various attributes for a thermostat and returns a dictionary with keys name and temperature with their respective values equal to whatever was passed to this function. It also has a key called "type" that has the value "thermostat" """
    record = createIoTDevice("thermostat", name)
    record['temperature'] = temperature
    return record

#create an instance that represents a thermostat
thermostat = createThermostat("thermostat", 70)


```
The `turnOn()`, `turnOff` and `isOn` would work as-is! But the `identify` would not work as it does not support thermostats. The Python implementation would be changed as follows: 

```python

#check if the given parameter is a thermostat
def isThermostat(device):
    return (type(device) is dict) and ('type' in device) and (device['type'] == "thermostat") and ('name' in device) and ('temperature' in device)


#function that identifies a device
def identify(device):
    if isLight(device):
        ...
    elif isFan(device):
        ...
    elif isThermostat(device):
        return "Thermostat display on, currently at {} temperature".format(device['temperature'])
    else:
        raise ValueError("Unknown device or not a valid IoT device")

```  

We can continue using them as before: calling `identify(thermostat)` generates the string `"Thermostat display on, currently at 70 temperature". 

We see that although possible, supporting an additional type of device creates *substantial* changes to *existing* code (a new case inside existing functions). It is reasonable to expect newer forms of data to be supported as an application evolves, so making extensive changes each time seems like a major limitation of this design.

## 2.3 Design 2: Combining data and functions
 
An alternative organization of data and functions is to pair the data with all the relevant manipulations to it. In other words, we assign the responsibility to a device to *identify itself*. 

One way to do this would be to add functions to each device. 

```python

class IoTDevice: # a structure that represents an IoT device
    """This class represents an IoT device. An IoT device has the following attributes: type, name, and isOn."""
    def __init__(self,type,name): #to instantiate IoT devices
        self.__type__ = type
        self.__name__ = name
        self.__isOn__ = False #by default, an IoT device is off when it is instantiated
    
    #function for an IoT device to identify itself
    def identify(self):
        return "Unknown Device not a valid IoT device"
    #function for an IoT device to turn itself on
    def turnOn(self):
        self.__isOn__ = True
    #function for an IoT device to turn itself off
    def turnOff(self):
        self.__isOn__ = False
    #function for an IoT device to check if it is on
    def isOn(self):
        return self.__isOn__
        
class Light(IoTDevice): # a structure that represents a light
    """This class represents a light-type IoT device. A light has the following attributes: type, id, isOn, and power."""
    def __init__(self,id,power):
        super().__init__("light", id)
        self.__power__ = power

    #function for a light to identify itself
    def identify(self):
        return "Light blinks at {}% power".format(self.__power__)

class Fan(IoTDevice): # a structure that represents a fan
    """This class represents a fan-type IoT device. A fan has the following attributes: type, id, isOn, and speed."""
    def __init__(self,id,speed):
        super().__init__("fan", id)
        self.__speed__ = speed

    #function for a fan to identify itself
    def identify(self):
        return "Fan spins at {}% speed".format(self.__speed__)
```

We can creates instances of these classes as follows: 

```python

#create an instance that represents a living room light
livingRoomLight = Light("livingRoomLight", 100)

#create an instance that represents a fan
fan = Fan("fan", 50)

```

Now that since each instance contains the `identify` function *inside it*, we call `livingRoom.identify()` to identify a device. 

**Note the different ways in which a device is identified.** In the first design `identify(livingRoomLight)` can be described as *"Function identify, take this device and identify it"*. In the second design `livingRoom.identify()` can be described as *"Device, identify yourself"*. 

Both designs achieve the same outcomes: representation of devices and operating on them. But they model the problem in fundamentally different ways. 

## 2.4 Extending the design: Take two
 
How does the second design fare in the same situation of supporting a new kind of device: themostat? Since each type of device is *self-contained*, we can add a `Thermostat` class as before, and implement functions for it. 

```python

class Thermostat(IoTDevice): # a structure that represents a thermostat
    """This class represents a thermostat-type IoT device. A thermostat has the following attributes: type, id, isOn, and temperature."""
    def __init__(self,id,temperature):
        super().__init__("thermostat", id)
        self.__temperature__ = temperature

    #function for a thermostat to identify itself
    def identify(self):
        return "Thermostat display on, currently at {} temperature".format(self.__temperature__)
      
```

That's it! **No** changes to any existing code is required. 

## 2.5 Which design is "better"?

Designs 1 and 2 represent two paradigms, but note that both of them are used to solve the same problem. Design 1 (functions external to data)  separates the data from functions that manipulate it. Such design is commonly found in implementations using functional programming. But it is not uncommon in implementations using procedural languages (such as Python above) as well. Design 2 is "classic object-oriented design." It embodies the basic OO principle of encapsulation: data and its functions are encapsulated (in a class). The resulting objects are self-contained and capable: they represent data (as attributes, often referred to as state) and offer relevant operations (as functions, often referred to as behavior). 
 
Which design is better? In the above situation, we see that incorporating a new device required isolated changes in Design 2. It is tempting to conclude that Design 2 is superior to Design 1. However consider another situation: adding a new operation on devices. In Design 1, this would require writing a new function for this operation that supports all existing type of devices. No changes to existing code would be required. However in Design 2, one would have to *add* a new function to each existing device class. In real-life situations, new features are often demanded *after* a design and implementation are complete. Moreover, they cannot always be anticipated accurately. Thus which design is "better" depends on which *future* changes it is able to support more easily. There is no one universally superior design paradigm. Consequently one must be aware of and open to using different design paradigms as suitable, possibly within the same application. Many modern programming languages support multiple design paradigms to varying degrees, as illustrated by the Python code. So the choice of design paradigm is not solely determined by the language chosen for implementation. This fact makes program design both complicated and interesting.

# 3 From Python to Java
 
Both of the above implementations in Python have some limitations:

  1. In the first implementation, we need to know what kind of a device has been passed to the `identify()` function so that it can work accordingly. Doing so is rather clunky: our helper functions basically differentiate between devices based on the contents of the dictionary representation. *Any* dictionary that happens to have the correct attributes will be mistaken as a device, whether or not it is meaningfully so.

  2. In both implementations, there is no *succinct* way to know what the capabilities of devices are. The `IoTDevice` class in the second implementation does show the functions available to all devices, but it mixes them with the common attributes. 

  3. Python allows reaching into an object to access its attributes. This encourages (or at least allows) writing code that is heavily intertwined. This makes maintaining code over a period of time more challenging.

## 3.1 Replicating the object-oriented design in Java

We see from the above design that all IoTDevice offers some common functionalities: identify, turnOn, turnOff and isOn. In other words, given *any* object that represents an IoTDevice, we can expect that these operations can be called on it. We formalize this requirement of an IoTDevice in Java by representing it as an interface.

```java
/**
 * This interface represents the operations for a single IoT device.
 * An IoTDevice can identify itself and turn itself on and off
 */
public interface IoTDevice {
    /**
     * Identify this device. How a device identifies itself is up to the individual device
     * @return a string representing the response of the device
     */
    String identify();

    /**
     * Turn this device on
     */
    void turnOn();

    /**
     * Turn this device off
     */
    void turnOff();

    /**
     * Return whether this device is on
     * @return true if this device is on, false otherwise
     */
    boolean isOn();
}

```

Any class whose objects claim to be IoT devices *must* implement this interface, and Java will enforce that those classes implement these methods. This is a stronger guarantee than Python, which *merely* verifies whether a function called on an object exists at the time the program is run. Being more specific like this in Java helps to catch non-compliance to this requirement before we even run the program.

We can now implement the `Light` class:

```java
/**
 * This class represents a single light. The light has 
 * a power.
 */
public class Light implements IoTDevice {
    private final int power;
    private final String name;
    private boolean isOn;

    /**
     * Construct a light with the given id and power. The
     * light is off by default.
     * 
     * @param id the name of this light
     * @param power the power of this light
     */
    public Light(String name,int power) {
        this.name = name;
        this.power = power;
        this.isOn = false;
    }

    @Override
    public String identify() {
        return String.format("Light blinks at %d%% power",this.power);
    }

    @Override
    public void turnOn() {
        this.isOn = true;
    }

    @Override
    public void turnOff() {
        this.isOn = false;
    }

    @Override
    public boolean isOn() {
        return this.isOn;
    }
}

```

This class shows several features of Java:

    * `class Light implements IoTDevice` makes the promise that this class provides implementations for all the methods specified in the `IoTDevice` interface. If the class omits any of these methods, Java will produce compilation errors.

    * Notice how each field of this class is marked `private`. This is an access modifier. An access modifier restricts the place in the code from where this field can be accessed. `private` is the most restrictive access modifier: these fields cannot be accessed from anywhere except from inside this class. This is good design practice: always minimize the places from where details of a class can be accessed.

    * All the methods are marked `public`: this means they can be called from anywhere. This is the least restrictive access modifier. 

    * Each method that emanates from the interface is annotated by `@Override`. It indicates that "the origins of this method lie somewhere else, related to this class". Java mandates that all methods in an interface be public in a class that implements that interface. This ensures that a developer can look at an interface and know which methods in an implementing class can be called from anywhere.

    * Note that some of the fields are also marked as `final`. This means that these fields, once initialized in the constructor, cannot be re-assigned. In the above example, since the brightness of the light does not change, this field is marked `final`. Any attempt to re-assign this field will result in a compilation error.

    * Java supports single-line and multiple-line comments. It is best practice to describe an interface or a class in a couple of sentences above it. It is also best practice to write similar documentation for each method inside the class.

    * Java takes its object-oriented nature more seriously. Specifically every method in Java must be written inside a clas or interface.

The `Fan` and `Thermostat` classes are similar and can be found in the accompanying code.

## 3.2 The `main` method

When we run a python file, it runs the instructions that are outside of a function in that file (there are ways to provide a more formal starting point). Java programs on the other hand require a formal starting point. This is a method called `main`. The following `main` method creates some IoTDevice objects and operates them.

```java

public class DeviceMain {
    public static void main(String []args) {
        IoTDevice light = new Light("livingRoomLight", 100);
        IoTDevice fan = new Fan("fan", 50);
        IoTDevice thermostat = new Thermostat("bedroom thermostat",70);

        System.out.println(light.identify());
        System.out.println("Light on status: "+light.isOn());
        System.out.println(fan.identify());
        System.out.println("Fan on status: "+fan.isOn());
        System.out.println(thermostat.identify());
        System.out.println("Thermostat on status: "+thermostat.isOn());
        light.turnOn();
        fan.turnOn();
        thermostat.turnOn();
        System.out.println("Light on status: "+light.isOn());
        System.out.println("Fan on status: "+fan.isOn());
        System.out.println("Themostat on status: "+thermostat.isOn());
    }
}


```
