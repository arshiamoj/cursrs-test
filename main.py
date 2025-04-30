import curses
import json
import os
import time
import pyfiglet
import random
import platform
import subprocess

QUOTES_FILE = "quotes.json"
PENDING_QUOTES_FILE = "pending_quotes.json"
REMOVED_QUOTES_FILE = "removed_quotes.json"

# Detect if we're running on a Raspberry Pi or another system
IS_RASPBERRY_PI = platform.system() == "Linux" and os.path.exists("/sys/firmware/devicetree/base/model") and "raspberry pi" in open("/sys/firmware/devicetree/base/model").read().lower()

# Only import gpiozero if we're on a Raspberry Pi
if IS_RASPBERRY_PI:
    try:
        from gpiozero import PWMOutputDevice
        buzzer = PWMOutputDevice(18)
        HAS_BUZZER = True
    except ImportError:
        HAS_BUZZER = False
else:
    HAS_BUZZER = False

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

def play_success_jingle():
    """Play a C major jingle when a quote is successfully added"""
    if HAS_BUZZER:
        # C Major mini jingle: C → E → G → C5
        notes = [261, 329, 392, 523]  # C4, E4, G4, C5
        
        for note in notes:
            # Play each note
            buzzer.frequency = note
            buzzer.value = 0.3
            time.sleep(0.15)
            buzzer.value = 0
            time.sleep(0.03)
    else:
        # Use system beep on other platforms
        if platform.system() == "Darwin":  # MacOS
            # Use afplay (built-in on MacOS) or print character bell
            subprocess.run(["osascript", "-e", "beep"])
        elif platform.system() == "Windows":
            # Windows - use winsound if available
            try:
                import winsound
                for freq in [261, 329, 392, 523]:  # C4, E4, G4, C5
                    winsound.Beep(freq, 150)  # Each note for 150ms
                    time.sleep(0.03)
            except ImportError:
                # Fallback to ASCII bell
                print("\a", end="", flush=True)
        else:
            # Linux/Unix without GPIO - use ASCII bell
            print("\a", end="", flush=True)

def play_beep():
    """Play a beep sound using either GPIO buzzer or system beep"""
    if HAS_BUZZER:
        # Use the GPIO buzzer on Raspberry Pi
        buzzer.frequency = 250  # Set frequency to 250Hz
        buzzer.value = 0.2      # Set duty cycle to 20%
        time.sleep(0.2)         # Play for 0.2 seconds
        buzzer.value = 0        # Stop the sound
    else:
        # Use system beep on other platforms
        if platform.system() == "Darwin":  # MacOS
            # Use afplay (built-in on MacOS) or print character bell
            subprocess.run(["osascript", "-e", "beep"])
        elif platform.system() == "Windows":
            # Windows - use winsound if available
            try:
                import winsound
                winsound.Beep(250, 200)  # 250Hz for 200ms
            except ImportError:
                # Fallback to ASCII bell
                print("\a", end="", flush=True)
        else:
            # Linux/Unix without GPIO - use ASCII bell
            print("\a", end="", flush=True)

