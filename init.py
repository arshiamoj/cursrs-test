import curses
import subprocess
import os

def main(stdscr):
    # Clear screen
    stdscr.clear()
    stdscr.refresh()

    # Wait for user input (any key)
    stdscr.getch()

    # Run boot.py in the same directory
    boot_path = os.path.join(os.path.dirname(__file__), "boot.py")
    subprocess.run(["python3", boot_path])

# Start the curses application
curses.wrapper(main)
