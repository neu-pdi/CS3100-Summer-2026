---
title: "Assignment 1: Sets of Rectangles"
sidebar_position: 2
---

Sets of Rectangles
=========

Starter code: [code.zip](/code/assignments/setofrectangles/code.zip)

# 1 Introduction

A lot of applications have "tile" data: data that can be represented using rectangular tiles in 2D space. Google map tiles, 2D drawings and designs, floor plans are some examples. In this assignment we will work with axis-aligned rectangles (i.e. rectangles whose sides are horizontal and vertical only). Such rectangles are characterized by the position of their lower left corner $(x,y)$, their width and height. For simplicity we will assume all of these quantities are integers, and the width and height are positive. We will specifically target 2D drawing as an application.

Many figures, such as building facades can be represented using rectangles. When an architect designs a building facade, they add rectangular artifacts such as panels, billboards, etc. Sometimes they cut out rectangular windows from existing facades. Such figures can be represented as a set of axis-aligned rectangles, with various set-like operations defined on them. 

# 2 Sets of Rectangles

A set of rectangles is defined as a collection of non-overlapping axis-aligned rectangles **(rectangles that touch can co-exist in the set)**. This means that the total area occupied by the drawing is simply the sum of the areas of rectangles that make up the drawing. Being a set, there is no possibility of the same rectangle occurring more than once. The figure below illustrates some examples.

![Image not loaded](/img/assignments/set-of-rectangles/set-examples.png)

The leftmost example shows a valid set of rectangles. The middle example shows an invalid set, because the rectangles overlap over a non-zero area. But they can be broken down into other rectangles that create the same figure, which is what the rightmost example shows. 

We imagine the following operations on it:

   1. Add a rectangular area to the set (while retaining its definition above). This rectangular area may or may not overlap with areas within the set.
   2. Subtract a rectangular area from the set. This rectangular area may or may not overlap with areas within the set.
   3. Get all the rectangular areas inside a set.

We explain the logic between these operations below.

# 2.1 Overlapping rectangles

Given two rectangles, how do we find out if they overlap or not? The problem can be simplified by thinking of a rectangle as made of a horizontal range $(x_{min},x_{max})$ and a vertical range $(y_{min},y_{max})$. Two rectangles overlap in area if they overlap both in their horizontal and vertical ranges. Moreover their area of overlap is also a rectangle! This is called the intersection of the two rectangles. 

# 2.2 Contained difference $(A \setminus B)$

Consider a set that contains a single rectangle $A$. We consider another rectangle $B$ such that $B$ is fully contained in $A$, i.e. there is no part of $B$ that does not overlap with $A$. We wish to compute the set of rectangles that represents the subtraction of $B$ from $A$. The illustration below shows some cases:

![Image not loaded](/img/assignments/set-of-rectangles/contained-difference.png)

We divide $A$ into $4$ rectangles as the first example shows. If some sides of the rectangles coincide then we may get fewer rectangles as the next two examples show. This contained difference operation is the building block for the two set operations we actually want.

# 2.3 Subtracting a rectangle from a set $(S - A)$

![Image not loaded](/img/assignments/set-of-rectangles/subtract.png)

Consider a set $S$ of rectangles. We wish to subtract a rectangle $B$ from this set. This can be accomplished as follows:

   1. Initialize the result set $T$ to be empty.
   2. For each rectangle $A$ in $S$:

       i. If $B$ does not overlap with $A$ add $A$ to $T$ and move to the next rectangle.

       ii. If $B$ overlaps with $A$ in a non-zero area, find their intersection $R$, and add the contained difference (subtract $R$ from $A$) to $T$.

   3. Return $T$ as the result.

# 2.3 Add a rectangle to a set $(A + B)$

![Image not loaded](/img/assignments/set-of-rectangles/add.png)

Consider a set $S$ of rectangles. We wish to add a rectangle $B$ to this set. As it turns out, this operation is an extension of subtraction:

   1. Compute $T$ as $S - B$.
   2. Add $B$ to $T$ and return the result.

# 3 What to do

All code should be in the `box` package. 

You are provided the `BoxSet` interface with this assignment. Here are the details of each method:
   

   * The `add` and `subtract` methods should throw an `IllegalArgumentException` if the box passed to it does not have a positive width and height.
   * The `getBoxes` method should return an array with each element containing exactly four numbers: the x, y, width and height of the rectangle in that order. For example, if there are two rectangles in this set, then the first rectangle would be (arr[0][0],arr[0][1],arr[0][2],arr[0][3]) and the second rectangle would be (arr[1][0],arr[1][1],arr[1][2],arr[1][3]).

Your task is to implement this interface in a class named `SimpleBoxSet` and test it. This class should have only one public constructor that does not take any arguments and creates an empty set of boxes. Other than this constructor and the methods mandated by the interface, it should have no other new public methods. 

Here are some helpful pointers:

   * You may use any suitable way available in the JDK to represent the set of rectangles. **However you are not allowed to use the existing `Rectangle` class available in the JDK**.
   * Note that the `add` and `subtract` method do not return anything. That is, they change the current set to the result.
   * Note that this is a "set" of boxes: it should not contain the same box more than once.
   * Note that the `getBoxes` method does not impose any order on the rectangles that are returned. In other words, this implementation can return the rectangles in any order, so long as it returns all of them.
   * To create an array for the `getBoxes` method, use this: `arr = new int[n][4]` where `n` is the number of rectangles.

You are encouraged to write other interfaces and classes as you see fit. However your work will also be judged by the design of those classes (in other words, you have the freedom to define other classes and interfaces, but do not have the freedom to design them as badly as you want without a point penalty).

# 3.1 Testing

You are expected to test your code thoroughly. This means you should write tests for the `SimpleBoxSet` class as well as any other classes that you choose to write yourself. The recommended way to approach testing is:

   1. Write an empty class (name, fields and constructor only).
   2. Write tests for various methods of this class (don't forget to test constructors, as well as exceptional conditions).
   3. Complete the class and make sure it passes all your tests.

If you wrote other classes, you are expected to write tests for them as well.


## 3.2 Documentation

We expect your code to be well-commented. The expectations are: 

   * Each interface and class contains a comment above it explaining specifically what it represents. This should be in plain language, understandable by anybody wishing to use it. Comment above a class should be specific: it should not merely state that it is an implementation of a particular interface.

   * Each public method in the interface should have information about what this method accomplishes (purpose), the nature and explanation of any arguments, return values and exceptions thrown by it and whether it changes the calling object in any way (contract).

   * If a class implements a method declared in an interface that it implements, **and** the comments in the interface describe this implementation completely and accurately, there is no need to replicate that documentation in the class.

   * All comments should be in Javadoc-style.



# Criteria for grading
 You will be graded on: 

   1. The correctness of your methods.

   2. How well you have tested your methods.

   3. Whether you have written enough comments for your classes and methods, and whether they are in proper Javadoc style.

   4. Whether you have placed appropriate restrictions on attributes and methods.

   5. Whether your code is modular, and each method/class has been designed suitably.

   6. Whether your code is formatted correctly (according to the style grader).
