#!/usr/bin/env python3
import time
import subprocess
import sys
import random
import os
from pynput.keyboard import Key, Controller
from pynput import keyboard as kb

def main():
    # Start the Retro Wall application
    try:
        app_process = subprocess.Popen(["python3", "main.py"])
    except Exception as e:
        print(f"Failed to launch app: {e}")
        sys.exit(1)
    
    keyboard_controller = Controller()
    
    # Wait for the application to load
    time.sleep(2)
    
    # Wait on the main screen
    time.sleep(6)
    
    # Press any key to start adding a quote
    keyboard_controller.press('a')
    keyboard_controller.release('a')
    
    # Wait for the "What's your name?" prompt
    time.sleep(1.5)

    # Additional delay before typing the name
    time.sleep(2.0)
    
    name = "Hamlet"
    for char in name:
        time.sleep(random.uniform(0.1, 0.4))
        keyboard_controller.press(char)
        keyboard_controller.release(char)
        if random.random() < 0.2:
            time.sleep(random.uniform(0.2, 0.5))
    
    # Wait before pressing Enter
    time.sleep(3.0)
    keyboard_controller.press(Key.enter)
    keyboard_controller.release(Key.enter)
    
    # Wait for the "Say something:" prompt
    time.sleep(1.5)

    # Additional delay before typing the quote
    time.sleep(3.0)
    
    quote = "To be, or not to be"
    words = quote.split()
    for i, word in enumerate(words):
        for char in word:
            time.sleep(random.uniform(0.1, 0.35))
            keyboard_controller.press(char)
            keyboard_controller.release(char)
        
        if i < len(words) - 1:
            if word.endswith(','):
                time.sleep(random.uniform(0.4, 0.7))
            else:
                time.sleep(random.uniform(0.2, 0.4))
            keyboard_controller.press(Key.space)
            keyboard_controller.release(Key.space)
    
    # Wait before pressing Enter
    time.sleep(3.0)
    keyboard_controller.press(Key.enter)
    keyboard_controller.release(Key.enter)
    
    # Wait to view the success
    time.sleep(5)

    # Prompt the user for final action

    def on_press(key):
        try:
            if key.char == 'd':
                # Delete the file if it exists
                if os.path.exists("pending_quotes.json"):
                    os.remove("pending_quotes.json")
                else:
                    print("File pending_quotes.json does not exist.")
                
                # Terminate the app process
                app_process.terminate()
            else:
                # Simulate Shift + 0
                keyboard_controller.press(Key.shift)
                keyboard_controller.press('0')
                keyboard_controller.release('0')
                keyboard_controller.release(Key.shift)
        except AttributeError:
            # For special keys (e.g., arrows), also simulate Shift+0
            keyboard_controller.press(Key.shift)
            keyboard_controller.press('0')
            keyboard_controller.release('0')
            keyboard_controller.release(Key.shift)
        return False  # Stop listener after one key press

    with kb.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