def add_quote(stdscr, pending_quotes):
    curses.echo()
    curses.curs_set(1)  # Show blinking cursor
    stdscr.timeout(-1)  # Wait indefinitely for input

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Center the prompt for the name input
    prompt_name = "What's your name?"
    name_x_center = (width // 2) - (len(prompt_name) // 2)
    stdscr.addstr(height // 2 - 4, name_x_center, prompt_name, curses.A_BOLD)
    stdscr.refresh()
    name = stdscr.getstr(height // 2 - 2, name_x_center, 22).decode('utf-8').strip()  # Limit to 20 characters
    play_beep()  # Beep after name is entered

    stdscr.clear()

    # Center the prompt for the quote input with character limit message
    prompt_quote = "Say something:"
    quote_x_center = (width // 2) - (len(prompt_quote) // 2)
    stdscr.addstr(height // 2 - 4, quote_x_center, prompt_quote, curses.A_BOLD)
    stdscr.refresh()
    quote_text = stdscr.getstr(height // 2 - 2, quote_x_center, 30).decode('utf-8').strip()  # Limit to 32 characters
    
    curses.noecho()
    curses.curs_set(0)  # Hide cursor again
    stdscr.timeout(100)  # Return to non-blocking mode

    if name and quote_text:
        new_quote = {"name": name, "quote": quote_text}
        pending_quotes.append(new_quote)
        save_quotes(pending_quotes, PENDING_QUOTES_FILE)
        play_success_jingle()  # Play success jingle after quote is added
        return new_quote  # Return the newly added quote
    return None

def admin_panel(stdscr, pending_quotes, approved_quotes, removed_quotes):
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking mode
    
    current_index = 0
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = "ADMIN PANEL - PENDING QUOTES"
        stdscr.addstr(1, (width // 2) - (len(title) // 2), title, curses.A_BOLD | curses.color_pair(4))
        
        # Show quotes counts
        pending_count = f"Pending: {len(pending_quotes)}"
        approved_count = f"Approved: {len(approved_quotes)}"
        removed_count = f"Removed: {len(removed_quotes)}"
        total_count = f"Total: {len(pending_quotes) + len(approved_quotes) + len(removed_quotes)}"
        
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
        
        # Display total count centered on the next row
        total_row = counts_row + 2
        stdscr.addstr(total_row, (width // 2) - (len(total_count) // 2), total_count, curses.A_BOLD | curses.color_pair(1))
        
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
        instructions = "ENTER: Approve | DEL: Remove | ESC: Exit"
        stdscr.addstr(height - 2, (width // 2) - (len(instructions) // 2), instructions, curses.color_pair(1))
        
        stdscr.refresh()
        
        # Process keyboard input
        key = stdscr.getch()
        
        if key == 27:  # ESC key
            break
        elif key == curses.KEY_UP and pending_quotes:
            current_index = (current_index - 1) % len(pending_quotes)
            # Removed beep for admin panel navigation
        elif key == curses.KEY_DOWN and pending_quotes:
            current_index = (current_index + 1) % len(pending_quotes)
            # Removed beep for admin panel navigation
        elif key == 10 and pending_quotes:  # ENTER key
            # Approve quote - move to approved quotes
            approved_quotes.append(pending_quotes.pop(current_index))
            save_quotes(approved_quotes, QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            # Removed beep for quote approval
            if current_index >= len(pending_quotes) and current_index > 0:
                current_index = len(pending_quotes) - 1
        elif (key == curses.KEY_DC or key == 127 or key == 8) and pending_quotes:  # DELETE or BACKSPACE key
            # Reject quote - move to removed quotes
            removed_quotes.append(pending_quotes.pop(current_index))
            save_quotes(removed_quotes, REMOVED_QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            # Removed beep for quote rejection
            if current_index >= len(pending_quotes) and current_index > 0:
                current_index = len(pending_quotes) - 1

def typewriter_effect(stdscr, y, text, color_pair, center_x):
    for i, ch in enumerate(text):
        stdscr.addstr(y, center_x + i, ch, color_pair | curses.A_BOLD)
        stdscr.refresh()
        time.sleep(0.03)

def draw_menu(stdscr, width, height):
    footer = "Press any key to add a quote"
    # Make "Press any key..." bold, no blink.
    blink_attr = curses.color_pair(2) | curses.A_BOLD
    stdscr.addstr(height - 3, (width // 2) - (len(footer) // 2), footer, blink_attr)
    # Add copyright notice
    copyright_text = "© Retro Mowz"
    stdscr.addstr(height - 1, (width // 2) - (len(copyright_text) // 2), copyright_text, curses.color_pair(1))

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking getch

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Main text
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Menu
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Border
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Admin panel title

    # Initialize key detection
    stdscr.keypad(True)  # Enable keypad mode for arrow keys

    # Load all quote types
    quotes = load_quotes(QUOTES_FILE)
    pending_quotes = load_quotes(PENDING_QUOTES_FILE)
    removed_quotes = load_quotes(REMOVED_QUOTES_FILE)
    
    if not quotes:
        quotes = [{"name": "System", "quote": "Welcome to the Retro Wall!"}]

    ascii_title = pyfiglet.figlet_format("Retro Wall", font="small")  # Using the "small" font
    ascii_title_lines = ascii_title.splitlines()

    displayed_indices = []
    current_quote = None

    vertical_space_before_title = 2  # Number of empty lines before the title

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Draw ASCII Title (with added space)
        for i, line in enumerate(ascii_title_lines):
            title_y = i + vertical_space_before_title
            if title_y >= height - 4:  # Leave space for border
                break
            stdscr.addstr(title_y, (width // 2) - (len(line) // 2), line, curses.color_pair(1) | curses.A_BOLD)

        # Calculate border position based on the new title position
        border_top_y = len(ascii_title_lines) + vertical_space_before_title + 1  # Adjusted for space

        # Draw the thicker border
        for x in range(2, width - 2):  # Top and bottom horizontal border
            stdscr.addch(border_top_y, x, curses.ACS_HLINE, curses.color_pair(3))  # Top border
            stdscr.addch(height - 4, x, curses.ACS_HLINE, curses.color_pair(3))  # Bottom border

        # Vertical borders (thicker)
        for y in range(border_top_y, height - 3):  # Left and right vertical borders
            stdscr.addch(y, 2, curses.ACS_VLINE, curses.color_pair(3))  # Left border
            stdscr.addch(y, width - 3, curses.ACS_VLINE, curses.color_pair(3))  # Right border

        # Corners (to complete the thick border)
        stdscr.addch(border_top_y, 2, curses.ACS_ULCORNER, curses.color_pair(3))
        stdscr.addch(border_top_y, width-3, curses.ACS_URCORNER, curses.color_pair(3))
        stdscr.addch(height-4, 2, curses.ACS_LLCORNER, curses.color_pair(3))
        stdscr.addch(height-4, width-3, curses.ACS_LRCORNER, curses.color_pair(3))

        # Draw Menu (always visible)
        draw_menu(stdscr, width, height)

        if not quotes:
            current_quote = {"name": "System", "quote": "No quotes available. Add some!"}
        elif current_quote is None:
            available_indices = [i for i in range(len(quotes)) if i not in displayed_indices]
            if not available_indices:
                displayed_indices = []
                available_indices = list(range(len(quotes)))
            if available_indices:
                chosen_index = random.choice(available_indices)
                current_quote = quotes[chosen_index]
                displayed_indices.append(chosen_index)

        if current_quote:
            # Centering the content vertically between the ASCII art and the border
            ascii_end_y = border_top_y
            menu_start_y = height - 3
            available_space = menu_start_y - ascii_end_y
            center_y = ascii_end_y + (available_space // 2)

            quote_y = center_y - 1
            name_y = center_y + 1

            # Center X positions
            quote_x_center = (width // 2) - (len(current_quote["quote"]) // 2)
            name_line = f"- {current_quote['name']} -"
            name_x_center = (width // 2) - (len(name_line) // 2)

            # Typing effect for quote
            typewriter_effect(stdscr, quote_y, current_quote["quote"], curses.color_pair(1), quote_x_center)

            # After typing, draw name normally
            stdscr.addstr(name_y, name_x_center, name_line, curses.color_pair(1) | curses.A_BOLD)

        stdscr.refresh()

        # Wait 5 seconds while listening for keys
        start_time = time.time()
        newly_added_quote = None
        while time.time() - start_time < 5:
            key = stdscr.getch()
            if key == 16:  # CTRL+P (ASCII 16 is DLE, which is what CTRL+P sends)
                # No beep when entering admin panel
                admin_panel(stdscr, pending_quotes, quotes, removed_quotes)
                current_quote = None  # Reset to show a random quote after admin panel
                break
            elif key != curses.ERR:  # Check if any other key was pressed
                play_beep()
                newly_added_quote = add_quote(stdscr, pending_quotes)
                if newly_added_quote:
                    current_quote = newly_added_quote
                    displayed_indices = []
                break
            time.sleep(0.1)

        if newly_added_quote is None and key != 16:  # Only reset if we didn't open the admin panel
            current_quote = None

def cleanup():
    """Clean up resources before exiting"""
    if HAS_BUZZER:
        buzzer.value = 0

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

try:
    curses.wrapper(main)
finally:
    cleanup()  # Make sure buzzer is turned off when the program exits