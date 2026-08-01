---
name: python-project-based-learning
description: Learn Python zero to hero through 8 hands-on projects.
version: 0.1.0
author: Hermes
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Python, Education, Project-Based, Beginner]
---

# Python Project-Based Learning (Zero to Hero)

Learn Python by building 8 progressive projects. Each project reinforces specific concepts and builds on previous ones. Stdlib only — no external dependencies until the API project.

## When to Use

- User says "learn Python from scratch"
- User wants "project-based Python learning"
- User asks "Python zero to hero"
- User wants "hands-on Python projects for beginners"
- User asks "Python projects for learning"

## Prerequisites

- Python 3.8+ installed
- Terminal access
- Text editor (VS Code, vim, nano)
- No external packages needed until Project 7

## How to Run

Each project is a standalone Python file. Run with the `terminal` tool:

```bash
python project_01_calculator.py
python project_02_guess_number.py
...
```

## Quick Reference

| Project | File | Concepts |
|---------|------|----------|
| 1 Calculator | `project_01_calculator.py` | Variables, types, input/output, operators |
| 2 Guess Number | `project_02_guess_number.py` | Conditionals, loops, random |
| 3 Password Manager | `project_03_password_manager.py` | Functions, string methods, validation |
| 4 Shopping List | `project_04_shopping_list.py` | Lists, dictionaries, CRUD operations |
| 5 Notes App | `project_05_notes_app.py` | File I/O, JSON, persistence |
| 6 Bank System | `project_06_bank_system.py` | Classes, OOP, encapsulation |
| 7 Telegram Bot | `project_07_telegram_bot.py` | API requests, async, webhooks |
| 8 E-Commerce | `project_08_ecommerce.py` | SQLite, SQL, database design |

## Procedure

### Project 1: Calculator — Variables & Types
Create `project_01_calculator.py`:
```python
num1 = float(input("First number: "))
num2 = float(input("Second number: "))

print(f"Sum: {num1 + num2}")
print(f"Diff: {num1 - num2}")
print(f"Product: {num1 * num2}")
print(f"Quotient: {num1 / num2 if num2 != 0 else 'Error'}")
```
**Concepts:** `input()`, type casting (`float`, `int`), f-strings, arithmetic operators, zero-division handling.

### Project 2: Guess Number — Conditionals & Loops
Create `project_02_guess_number.py`:
```python
import random

secret = random.randint(1, 100)
attempts = 0

while True:
    guess = int(input("Guess (1-100): "))
    attempts += 1
    if guess < secret:
        print("Higher!")
    elif guess > secret:
        print("Lower!")
    else:
        print(f"Correct! Attempts: {attempts}")
        break
```
**Concepts:** `import`, `random.randint()`, `while True`, `if/elif/else`, loop control with `break`.

### Project 3: Password Manager — Functions & Validation
Create `project_03_password_manager.py`:
```python
def validate_password(pwd: str) -> bool:
    checks = [
        len(pwd) >= 8,
        any(c.isupper() for c in pwd),
        any(c.islower() for c in pwd),
        any(c.isdigit() for c in pwd),
        any(not c.isalnum() for c in pwd)
    ]
    return all(checks)

def generate_password(length: int = 12) -> str:
    import secrets, string
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

while True:
    pwd = input("Enter password (or 'gen'): ")
    if pwd == 'gen':
        print(f"Generated: {generate_password()}")
    elif validate_password(pwd):
        print("Strong!")
        break
    else:
        print("Weak: need 8+ chars, upper, lower, digit, special")
```
**Concepts:** Function definitions, type hints, docstrings, `all()`, `any()`, generator expressions, `secrets` module.

### Project 4: Shopping List — Lists & Dicts
Create `project_04_shopping_list.py`:
```python
shopping_list = []

def add_item(name, qty=1):
    shopping_list.append({"name": name, "qty": qty, "bought": False})

def show_list():
    for i, item in enumerate(shopping_list, 1):
        status = "✓" if item["bought"] else " "
        print(f"{i}. [{status}] {item['name']} x{item['qty']}")

def toggle_bought(index):
    if 0 <= index < len(shopping_list):
        shopping_list[index]["bought"] = not shopping_list[index]["bought"]

# Menu loop
while True:
    print("\n1.Add 2.Show 3.Toggle 4.Exit")
    choice = input("Choose: ")
    if choice == "1": add_item(input("Name: "))
    elif choice == "2": show_list()
    elif choice == "3": toggle_bought(int(input("Index: "))-1)
    elif choice == "4": break
```
**Concepts:** List of dicts, `enumerate()`, list methods (`append`, `pop`), menu-driven CLI.

