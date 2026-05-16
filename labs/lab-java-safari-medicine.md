# Objectives
 
The objectives of this lab are: 

* Practice designing equality between objects and implementing it.
* Write JUnit tests to verify that implementation matches the specification.
 

# 2 The `Medicine` interface
 
In this lab, you will implement several classes that represent medicine in various forms. A medicine in any form contains a certain weight of its active ingredient. There are three levels of concentration: Low (10mg), Medium (20mg) and High (30mg). 

A medicine is represented by the `Medicine` interface. This interface should contain the following methods: 

* A method to retrieve the weight of its active ingredient in mg: `int getWeightOfActiveIngredient()`.

* A method to get the category of its concentration: `String getConcentrationCategory()`. Depending on the weight of its active ingredient, it returns "Low", "Medium", "High" or "Invalid Concentration".  

 
# 3 What to do: Part 1
 
* Create the `Medicine` interface, and document its specifications as detailed above.

* Design JUnit tests that verify these specifications for two implementations: `Pill` and `Syrup`.

* Implement the `Medicine` interface in a `Pill` class. Leave all the methods blank for now, but document them properly. The specifications for this implementation (beyond what the interface specifies) are: 

   * This class represents medicine in pill form.

   * Its only constructor takes the (integral) weight of its active ingredient in mg as its only parameter. The constructor should throw an `IllegalArgumentException` if a negative weight is passed. 

   * For each method to be implemented in the `Pill` class: design and write all JUnit tests to verify its specification, then complete the implementation and run the tests. Proceed in this "write tests -> implement method -> run tests" to complete the class. Follow the directions in Lab 1 to place the test files correctly in your project. 

* Implement the `Medicine` interface in a `Syrup` class. Leave all the methods blank for now, but document them properly. The specifications for this implementation (beyond what the interface specifies) are: 

   * This class represents medicine in syrup form. It has a concentration in mg/ml and dosage in ml.

   * Its only constructor takes the (integral) concentration in mg/ml and dosage in ml as its only parameters. The constructor should throw an `IllegalArgumentException` if a negative concentration or dosage is passed. 

   * For each method to be implemented in the `Syrup` class: design and write all JUnit tests to verify its specification, then complete the implementation and run the tests. Proceed in this "write tests -> implement method -> run tests" to complete the class. Follow the directions in Lab 1 to place the test files correctly in your project. 

Due to limitations in manufacturing tolerances, either form of medicine is not perfectly made. Doctors have determined that if the medicine has an active ingredient weight that is within 2mg of a concentration, then the medicine can be safely taken if that concentration is prescribed. For example, medicine with 11mg or 8mg of active ingredient can be safely taken by a patient who is prescribed a low dose of that medicine.

Override the `equals` method(s) so that two medicines whose active ingredient weight is within 2mg of each other are considered equal. Write tests for it. Don't forget `hashCode`! 
 
# 4 Question to ponder and discuss: Part 1
 
Is the above notion of equality mathematically sound? How would you test the mathematical soundness of your equality implementation? Discuss with the person next to you, and write it in REFLECTION.md.

If you think that the above notion of equality is mathematically sound, include test(s) in your reflection that verify its mathematical soundness. If you think it is not mathematically sound, include at least one test in your reflection that should pass, but does not on your implementation.

# 5 What to do: Part 2
 
Comment out your earlier implementation of equality and hash code, and replace with a new one: two medicines are the same if they have the same safe concentration, or they are both within the range of the same concentration (e.g. they are both between "Low" and "Medium" but are not safe for either). Write tests for this new implementation (preserve your earlier code and tests in comments).

**Do not submit to the submission server yet!** 

# 6 Question to ponder and discuss: Part 2
 
Discuss the following points with the person next to you, and include your answers in REFLECTION.md: 

   1. Is this new notion of equality mathematically sound? How can one test this?

   2. Is this new notion of equality the same as the first one? Present an argument for why it is, or present a counterexample (i.e. examples that are equal by one notion but not the other).

   3. Which notion of equality seems more "natural" and why? Does this exercise provide any general insights about determining equality among objects that involves floating-point values?
 
**Fix the style, and submit on the submission server.**