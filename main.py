import curses
import json
import os
import time
import pyfiglet
import random

QUOTES_FILE = "quotes.json"
UNAPPROVED_FILE = "unapproved_quotes.json"
REMOVED_FILE = "removed_quotes.json"

def load_quotes():
    if os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def load_unapproved_quotes():
    if os.path.exists(UNAPPROVED_FILE):
        with open(UNAPPROVED_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def load_removed_quotes():
    if os.path.exists(REMOVED_FILE):
        with open(REMOVED_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def save_quotes(quotes):
    with open(QUOTES_FILE, 'w') as f:
        json.dump(quotes, f, indent=2)

def save_unapproved_quotes(quotes):
    with open(UNAPPROVED_FILE, 'w') as f:
        json.dump(quotes, f, indent=2)

def save_removed_quotes(quotes):
    with open(REMOVED_FILE, 'w') as f:
        json.dump(quotes, f, indent=2)

def play_beep():
    sound_file = "/home/mojtaba/cursrs-test/beep.wav"  # Replace with the actual path to your sound file
    os.system(f"aplay -q {sound_file} &")  # -q for quiet, & to run in background

def add_quote(stdscr, unapproved_quotes):
    curses.echo()
    curses.curs_set(1)  # Show blinking cursor
    stdscr.timeout(-1)  # Wait indefinitely for input

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Center the prompt for the name input
    prompt_name = "Whats your name?"
    name_x_center = (width // 2) - (len(prompt_name) // 2)
    stdscr.addstr(height // 2 - 4, name_x_center, prompt_name, curses.A_BOLD)
    stdscr.refresh()
    name = stdscr.getstr(height // 2 - 2, name_x_center, 100).decode('utf-8').strip()
    play_beep()  # Beep after name is entered

    stdscr.clear()

    # Center the prompt for the quote input
    prompt_quote = "Say something:"
    quote_x_center = (width // 2) - (len(prompt_quote) // 2)
    stdscr.addstr(height // 2 - 4, quote_x_center, prompt_quote, curses.A_BOLD)
    stdscr.refresh()
    quote_text = stdscr.getstr(height // 2 - 2, quote_x_center, 100).decode('utf-8').strip()
    play_beep()  # Beep after quote is entered

    curses.noecho()
    curses.curs_set(0)  # Hide cursor again
    stdscr.timeout(100)  # Return to non-blocking mode

    if name and quote_text:
        new_quote = {"name": name, "quote": quote_text, "approved": False}
        unapproved_quotes.append(new_quote)
        save_unapproved_quotes(unapproved_quotes)
        return new_quote  # Return the newly added quote
    return None

def admin_menu(stdscr, unapproved_quotes, removed_quotes):
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking getch

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    stdscr.addstr(2, (width // 2) - 7, "Admin Panel", curses.A_BOLD)
    stdscr.addstr(4, 2, "Unapproved Quotes:", curses.A_BOLD)

    # Display unapproved quotes
    if unapproved_quotes:
        for idx, quote in enumerate(unapproved_quotes):
            stdscr.addstr(6 + idx, 2, f"{idx + 1}. {quote['name']}: {quote['quote']}", curses.color_pair(1))

    stdscr.addstr(height - 3, (width // 2) - 15, "Press ENTER to approve or D to delete", curses.A_BOLD)
    stdscr.refresh()

    key = stdscr.getch()
    if key == 10:  # ENTER key
        # Select quote to approve
        quote_index = len(unapproved_quotes) - 1
        selected_quote = unapproved_quotes.pop(quote_index)
        selected_quote["approved"] = True
        # Add to approved quotes
        quotes = load_quotes()
        quotes.append(selected_quote)
        save_quotes(quotes)
        save_unapproved_quotes(unapproved_quotes)
    elif key == ord('d'):  # D key for delete
        # Select quote to delete
        quote_index = len(unapproved_quotes) - 1
        selected_quote = unapproved_quotes.pop(quote_index)
        removed_quotes.append(selected_quote)
        save_removed_quotes(removed_quotes)
        save_unapproved_quotes(unapproved_quotes)

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

    quotes = load_quotes()
    unapproved_quotes = load_unapproved_quotes()
    removed_quotes = load_removed_quotes()

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

        # Wait for user key input to add quote or show admin menu
        start_time = time.time()
        while time.time() - start_time < 5:
            key = stdscr.getch()
            if key != curses.ERR:  # Check if a key was pressed
                play_beep()
                if key == 17:  # Ctrl + P
                    admin_menu(stdscr, unapproved_quotes, removed_quotes)
                else:
                    newly_added_quote = add_quote(stdscr, unapproved_quotes)
                    if newly_added_quote:
                        current_quote = newly_added_quote
                        displayed_indices = []
                break

curses.wrapper(main)
