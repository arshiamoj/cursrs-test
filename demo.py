#!/usr/bin/env python3
import time
import subprocess
import sys
import random
import os

def type_text(text, delay_range=(0.1, 0.4)):
    for char in text:
        subprocess.run(["xdotool", "type", char])
        time.sleep(random.uniform(*delay_range))
        if random.random() < 0.2:
            time.sleep(random.uniform(0.2, 0.5))

def press_key(key):
    subprocess.run(["xdotool", "key", key])

def main():
    try:
        app_process = subprocess.Popen(["python3", "main.py"])
    except Exception:
        sys.exit(1)

    time.sleep(8)

    press_key('a')

    time.sleep(3.5)

    name = "Hamlet"
    type_text(name)

    time.sleep(3)
    press_key('Return')

    time.sleep(4.5)

    quote = "To be, or not to be"
    words = quote.split()
    for i, word in enumerate(words):
        type_text(word)
        if i < len(words) - 1:
            time.sleep(0.3)
            press_key('space')

    time.sleep(3)
    press_key('Return')

    time.sleep(5)

    try:
        key = input().strip().lower()
        if key == 'd':
            if os.path.exists("pending_quotes.json"):
                os.remove("pending_quotes.json")
            app_process.terminate()
        else:
            subprocess.run(["xdotool", "key", "Shift+0"])
    except KeyboardInterrupt:
        app_process.terminate()

if __name__ == "__main__":
    main()