### Project 5: Notes App — File I/O & JSON
Create `project_05_notes_app.py`:
```python
import json, os

FILE = "notes.json"

def load_notes():
    if os.path.exists(FILE):
        with open(FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

notes = load_notes()

def add_note(title, content):
    notes.append({"title": title, "content": content})
    save_notes(notes)

def list_notes():
    for i, n in enumerate(notes, 1):
        print(f"{i}. {n['title']}: {n['content'][:50]}...")
```
**Concepts:** `os.path.exists()`, `json.load/dump`, `with open()`, encoding, persistent storage.

### Project 6: Bank System — Classes & OOP
Create `project_06_bank_system.py`:
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    type: str
    amount: float
    timestamp: str = datetime.now().isoformat()

class Account:
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self._balance = initial_balance
        self.history = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0: return False
        self._balance += amount
        self.history.append(Transaction("deposit", amount))
        return True

    def withdraw(self, amount):
        if amount <= 0 or amount > self._balance: return False
        self._balance -= amount
        self.history.append(Transaction("withdraw", amount))
        return True

    def statement(self):
        print(f"\n=== {self.owner}'s Statement ===")
        for t in self.history:
            print(f"{t.timestamp[:19]} | {t.type:8} | {t.amount:>10.2f}")
        print(f"Balance: {self._balance:.2f}")

acc = Account("Abolfazl", 1000)
acc.deposit(500)
acc.withdraw(200)
acc.statement()
```
**Concepts:** `@dataclass`, `@property`, encapsulation (`_private`), type hints, datetime.

### Project 7: Telegram Bot — API & HTTP
Create `project_07_telegram_bot.py`:
```python
import requests, os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_msg(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset: params["offset"] = offset
    return requests.get(f"{API}/getUpdates", params=params).json()

offset = None
while True:
    data = get_updates(offset)
    for u in data.get("result", []):
        offset = u["update_id"] + 1
        if "message" in u:
            msg = u["message"]
            send_msg(msg["chat"]["id"], f"Echo: {msg.get('text', '')}")
```
**Concepts:** Environment variables, HTTP requests, long polling, JSON API, message handling.

### Project 8: E-Commerce — SQLite Database
Create `project_08_ecommerce.py`:
```python
import sqlite3
from dataclasses import dataclass
from typing import List

DB = "shop.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                price REAL,
                stock INTEGER
            )
        """)

def add_product(name, price, stock):
    try:
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                         (name, price, stock))
            return True
    except sqlite3.IntegrityError:
        return False

def list_products():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute("SELECT * FROM products").fetchall()]

def place_order(product_id, qty):
    with sqlite3.connect(DB) as conn:
        prod = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        if not prod or prod["stock"] < qty:
            return False
        conn.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))
        conn.execute("INSERT INTO orders (product_id, qty, total) VALUES (?, ?, ?)",
                     (product_id, qty, prod["price"] * qty))
        return True

init_db()
add_product("Laptop", 50000000, 10)
for p in list_products():
    print(f"{p['id']}. {p['name']} - {p['price']:,} Toman (Stock: {p['stock']})")
```
**Concepts:** `sqlite3`, parameterized queries, `dataclass`, transactions, foreign keys, `row_factory`.

## Pitfalls

- **Project 1:** Forgetting `float()` on input causes string concatenation instead of math.
- **Project 2:** No input validation crashes on non-numeric input. Wrap `int()` in `try/except`.
- **Project 3:** `secrets` is cryptographically secure; `random` is not for passwords.
- **Project 5:** JSON doesn't support all Python types (set, tuple). Convert before saving.
- **Project 6:** Never expose `_balance` directly — use `@property`.
- **Project 7:** Never hardcode bot token. Use `os.environ.get()`.
- **Project 8:** Always use `?` placeholders, never f-strings in SQL (injection risk).
- **Rate limits:** Telegram API allows ~30 msg/sec. Add `time.sleep(0.1)` in loops.

## Verification

Run each project and verify output:

```bash
# Project 1
python project_01_calculator.py
# Input: 10, 5 -> Output shows 15, 5, 50, 2.0

# Project 2
python project_02_guess_number.py
# Guess correctly -> shows attempt count

# Project 3
python project_03_password_manager.py
# Input: "Abc123!@" -> "Strong!"

# Project 4
python project_04_shopping_list.py
# Add items, toggle, list works

# Project 5
python project_05_notes_app.py
# Notes persist after restart

# Project 6
python project_06_bank_system.py
# Statement shows transactions

# Project 7
python project_07_telegram_bot.py
# Bot responds to messages

# Project 8
python project_08_ecommerce.py
# Products listed, order reduces stock
```

All projects run with stdlib except Project 7 (requires `requests` and `TELEGRAM_BOT_TOKEN` env var).