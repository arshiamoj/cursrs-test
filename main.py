import curses
import json
import os
import time
import pyfiglet
import random

APPROVED_QUOTES_FILE = "approved_quotes.json"
PENDING_QUOTES_FILE = "pending_quotes.json"
DELETED_QUOTES_FILE = "deleted_quotes.json"

def load_quotes(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def save_quotes(quotes, file):
    with open(file, 'w') as f:
        json.dump(quotes, f, indent=2)

def add_quote(stdscr, approved_quotes, pending_quotes):
    curses.echo()
    curses.curs_set(1)
    stdscr.timeout(-1)

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    prompt_name = "Enter the name of the person:"
    name_x_center = (width // 2) - (len(prompt_name) // 2)
    stdscr.addstr(height // 2 - 4, name_x_center, prompt_name, curses.A_BOLD)
    stdscr.refresh()
    name = stdscr.getstr(height // 2 - 2, name_x_center, 100).decode('utf-8').strip()

    stdscr.clear()

    prompt_quote = "Type the quote:"
    quote_x_center = (width // 2) - (len(prompt_quote) // 2)
    stdscr.addstr(height // 2 - 4, quote_x_center, prompt_quote, curses.A_BOLD)
    stdscr.refresh()
    quote_text = stdscr.getstr(height // 2 - 2, quote_x_center, 100).decode('utf-8').strip()

    curses.noecho()
    curses.curs_set(0)
    stdscr.timeout(100)

    if name and quote_text:
        new_quote = {"name": name, "quote": quote_text}
        pending_quotes.append(new_quote)
        save_quotes(pending_quotes, PENDING_QUOTES_FILE)
        return new_quote
    return None

def typewriter_effect(stdscr, y, text, color_pair, center_x):
    for i, ch in enumerate(text):
        stdscr.addstr(y, center_x + i, ch, color_pair | curses.A_BOLD)
        stdscr.refresh()
        time.sleep(0.03)

def admin_menu(stdscr, pending_quotes, approved_quotes):
    idx = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "ADMIN PANEL - PENDING QUOTES"
        stdscr.addstr(1, (width // 2) - (len(title) // 2), title, curses.color_pair(1) | curses.A_BOLD)

        if not pending_quotes:
            stdscr.addstr(height // 2, (width // 2) - 10, "No pending quotes!", curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()
            return

        for i, quote in enumerate(pending_quotes):
            marker = "-> " if i == idx else "   "
            text = f"{marker}{quote['quote']} - {quote['name']}"
            stdscr.addstr(3 + i, 4, text[:width-8], curses.color_pair(1))

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            idx = (idx - 1) % len(pending_quotes)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(pending_quotes)
        elif key == 10:  # Enter
            approved_quotes.append(pending_quotes.pop(idx))
            save_quotes(approved_quotes, APPROVED_QUOTES_FILE)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            if idx >= len(pending_quotes):
                idx = max(0, len(pending_quotes) - 1)
        elif key in (curses.KEY_DC, curses.KEY_BACKSPACE, 127):  # Delete
            pending_quotes.pop(idx)
            save_quotes(pending_quotes, PENDING_QUOTES_FILE)
            if idx >= len(pending_quotes):
                idx = max(0, len(pending_quotes) - 1)
        elif key in (27, ord('q'), ord('Q')):  # ESC or q to quit admin
            return

def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(100)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    approved_quotes = load_quotes(APPROVED_QUOTES_FILE)
    pending_quotes = load_quotes(PENDING_QUOTES_FILE)

    if not approved_quotes:
        approved_quotes = [{"name": "System", "quote": "Welcome to the Retro Terminal!"}]

    ascii_title = pyfiglet.figlet_format("Retro Terminal")
    ascii_title_lines = ascii_title.splitlines()

    displayed_indices = []
    current_quote = None

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        padding = 3  # Padding before the ASCII art
        for i in range(padding):
            stdscr.addstr(i, 0, '\n')

        for i, line in enumerate(ascii_title_lines):
            if i >= height - padding - 4:
                break
            stdscr.addstr(padding + i, (width // 2) - (len(line) // 2), line, curses.color_pair(1) | curses.A_BOLD)

        border_top_y = padding + len(ascii_title_lines) + 2

        for x in range(2, width - 2):
            stdscr.addch(border_top_y, x, curses.ACS_HLINE, curses.color_pair(3))
            stdscr.addch(height - 4, x, curses.ACS_HLINE, curses.color_pair(3))

        for y in range(border_top_y, height - 3):
            stdscr.addch(y, 2, curses.ACS_VLINE, curses.color_pair(3))
            stdscr.addch(y, width - 3, curses.ACS_VLINE, curses.color_pair(3))

        stdscr.addch(border_top_y, 2, curses.ACS_ULCORNER, curses.color_pair(3))
        stdscr.addch(border_top_y, width-3, curses.ACS_URCORNER, curses.color_pair(3))
        stdscr.addch(height-4, 2, curses.ACS_LLCORNER, curses.color_pair(3))
        stdscr.addch(height-4, width-3, curses.ACS_LRCORNER, curses.color_pair(3))

        # Removed the menu bar and added the "PRESS ANY KEY TO ADD A QUOTE."
        stdscr.addstr(height - 3, (width // 2) - (len("PRESS ANY KEY TO ADD A QUOTE.") // 2), "PRESS ANY KEY TO ADD A QUOTE.", curses.color_pair(2) | curses.A_BOLD)

        copyright_text = "© Retro Mowz"
        stdscr.addstr(height - 1, (width // 2) - (len(copyright_text) // 2), copyright_text, curses.color_pair(1))

        if not approved_quotes:
            current_quote = {"name": "System", "quote": "No approved quotes available!"}
        elif current_quote is None:
            available_indices = [i for i in range(len(approved_quotes)) if i not in displayed_indices]
            if not available_indices:
                displayed_indices = []
                available_indices = list(range(len(approved_quotes)))
            if available_indices:
                chosen_index = random.choice(available_indices)
                current_quote = approved_quotes[chosen_index]
                displayed_indices.append(chosen_index)

        if current_quote:
            ascii_end_y = border_top_y
            menu_start_y = height - 3
            available_space = menu_start_y - ascii_end_y
            center_y = ascii_end_y + (available_space // 2)

            quote_y = center_y - 1
            name_y = center_y + 1

            quote_x_center = (width // 2) - (len(current_quote["quote"]) // 2)
            name_line = f"- {current_quote['name']} -"
            name_x_center = (width // 2) - (len(name_line) // 2)

            typewriter_effect(stdscr, quote_y, current_quote["quote"], curses.color_pair(1), quote_x_center)
            stdscr.addstr(name_y, name_x_center, name_line, curses.color_pair(1) | curses.A_BOLD)

        stdscr.refresh()

        start_time = time.time()
        newly_added_quote = None
        while time.time() - start_time < 5:
            key = stdscr.getch()
            if key in (ord('a'), ord('A')):
                newly_added_quote = add_quote(stdscr, approved_quotes, pending_quotes)
                if newly_added_quote:
                    current_quote = newly_added_quote
                break
            elif key == 16:  # Ctrl+P = 16 (ascii code)
                admin_menu(stdscr, pending_quotes, approved_quotes)
                current_quote = None
                break
            time.sleep(0.1)

        if newly_added_quote is None:
            current_quote = None

curses.wrapper(main)
