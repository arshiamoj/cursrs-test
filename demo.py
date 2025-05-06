#!/usr/bin/env python3
import time
import pexpect
import random
import os

def type_text(child, text, delay_range=(0.1, 0.4)):
    for char in text:
        child.send(char)
        time.sleep(random.uniform(*delay_range))
        if random.random() < 0.2:
            time.sleep(random.uniform(0.2, 0.5))

def press_key(child, key):
    if key.lower() == "return":
        child.sendline("")
    else:
        child.send(key)

def main():
    # Start main.py process
    child = pexpect.spawn("python3 main.py", encoding='utf-8')

    # Optional: uncomment if you want to see output for debugging
    # child.logfile = sys.stdout

    time.sleep(8)

    # Simulate pressing 'a'
    press_key(child, 'a')

    time.sleep(3.5)

    # Type name
    name = "Hamlet"
    type_text(child, name)
    press_key(child, "return")

    time.sleep(4.5)

    # Type quote word-by-word
    quote = "To be, or not to be"
    words = quote.split()
    for i, word in enumerate(words):
        type_text(child, word)
        if i < len(words) - 1:
            press_key(child, ' ')
            time.sleep(0.3)

    press_key(child, "return")

    time.sleep(5)

    try:
        key = input("Press 'd' to delete pending_quotes.json or any other key to send Shift+0: ").strip().lower()
        if key == 'd':
            if os.path.exists("pending_quotes.json"):
                os.remove("pending_quotes.json")
            child.terminate()
        else:
            # Simulate Shift+0 as the character ')'
            press_key(child, ')')
    except KeyboardInterrupt:
        child.terminate()

if __name__ == "__main__":
    main()
