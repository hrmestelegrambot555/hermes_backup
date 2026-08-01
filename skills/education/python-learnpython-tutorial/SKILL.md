---
name: python-learnpython-tutorial
description: Interactive Python tutorial following learnpython.org.
version: 0.1.0
author: Hermes
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Python, Education, Tutorial, Beginner]
---

# Python Interactive Tutorial (learnpython.org)

Interactive Python tutorial following learnpython.org structure. Covers basics to advanced topics including decorators, closures, and CSV parsing. Stdlib only — no external packages needed.

## When to Use

- User says "learn Python"
- User wants "Python tutorial"
- User asks "Python basics"
- User wants "interactive Python learning"
- User asks "Python course from scratch"

## Prerequisites

- Python 3.8+ installed
- Terminal access
- Text editor
- No external packages needed

## How to Run

Each tutorial is a standalone Python file. Run with the `terminal` tool:

```bash
python tutorial_01_hello_world.py
python tutorial_02_variables.py
...
```

## Quick Reference

| # | Tutorial | File | Concepts |
|---|----------|------|----------|
| 1 | Hello, World! | `tutorial_01_hello_world.py` | print(), comments, indentation |
| 2 | Variables & Types | `tutorial_02_variables.py` | int, float, str, bool, type() |
| 3 | Lists | `tutorial_03_lists.py` | [], append, pop, slice, len() |
| 4 | Basic Operators | `tutorial_04_operators.py` | +, -, *, /, //, %, **, ==, != |
| 5 | String Formatting | `tutorial_05_string_format.py` | f-strings, .format(), % |
| 6 | String Operations | `tutorial_06_string_ops.py` | .upper, .lower, .split, .join |
| 7 | Conditions | `tutorial_07_conditions.py` | if/elif/else, and, or, not |
| 8 | Loops | `tutorial_08_loops.py` | for, while, range(), break |
| 9 | Functions | `tutorial_09_functions.py` | def, return, args, *args, **kwargs |
| 10 | Classes & Objects | `tutorial_10_classes.py` | class, __init__, self, methods |
| 11 | Dictionaries | `tutorial_11_dicts.py` | {}, .keys(), .values(), .items() |
| 12 | Modules & Packages | `tutorial_12_modules.py` | import, from...import, pip |
| 13 | Input & Output | `tutorial_13_io.py` | input(), print(), file I/O |
| 14 | Generators | `tutorial_14_generators.py` | yield, generator expression |
| 15 | List Comprehensions | `tutorial_15_list_comp.py` | [x for x in ...], filters |
| 16 | Lambda Functions | `tutorial_16_lambda.py` | lambda, map, filter |
| 17 | Multiple Args | `tutorial_17_multi_args.py` | *args, **kwargs, default values |
| 18 | Regular Expressions | `tutorial_18_regex.py` | re.match, re.search, re.findall |
| 19 | Exception Handling | `tutorial_19_exceptions.py` | try/except, raise, finally |
| 20 | Sets | `tutorial_20_sets.py` | set(), union, intersection, difference |
| 21 | Serialization | `tutorial_21_serialization.py` | json.dumps/loads, pickle |
| 22 | Partial Functions | `tutorial_22_partial.py` | functools.partial |
| 23 | Code Introspection | `tutorial_23_introspection.py` | dir(), type(), help() |
| 24 | Closures | `tutorial_24_closures.py` | nested functions, nonlocal |
| 25 | Decorators | `tutorial_25_decorators.py` | @decorator, function wrapping |
| 26 | Map, Filter, Reduce | `tutorial_26_map_filter.py` | map(), filter(), reduce() |
| 27 | CSV Parsing | `tutorial_27_csv.py` | csv.reader, csv.DictReader |

## Procedure

### Tutorial 1: Hello, World! — print(), comments, indentation
Create `tutorial_01_hello_world.py`:
```python
# This is a comment
print("Hello, World!")

# Multi-line string
print("""This is
a multi-line
string""")

# Indentation (4 spaces)
if True:
    print("Indented block")
    print("Still in block")
print("Out of block")
```
**Concepts:** `print()`, single/multi-line comments, indentation rules (4 spaces).

### Tutorial 2: Variables & Types — int, float, str, bool
Create `tutorial_02_variables.py`:
```python
name = "Python"
version = 3.11
year = 1991
is_awesome = True

print(type(name))
print(type(version))
print(type(year))
print(type(is_awesome))

num_str = "42"
num_int = int(num_str)
num_float = float(num_str)
```
**Concepts:** Variable assignment, `type()`, type conversion.

