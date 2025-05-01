#!/usr/bin/env python3
import curses
import json
import os
import time
import platform
import subprocess
import signal

# File paths for quote storage
QUOTES_FILE = "quotes.json"
PENDING_QUOTES_FILE = "pending_quotes.json"
REMOVED_QUOTES_FILE = "removed_quotes.json"

# Flag to control application exit
EXIT_APP = False

# Detect if we're running on a Raspberry Pi
IS_RASPBERRY_PI = platform.system() == "Linux" and os.path.exists("/sys/firmware/devicetree/base/model") and "raspberry pi" in open("/sys/firmware/devicetree/base/model").read().lower()

def signal_handler(sig, frame):
    # Ignore Ctrl+C (SIGINT) - do nothing when it's pressed
    pass

# Set up the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def load_quotes(file_path):
    """Load quotes from a JSON file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def save_quotes(quotes, file_path):
    """Save quotes to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(quotes, f, indent=2)

def admin_panel(stdscr, pending_quotes, approved_quotes, removed_quotes):
    """Run the admin panel interface for quote management."""
    global EXIT_APP
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking mode
    
    current_index = 0
    last_pending_count = len(pending_quotes)
    last_check_time = time.time()
    refresh_interval = 2.0  # Check for new quotes every 2 seconds
    notification_active = False
    notification_start_time = 0
    notification_duration = 2.0  # Show notification for 2 seconds
    
    while True:
        if EXIT_APP:
            break
            
        # Check for file changes periodically
        current_time = time.time()
        if current_time - last_check_time >= refresh_interval:
            # Reload all quotes to ensure we have the latest state
            new_pending_quotes = load_quotes(PENDING_QUOTES_FILE)
            new_approved_quotes = load_quotes(QUOTES_FILE)
            new_removed_quotes = load_quotes(REMOVED_QUOTES_FILE)
            
            # Filter out any pending quotes that have been processed in another instance
            filtered_pending = []
            for quote in new_pending_quotes:
                # Skip quotes that are already in approved or removed lists
                already_processed = False
                for existing in new_approved_quotes + new_removed_quotes:
                    if quote["name"] == existing["name"] and quote["quote"] == existing["quote"]:
                        already_processed = True
                        break
                
                if not already_processed:
                    filtered_pending.append(quote)
            
            # Check if there are changes to pending quotes
            if len(filtered_pending) != len(pending_quotes):
                pending_quotes = filtered_pending
                approved_quotes = new_approved_quotes
                removed_quotes = new_removed_quotes
                
                # Show notification if new quotes were added
                if len(filtered_pending) > last_pending_count:
                    notification_active = True
                    notification_start_time = current_time
                
                # If the current index is no longer valid, reset it
                if pending_quotes and current_index >= len(pending_quotes):
                    current_index = len(pending_quotes) - 1
                elif not pending_quotes:
                    current_index = 0
                
                # Save the filtered pending quotes back to file to maintain consistency
                save_quotes(filtered_pending, PENDING_QUOTES_FILE)
            
            last_pending_count = len(pending_quotes)
            last_check_time = current_time
        
        # Clear notification after the duration expires
        if notification_active and current_time - notification_start_time >= notification_duration:
            notification_active = False
            
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
        stdscr.addstr(counts_row, start_x, pending_count, curses.color_pair(1))
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
        instructions = "PUP: Approve | PDOWN: Remove | ESC: Exit"
        stdscr.addstr(height - 2, (width // 2) - (len(instructions) // 2), instructions, curses.color_pair(1))
        
        # Display notification if active
        if notification_active:
            notification_msg = "New quotes detected!"
            msg_x = (width // 2) - (len(notification_msg) // 2)
            
            # Draw a highlighted notification
            for i in range(len(notification_msg) + 4):
                stdscr.addch(5, msg_x - 2 + i, ' ', curses.color_pair(2))
            
            stdscr.addstr(5, msg_x, notification_msg, curses.color_pair(2) | curses.A_BOLD)
        
        stdscr.refresh()
        
        # Process keyboard input
        key = stdscr.getch()
        
        if key == 27:  # ESC key
            break
        elif key == curses.KEY_UP and pending_quotes:
            current_index = (current_index - 1) % len(pending_quotes)
        elif key == curses.KEY_DOWN and pending_quotes:
            current_index = (current_index + 1) % len(pending_quotes)
        elif key == curses.KEY_PPAGE  and pending_quotes:  # ENTER key
            # Approve quote - move to approved quotes
            approved_quotes.append(pending_quotes.pop(current_index))
            save_quotes(approved_quotes, QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            if current_index >= len(pending_quotes) and current_index > 0:
                current_index = len(pending_quotes) - 1
        elif (key == curses.KEY_NPAGE ) and pending_quotes:  # DELETE or BACKSPACE key
            # Reject quote - move to removed quotes
            removed_quotes.append(pending_quotes.pop(current_index))
            save_quotes(removed_quotes, REMOVED_QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            if current_index >= len(pending_quotes) and current_index > 0:
                current_index = len(pending_quotes) - 1
        elif check_exit_combination(key):  # Check for the exit combination (Shift+0)
            EXIT_APP = True
            break

        
def check_exit_combination(key):
    """Check if the key is the Shift+0 combination (ASCII 41 is ")") """
    return key == 41  # ASCII code for the ")" character (Shift+0)

def main(stdscr):
    """Main function to run the admin panel."""
    global EXIT_APP
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking getch

    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Main text
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Menu/Notification
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Border
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Admin panel title

    # Initialize key detection
    stdscr.keypad(True)  # Enable keypad mode for arrow keys

    # Load all quote types
    quotes = load_quotes(QUOTES_FILE)
    pending_quotes = load_quotes(PENDING_QUOTES_FILE)
    removed_quotes = load_quotes(REMOVED_QUOTES_FILE)
    
    # Ensure quotes file exists and has at least one quote
    if not quotes:
        quotes = [{"name": "System", "quote": "Welcome to the Retro Wall!"}]
        save_quotes(quotes, QUOTES_FILE)

    # Call admin panel directly
    admin_panel(stdscr, pending_quotes, quotes, removed_quotes)

    # Save all changes to files before exiting
    save_quotes(quotes, QUOTES_FILE)
    save_quotes(pending_quotes, PENDING_QUOTES_FILE)
    save_quotes(removed_quotes, REMOVED_QUOTES_FILE)

# No buzzer for this version
HAS_BUZZER = False

def cleanup():
    """Clean up resources before exiting"""
    pass  # No resources to clean up in this version

# Ensure all required files exist
def init_files():
    if not os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(PENDING_QUOTES_FILE):
        with open(PENDING_QUOTES_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(REMOVED_QUOTES_FILE):
        with open(REMOVED_QUOTES_FILE, 'w') as f:
            json.dump([], f)

if __name__ == "__main__":
    # Initialize files
    init_files()
    
    try:
        # Run the admin panel using curses
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
    
    print("Admin panel closed. Goodbye!")