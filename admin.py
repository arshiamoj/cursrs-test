#!/usr/bin/env python3
import curses
import json
import os
import time
import signal
import platform

QUOTES_FILE = "quotes.json"
PENDING_QUOTES_FILE = "pending_quotes.json"
REMOVED_QUOTES_FILE = "removed_quotes.json"

# Flag to control application exit
EXIT_APP = False

def signal_handler(sig, frame):
    # Ignore Ctrl+C (SIGINT) - do nothing when it's pressed
    pass

# Set up the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def load_quotes(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def save_quotes(quotes, file_path):
    with open(file_path, 'w') as f:
        json.dump(quotes, f, indent=2)

def check_exit_combination(key):
    """Check if the key is the Shift+0 combination (ASCII 41 is ")") """
    return key == 41  # ASCII code for the ")" character (Shift+0)

def admin_panel(stdscr):
    global EXIT_APP
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking mode
    
    current_index = 0
    
    # Initialize color pairs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Main text
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Menu
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Approved/Border
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Removed/Title
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Pending
    
    # Last refresh time
    last_refresh = time.time()
    refresh_interval = 2  # Refresh every 2 seconds
    
    while True:
        if EXIT_APP:
            break
            
        # Check if it's time to reload the quotes
        current_time = time.time()
        if current_time - last_refresh >= refresh_interval:
            # Reload all quotes
            pending_quotes = load_quotes(PENDING_QUOTES_FILE)
            approved_quotes = load_quotes(QUOTES_FILE)
            removed_quotes = load_quotes(REMOVED_QUOTES_FILE)
            
            # Make sure current_index is still valid after reloading
            if pending_quotes and current_index >= len(pending_quotes):
                current_index = len(pending_quotes) - 1
                
            last_refresh = current_time
        else:
            # Load quotes normally
            pending_quotes = load_quotes(PENDING_QUOTES_FILE)
            approved_quotes = load_quotes(QUOTES_FILE)
            removed_quotes = load_quotes(REMOVED_QUOTES_FILE)
        
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = "ADMIN PANEL - PENDING QUOTES"
        stdscr.addstr(1, (width // 2) - (len(title) // 2), title, curses.A_BOLD | curses.color_pair(4))
        
        # Show quotes counts
        pending_count = f"Pending: {len(pending_quotes)}"
        approved_count = f"Approved: {len(approved_quotes)}"
        removed_count = f"Removed: {len(removed_quotes)}"
        
        # Display counts on row 3
        counts_row = 3
        padding = 4  # Space between counts
        
        # Calculate the total width needed for the three main counts
        three_counts_width = len(pending_count) + len(approved_count) + len(removed_count) + (padding * 2)
        start_x = (width // 2) - (three_counts_width // 2)
        
        # Display each count with appropriate color
        stdscr.addstr(counts_row, start_x, pending_count, curses.color_pair(5))
        start_x += len(pending_count) + padding
        
        stdscr.addstr(counts_row, start_x, approved_count, curses.color_pair(3))
        start_x += len(approved_count) + padding
        
        stdscr.addstr(counts_row, start_x, removed_count, curses.color_pair(4))
        
        # No pending quotes
        if not pending_quotes:
            no_quotes_msg = "No pending quotes available"
            stdscr.addstr(height // 2, (width // 2) - (len(no_quotes_msg) // 2), no_quotes_msg, curses.color_pair(1))
        else:
            # Display current quote
            quote = pending_quotes[current_index]
            
            # Draw quote in a box
            box_width = min(width - 10, max(len(quote["quote"]), len(quote["name"])) + 10)
            box_start_x = (width // 2) - (box_width // 2)
            box_start_y = height // 2 - 4
            
            # Draw border
            for i in range(box_width):
                stdscr.addch(box_start_y, box_start_x + i, curses.ACS_HLINE, curses.color_pair(3))
                stdscr.addch(box_start_y + 6, box_start_x + i, curses.ACS_HLINE, curses.color_pair(3))
            
            for i in range(7):
                stdscr.addch(box_start_y + i, box_start_x, curses.ACS_VLINE, curses.color_pair(3))
                stdscr.addch(box_start_y + i, box_start_x + box_width - 1, curses.ACS_VLINE, curses.color_pair(3))
            
            # Corners
            stdscr.addch(box_start_y, box_start_x, curses.ACS_ULCORNER, curses.color_pair(3))
            stdscr.addch(box_start_y, box_start_x + box_width - 1, curses.ACS_URCORNER, curses.color_pair(3))
            stdscr.addch(box_start_y + 6, box_start_x, curses.ACS_LLCORNER, curses.color_pair(3))
            stdscr.addch(box_start_y + 6, box_start_x + box_width - 1, curses.ACS_LRCORNER, curses.color_pair(3))
            
            # Quote content
            quote_str = quote["quote"]
            if len(quote_str) > box_width - 6:
                quote_str = quote_str[:box_width - 9] + "..."
            
            name_str = f"- {quote['name']} -"
            
            # Display quote and name
            stdscr.addstr(box_start_y + 2, (width // 2) - (len(quote_str) // 2), quote_str, curses.color_pair(1))
            stdscr.addstr(box_start_y + 4, (width // 2) - (len(name_str) // 2), name_str, curses.color_pair(1))
            
            # Show navigation indicator
            if len(pending_quotes) > 1:
                nav_text = f"Quote {current_index + 1} of {len(pending_quotes)}"
                stdscr.addstr(box_start_y + 8, (width // 2) - (len(nav_text) // 2), nav_text, curses.color_pair(1))
        
        # Add instructions at the bottom
        instructions = "PAGE UP: Approve | PAGE DOWN: Remove | ESC: Exit"
        stdscr.addstr(height - 2, (width // 2) - (len(instructions) // 2), instructions, curses.color_pair(1))
        
        # Show auto-refresh info
        refresh_info = f"Auto-refreshing every {refresh_interval} seconds"
        stdscr.addstr(height - 1, (width // 2) - (len(refresh_info) // 2), refresh_info, curses.color_pair(2))
        
        stdscr.refresh()
        
        # Process keyboard input
        key = stdscr.getch()
        
        if key == 27:  # ESC key
            break
        elif key == curses.KEY_UP and pending_quotes:
            current_index = (current_index - 1) % len(pending_quotes)
        elif key == curses.KEY_DOWN and pending_quotes:
            current_index = (current_index + 1) % len(pending_quotes)
        elif key == curses.KEY_PPAGE and pending_quotes:  # PAGE UP key - approve
            # Approve quote - move to approved quotes
            approved_quotes.append(pending_quotes.pop(current_index))
            save_quotes(approved_quotes, QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            
            if current_index >= len(pending_quotes) and current_index > 0:
                current_index = len(pending_quotes) - 1
        elif key == curses.KEY_NPAGE and pending_quotes:  # PAGE DOWN key - remove
            # Reject quote - move to removed quotes
            removed_quotes.append(pending_quotes.pop(current_index))
            save_quotes(removed_quotes, REMOVED_QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            
            if current_index >= len(pending_quotes) and current_index > 0:
                current_index = len(pending_quotes) - 1
        elif check_exit_combination(key):  # Check for the exit combination (Shift+0)
            EXIT_APP = True
            break

def main():
    # Ensure all required files exist
    if not os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(PENDING_QUOTES_FILE):
        with open(PENDING_QUOTES_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(REMOVED_QUOTES_FILE):
        with open(REMOVED_QUOTES_FILE, 'w') as f:
            json.dump([], f)
    
    # Run the admin panel
    curses.wrapper(admin_panel)

if __name__ == "__main__":
    main()