### Tutorial 3: Lists — [], append, pop, slice
Create `tutorial_03_lists.py`:
```python
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]

print(fruits[0])
print(fruits[-1])

fruits.append("date")
fruits.insert(1, "blueberry")
fruits.pop()
fruits.remove("banana")

print(numbers[1:3])
print(len(fruits))
```
**Concepts:** List creation, indexing, slicing, `append()`, `pop()`, `remove()`, `len()`.

### Tutorial 4: Basic Operators
Create `tutorial_04_operators.py`:
```python
a, b = 10, 3
print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)

print(a == b)
print(a != b)
print(a > b)

x, y = True, False
print(x and y)
print(x or y)
print(not x)
```
**Concepts:** Arithmetic, comparison, logical operators.

### Tutorial 5: String Formatting
Create `tutorial_05_string_format.py`:
```python
name = "Abolfazl"
age = 25

print(f"Hello, {name}! You are {age} years old.")
print("Hello, {}! You are {} years old.".format(name, age))

pi = 3.14159
print(f"Pi is {pi:.2f}")
print(f"Number: {1000000:,}")
```
**Concepts:** f-strings, `.format()`, number formatting.

### Tutorial 6: String Operations
Create `tutorial_06_string_ops.py`:
```python
text = "Hello, World!"

print(text.upper())
print(text.lower())
print(text.find("World"))
print(text.count("l"))
print(text.startswith("Hello"))
print(text.split(", "))
print(" - ".join(["Hello", "World"]))
print(text.replace("World", "Python"))
print("  hello  ".strip())
```
**Concepts:** String methods.

### Tutorial 7: Conditions
Create `tutorial_07_conditions.py`:
```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Grade: {grade}")

age = 20
has_id = True
if age >= 18 and has_id:
    print("Allowed")

status = "adult" if age >= 18 else "minor"
```
**Concepts:** `if/elif/else`, logical operators, ternary operator.

### Tutorial 8: Loops
Create `tutorial_08_loops.py`:
```python
for i in range(5):
    print(i)

fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

count = 0
while count < 5:
    print(count)
    count += 1

for i in range(10):
    if i == 3: continue
    if i == 7: break
    print(i)

for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```
**Concepts:** `for`, `while`, `range()`, `break`, `continue`, `enumerate()`.

### Tutorial 9: Functions
Create `tutorial_09_functions.py`:
```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Abolfazl"))

def power(base, exponent=2):
    return base ** exponent

print(power(3))
print(power(3, 3))

def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([1, 5, 3, 9, 2])
```
**Concepts:** `def`, `return`, default arguments, multiple return values.

### Tutorial 10: Classes & Objects
Create `tutorial_10_classes.py`:
```python
class Dog:
    species = "Canis familiaris"
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        return f"{self.name} says Woof!"
    
    def __str__(self):
        return f"{self.name} is {self.age} years old"

dog1 = Dog("Rex", 5)
print(dog1.bark())
print(dog1)
```
**Concepts:** `class`, `__init__`, `self`, instance attributes, methods, `__str__`.

### Tutorial 11: Dictionaries
Create `tutorial_11_dicts.py`:
```python
person = {
    "name": "Abolfazl",
    "age": 25,
    "skills": ["Python", "JavaScript"]
}

print(person["name"])
print(person.get("email", "N/A"))

person["age"] = 26
person["email"] = "test@test.com"
del person["age"]

for key, value in person.items():
    print(f"{key}: {value}")
```
**Concepts:** Dict creation, access, modification, `.keys()`, `.values()`, `.items()`.

### Tutorial 12: Modules & Packages
Create `tutorial_12_modules.py`:
```python
import math
print(math.pi)

from random import randint, choice
print(randint(1, 10))
print(choice(["a", "b"]))

import datetime as dt
now = dt.datetime.now()
print(now.strftime("%Y-%m-%d %H:%M"))
```
**Concepts:** `import`, `from...import`, alias, common stdlib modules.

### Tutorial 13: Input & Output
Create `tutorial_13_io.py`:
```python
name = input("Enter your name: ")
print(f"Hello, {name}!")

with open("test.txt", "w") as f:
    f.write("Hello, World!\n")

with open("test.txt", "r") as f:
    content = f.read()
    print(content)

import json
data = {"name": "Abolfazl", "age": 25}
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
```
**Concepts:** `input()`, `with open()`, file modes, JSON read/write.

### Tutorial 14: Generators
Create `tutorial_14_generators.py`:
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for i in countdown(5):
    print(i)

squares = (x**2 for x in range(10))
print(sum(squares))
```
**Concepts:** `yield`, generator functions, generator expressions.

### Tutorial 15: List Comprehensions
Create `tutorial_15_list_comp.py`:
```python
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
matrix = [[i*j for j in range(3)] for i in range(3)]
word_lengths = {word: len(word) for word in ["hello", "world"]}
unique_lengths = {len(word) for word in ["hello", "world", "hi"]}
```
**Concepts:** List/dict/set comprehensions, nested comprehensions, filtering.

### Tutorial 16: Lambda Functions
Create `tutorial_16_lambda.py`:
```python
square = lambda x: x ** 2
print(square(5))

numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))

words = ["banana", "apple", "cherry"]
sorted_words = sorted(words, key=lambda w: len(w))
```
**Concepts:** `lambda`, `map()`, `filter()`, key functions.

### Tutorial 17: Multiple Function Arguments
Create `tutorial_17_multi_args.py`:
```python
def add_all(*args):
    return sum(args)

print(add_all(1, 2, 3))

def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Abolfazl", age=25)

def complex_func(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")
```
**Concepts:** `*args`, `**kwargs`, unpacking.

### Tutorial 18: Regular Expressions
Create `tutorial_18_regex.py`:
```python
import re

text = "My phone is 123-456-7890"
phones = re.findall(r'\d{3}-\d{3}-\d{4}', text)
print(phones)

match = re.search(r'\d+', text)
if match:
    print(match.group())

new_text = re.sub(r'\d{3}-\d{3}-\d{4}', 'XXX-XXX-XXXX', text)
print(new_text)
```
**Concepts:** `re.findall()`, `re.search()`, `re.sub()`, patterns.

### Tutorial 19: Exception Handling
Create `tutorial_19_exceptions.py`:
```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

try:
    num = int(input("Enter a number: "))
except ValueError:
    print("Not a valid number!")

def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age
```
**Concepts:** `try/except/else/finally`, exception types, `raise`.

### Tutorial 20: Sets
Create `tutorial_20_sets.py`:
```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)
print(a & b)
print(a - b)
print(a ^ b)
```
**Concepts:** Set creation, union, intersection, difference.

### Tutorial 21: Serialization
Create `tutorial_21_serialization.py`:
```python
import json
import pickle

data = {"name": "Abolfazl", "scores": [90, 85, 92]}
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

with open("data.json", "r") as f:
    loaded = json.load(f)
```
**Concepts:** `json.dump/load`, `pickle.dump/load`.

### Tutorial 22: Partial Functions
Create `tutorial_22_partial.py`:
```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))
print(cube(5))
```
**Concepts:** `functools.partial`.

### Tutorial 23: Code Introspection
Create `tutorial_23_introspection.py`:
```python
print(type(42))
print(isinstance(42, int))
print(dir("hello"))
print(hasattr("hello", "upper"))
print(callable(print))
```
**Concepts:** `type()`, `isinstance()`, `dir()`, `hasattr()`, `callable()`.

### Tutorial 24: Closures
Create `tutorial_24_closures.py`:
```python
def outer_func(x):
    def inner_func(y):
        return x + y
    return inner_func

add_five = outer_func(5)
print(add_five(3))

def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

counter = make_counter()
print(counter())
```
**Concepts:** Nested functions, `nonlocal`, closures.

### Tutorial 25: Decorators
Create `tutorial_25_decorators.py`:
```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time()-start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done!"

slow_function()
```
**Concepts:** `@decorator`, `functools.wraps`.

### Tutorial 26: Map, Filter, Reduce
Create `tutorial_26_map_filter.py`:
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

squared = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))
total = reduce(lambda a, b: a + b, numbers)

print(squared, evens, total)
```
**Concepts:** `map()`, `filter()`, `reduce()`.

### Tutorial 27: CSV Parsing
Create `tutorial_27_csv.py`:
```python
import csv
from io import StringIO

csv_data = """name,age,city
Abolfazl,25,Tehran
Sara,22,Shiraz"""

reader = csv.DictReader(StringIO(csv_data))
for row in reader:
    print(f"{row['name']} is {row['age']} from {row['city']}")
```
**Concepts:** `csv.reader`, `csv.DictReader`.

## Pitfalls

- IndentationError if inconsistent (mix tabs/spaces).
- `type()` returns class, not string. Use `isinstance()`.
- f-strings need Python 3.6+. Use `.format()` for older versions.
- Infinite loop if `while` condition never becomes False.
- Forgetting `self` in method definitions causes TypeError.
- Generators are consumed once. Recreate if needed.
- Regex patterns use raw strings `r''` to avoid escape issues.
- Bare `except:` catches all exceptions. Be specific.
- Pickle is not secure. Don't unpickle untrusted data.
- Forgetting `@functools.wraps` loses function metadata.

## Verification

Run each tutorial and verify output:

```bash
python tutorial_01_hello_world.py
# Output: Hello, World!

python tutorial_09_functions.py
# Shows greet, power, get_min_max results

python tutorial_25_decorators.py
# Shows timing output
```

All tutorials run with stdlib only — no pip install needed.