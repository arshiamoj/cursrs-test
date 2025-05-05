#!/usr/bin/env python3
import curses
import time
import pyfiglet
import random
import os
import sys
import subprocess

def blink_text(stdscr, y, text, color_pair, center_x, times=1, on_time=0.3, off_time=0.2):
    """Display text with a blinking effect"""
    for _ in range(times):
        # Display text
        stdscr.addstr(y, center_x, text, color_pair | curses.A_BOLD)
        stdscr.refresh()
        time.sleep(on_time)
        
        # Clear text
        stdscr.addstr(y, center_x, " " * len(text))
        stdscr.refresh()
        time.sleep(off_time)
    
    # Make sure text is visible at the end
    stdscr.addstr(y, center_x, text, color_pair | curses.A_BOLD)
    stdscr.refresh()

def loading_animation(stdscr, y, width, color_pair, duration=2.0):
    """Display a simple loading bar animation"""
    bar_width = 40
    start_x = (width // 2) - (bar_width // 2)
    
    # Draw empty bar outline
    stdscr.addstr(y, start_x - 1, "[", color_pair)
    stdscr.addstr(y, start_x + bar_width, "]", color_pair)
    stdscr.refresh()
    
    # Fill the bar gradually
    steps = 20
    step_size = bar_width / steps
    step_time = duration / steps
    
    for i in range(steps + 1):
        fill_width = int(i * step_size)
        stdscr.addstr(y, start_x, "#" * fill_width + " " * (bar_width - fill_width), color_pair)
        stdscr.refresh()
        time.sleep(step_time)

def boot_sequence(stdscr):
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking getch
    
    # Colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Matrix-style green text
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Amber for status
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White for title
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Red for errors/warnings
    
    height, width = stdscr.getmaxyx()
    
    # Boot sequence
    stdscr.clear()
    
    # 3 seconds of black screen before showing the title
    time.sleep(3.0)
    
    # Display title with figlet
    ascii_title = pyfiglet.figlet_format("Retro Wall", font="small")
    ascii_title_lines = ascii_title.splitlines()
    
    # Display ASCII title with single blink-in effect
    title_start_y = (height // 2) - (len(ascii_title_lines) // 2) - 5
    
    # Display the title directly (blink in once from black)
    for i, line in enumerate(ascii_title_lines):
        center_x = (width // 2) - (len(line) // 2)
        stdscr.addstr(title_start_y + i, center_x, line, curses.color_pair(3) | curses.A_BOLD)
    
    stdscr.refresh()
    
    # Wait 1 second after showing Retro Wall before continuing
    time.sleep(1.0)
    
    # Display version - directly below the title with no gap
    version_text = "v1.0"
    version_y = title_start_y + len(ascii_title_lines)
    stdscr.addstr(version_y, (width // 2) - (len(version_text) // 2), version_text, curses.color_pair(2))
    stdscr.refresh()
    time.sleep(0.2)
    
    # Show system initialization text
    init_y = version_y + 2
    init_text = "System Initializing..."
    stdscr.addstr(init_y, (width // 2) - (len(init_text) // 2), init_text, curses.color_pair(1))
    stdscr.refresh()
    time.sleep(0.2)
    
    # Display loading bar (slower)
    loading_animation(stdscr, init_y + 2, width, curses.color_pair(1), 2.0)
    
    # Display only one system component loading
    components = [
        "Loading system modules"
    ]
    
    comp_y = init_y + 4
    for i, component in enumerate(components):
        comp_text = f"{component}... "
        stdscr.addstr(comp_y + i, (width // 2) - 20, comp_text, curses.color_pair(1))
        stdscr.refresh()
        time.sleep(0.5)
        stdscr.addstr(comp_y + i, (width // 2) - 20 + len(comp_text), "OK", curses.color_pair(2))
        stdscr.refresh()
    
    # Finalize boot sequence
    time.sleep(0.3)
    ready_y = comp_y + len(components) + 2
    ready_text = "SYSTEM READY"
    
    # Make SYSTEM READY blink 3 times
    blink_text(
        stdscr, 
        ready_y, 
        ready_text, 
        curses.color_pair(2), 
        (width // 2) - (len(ready_text) // 2),
        times=3,
        on_time=0.3, 
        off_time=0.2
    )
    
    # Short pause before closing
    time.sleep(0.3)
    
    # Closing boot splash
    stdscr.clear()
    closing_text = "Starting application..."
    stdscr.addstr(height // 2, (width // 2) - (len(closing_text) // 2), closing_text, curses.color_pair(3))
    stdscr.refresh()
    time.sleep(0.3)

if __name__ == "__main__":
    # Run the boot sequence
    curses.wrapper(boot_sequence)
    
    # After boot sequence, launch the main application
    try:
        # Path to the main script
        main_script = "./main.py"
        
        # Check if the script exists
        if os.path.exists(main_script):
            subprocess.run(["python3", main_script])
        else:
            print(f"Error: Main application script '{main_script}' not found.")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to start main application: {e}")
        sys.exit(1)