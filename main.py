"""This executable module launches the KrisCo Fallout Hack Screensaver."""

################################# I M P O R T S ################################

# Standard Library imports:
import random
import string
import sys
import time
from win32 import win32api
from typing import List, Literal, Tuple


# Third party imports:
import pyrogue

############################### C O N S T A N T S ##############################

ADDR_CT: int = 32               # Number of addresses
ADDR_LEFT_OFFSET: int = 1       # Column where addresses on left section begin
ADDR_RIGHT_OFFSET: int = 30     # Column where addresses on right section begin
CHARS_PER_ADDR: int = 12        # Number of characters-per address
COLUMNS: int = 80               # Max. columns in screen
DATA_LEFT_OFFSET: int = 8       # Column where data on left section begins
DATA_RIGHT_OFFSET: int = 37     # Column where data on right section begins
DATA_ROW_OFFSET: int = 8        # Row where data begins
DIVIDER_COLUMN: int = 59        # Column to place vertical divider
GUESS_COLUMN: int = 60          # Column where guesses are drawn
GUESS_ROW: int = 1              # Row where the first guess is drawn
GUESS_CT: int = 48              # Max. lines in guess section
LOCKOUT_COL: int = 2            # Column where lockout message is drawn
LOCKOUT_ROW: int = 46           # Row where lockout message is drawn
ROWS: int = 50                  # Max. rows in screen

###################### C O N F I G U R A B L E    D A T A ######################

config_fg_color: Tuple[int, int, int] = (0, 255, 0) # Foreground color
config_guess_ct: int = 5        # Max. number of guesses before lockout
config_lockout_time: int = 15   # Time penalty for lockout (in sec.)
config_word_len: int = 6        # Guess word length
config_word_ct: int = 12        # Guess word count

#################### A U X I L I A R Y    F U N C T I O N S ####################

def choose_words(wordlen: int, wordct: int) -> List[str]:
    """Choose a list of random words. The list will not contain any repeats."""

    ret: List[str]          # Return data
    temp_word: str           # Stages random choice before it is checked

    ret = []
    for _ in range(wordct):
        temp_word = rand_word(wordlen)

        # Ensure no repeats occur:
        while temp_word in ret:
            temp_word = rand_word(wordlen)
        ret.append(temp_word)
    return ret

def draw_addrs() -> None:
    """Draw the memory addresses."""

    start_addr: int                 # Start address
    row: int                        # Row to print current addr
    col: int                        # Column to print current addr
    addr_tstr: List[pyrogue.Tile]   # Tile string for current addr

    # Choose a random start address. The start address should be divisible by 4
    # and should leave enough space to fit all addresses on screen without 
    # rolling over.

    # 16384 = # of values in a 16-bit number, divided by 4
    # 32 = Number of addrs offset from the max needed to accomodate all addrs
    # 4 = All displayed addresses should be divisible by 4
    start_addr = random.randint(0, 16384 - 1 - 32) * 4
    row = DATA_ROW_OFFSET
    col = ADDR_LEFT_OFFSET

    for addr in range(start_addr, start_addr + (32*4), 4):
        if (row == DATA_ROW_OFFSET + 32):
            row = DATA_ROW_OFFSET
            col = ADDR_RIGHT_OFFSET
        addr_tstr = pyrogue.get_tstr(hex(addr), fg=config_fg_color)
        pyrogue.draw_tstr(addr_tstr, col, row)

        # Skip every other row:
        row += 2
    return

def draw_borders() -> None:
    """Draw the line-art borders."""

    top_left: pyrogue.Tile      # Top-left line-art corner
    top_right: pyrogue.Tile     # Top-right line-art corner
    bot_left: pyrogue.Tile      # Bottom-left line-art corner
    bot_right: pyrogue.Tile     # Botton-right line-art corner
    horiz: pyrogue.Tile         # Horizontal line-art
    vert: pyrogue.Tile          # Vertical line-art
    t_up: pyrogue.Tile          # Upwards t-junction line-art
    t_down: pyrogue.Tile        # Downwards t-junction line-art

    # Create tiles:
    top_left = pyrogue.get_tile(201, fg=config_fg_color)
    top_right = pyrogue.get_tile(187, fg=config_fg_color)
    bot_left = pyrogue.get_tile(200, fg=config_fg_color)
    bot_right = pyrogue.get_tile(188, fg=config_fg_color)
    horiz = pyrogue.get_tile(205, fg=config_fg_color)
    vert = pyrogue.get_tile(186, fg=config_fg_color)
    t_up = pyrogue.get_tile(202, fg=config_fg_color)
    t_down = pyrogue.get_tile(203, fg=config_fg_color)

    # Draw the top and bottom lines:
    for col in range(COLUMNS):
        if col == 0:
            pyrogue.draw_tile(top_left, col, 0)
            pyrogue.draw_tile(bot_left, col, ROWS-1)
        elif col == COLUMNS-1:
            pyrogue.draw_tile(top_right, col, 0)
            pyrogue.draw_tile(bot_right, col, ROWS-1)
        else:
            pyrogue.draw_tile(horiz, col, 0)
            pyrogue.draw_tile(horiz, col, ROWS-1)

    # Draw the vertical borders:
    for row in range(ROWS):
        if row == 0:
            pyrogue.draw_tile(t_down, DIVIDER_COLUMN, row)
            continue
        elif row == ROWS-1:
            pyrogue.draw_tile(t_up, DIVIDER_COLUMN, row)
            continue
        else:
            pyrogue.draw_tile(vert, DIVIDER_COLUMN, row)
            pyrogue.draw_tile(vert, 0, row)
            pyrogue.draw_tile(vert, COLUMNS-1, row)
    return

def draw_data(tiles: List[pyrogue.Tile]) -> None:
    """Draw the data characters."""

    row: int        # Row to draw the current line of data
    col: int        # Column to draw the current line of data

    row = DATA_ROW_OFFSET
    col = DATA_LEFT_OFFSET
    for i in range(len(tiles)):
        col, row = get_data_pos(i)
        pyrogue.draw_tile(tiles[i], col, row)
        col += 1
    return
    
def draw_default_txt() -> None:
    """Draw the default menu text."""

    title_str: str                      # Title text
    enter_str: str                      # "Enter password now" text
    guess_str: str                      # Guesses remaining text
    titletstr: List[pyrogue.Tile]       # Title text tile string
    entertstr: List[pyrogue.Tile]       # "Enter password now" text tile string
    guesststr: List[pyrogue.Tile]       # Guesses remaining text tile string

    title_str = "KrisCo Industries (TM) TermLink Protocol"
    titletstr = pyrogue.get_tstr(title_str, fg=config_fg_color)
    pyrogue.draw_tstr(titletstr, 1, 1)
    enter_str = "Enter Password Now"
    entertstr = pyrogue.get_tstr(enter_str, fg=config_fg_color)
    pyrogue.draw_tstr(entertstr, 1, 2)
    guess_str = "{} Guesses Remaining".format(config_guess_ct)
    guesststr = pyrogue.get_tstr(guess_str, fg=config_fg_color)
    pyrogue.draw_tstr(guesststr, 1, 4)
    return

def draw_guess(txt: str, ln: int) -> None:
    """
    Draw text to the guess panel.

    `ln` is the line number (not the row number), zero-indexed.

    This function does not perform redraw.
    """

    out: str                            # String that will be drawn
    col: int                            # Column where text will be drawn
    row: int                            # Row where text will be drawn
    tiles: List[pyrogue.Tile]           # Tile string that will be drawn    

    out = ">" + txt
    col = GUESS_COLUMN
    row = GUESS_ROW + ln
    tiles = pyrogue.get_tstr(out, fg=config_fg_color)
    pyrogue.draw_tstr(tiles, col, row)
    return

def get_char_matches(guess: str, ans: str) -> int:
    """
    Return the number of characters that match (position and value) between
    a given guess and the answer.
    """

    ret: int        # Return data 

    ret = 0
    for i in range(len(guess)):
        if guess[i] == ans[i]:
            ret += 1
    return ret

def get_cursor_word(cursor: int, chars: str) -> str:
    """
    Get the word that the cursor is currently on. 
    
    If the cursor is on a garbage character, return an empty string.
    """

    ret: str        # Return data

    if chars[cursor] not in string.ascii_uppercase:
        ret = ""
    else:

        # First, move the cursor to the left most character of the word:
        while True:
            if cursor-1 <= 0:
                break
            if chars[cursor-1] not in string.ascii_uppercase:
                break
            cursor -= 1
        
        # Slice `chars` to yield the string and return it:
        ret = chars[cursor:cursor+config_word_len]
    return ret

def get_data_pos(index: int) -> Tuple[int, int]:
    """
    Get the position that the given data char should be written to the screen, 
    in tile space.
    
    Returns the position as a `Tuple` containing the column and row.
    """

    word_no: int            # The index of the "word" the char belongs to
    word_pos: int           # The position of the char within the "word"
    col: int                # The column-part of the return data (index 0)
    row: int                # The row-part of the return data (index 1)

    word_no = index // CHARS_PER_ADDR
    word_pos = index % CHARS_PER_ADDR

    # Treat the first half of the data array separate from the last half, since
    # we are splitting the data characters into two separate sections:

    # Front half:
    if word_no < (ADDR_CT/2):
        col = DATA_LEFT_OFFSET + word_pos

        # Multiply the row by two, so that we skip every other row.
        row = DATA_ROW_OFFSET + (word_no * 2)

    # Back half
    else:
        col = DATA_RIGHT_OFFSET + word_pos

        # Multiply the row by two, so that we skip every other row. Subtract
        # by 32 (16*2) since we are now on the righthand section.
        row = (DATA_ROW_OFFSET + (word_no * 2)) - 32
    return (col, row)

def get_left_bound(index: int, chars: str) -> int:
    """
    Get the leftmost letter of the word in which the current index belongs. If
    the current index points to a garbage character, return None.
    """

    ret: int                # Return data

    if chars[index] not in string.ascii_uppercase:
        return None
    ret = index
    while True:
        if ret-1 < 0:
            break
        if chars[ret-1] not in string.ascii_uppercase:
            break
        ret -= 1
    return ret

def get_right_bound(index: int, chars: str) -> int:
    """
    Get the rightmost letter of the word in which the current index belongs. If
    the current index points to a garbage character, return None.
    """

    ret: int                # Return data

    if chars[index] not in string.ascii_uppercase:
        return None
    ret = index
    while True:
        if ret+1 >= len(chars):
            break
        if chars[ret+1] not in string.ascii_uppercase:
            break
        ret += 1
    return ret

def invert_word(index: int, chars: str, tlist: List[pyrogue.Tile]) -> None:
    """
    If the given index is a letter, invert the whole word it belongs to.

    `chars` is the data character `str`.

    `tlist` is the List of data character tiles.
    """

    start: int                      # The index of the first letter
    end: int                        # The index of the last letter
    draw_pos: Tuple[int, int]       # The position to draw the current char

    if chars[index] not in string.ascii_uppercase:
        return
    start = get_left_bound(index)
    end = get_right_bound(index)
    for i in range(start, end-1):
        draw_pos = get_data_pos(i)
        pyrogue.invert_tile(tlist[i])
        pyrogue.draw_tile(tlist[i], draw_pos[0], draw_pos[1])
        pyrogue.update()
    return

def insert_words(words: List[str], chars: str) -> str:
    """
    Place the list of words into the data character string such that they are 
    not truncated and do not overlap or abut.
    """

    ret: str                    # Return data
    can_place: bool             # Whether or not the current word can be placed
    start_pos: int              # Position where the current word will be placed

    ret = chars
    for word in words:

        # Choose a random start position:
        while True:
            can_place = True

            # Don't allow startpos==0, that way we don't have to handle
            # inverting that word at init:
            start_pos = random.randint(1, len(ret)-1)
            for i in range(start_pos, start_pos+6):

                # Check for out-of-bounds, and collision with previously placed
                # words:
                if i >= len(ret):
                    can_place = False
                    break
                if ret[i] in string.ascii_uppercase:
                    can_place = False
                    break
            
            # Give at least one space between sucessive words:
            if (start_pos+config_word_len+1 < len(ret)) and \
                    (ret[start_pos+config_word_len+1] in \
                    string.ascii_uppercase):
                can_place = False
            if (start_pos-1 >= 0) and (ret[start_pos-1] in \
                    string.ascii_uppercase):
                can_place = False
            if can_place:
                break

        # Place the word:       
        for i in range(config_word_len):
            ret = ret[:start_pos+i] + word.strip()[i].upper() + \
                ret[start_pos+1+i:]
    return ret

def lockout(secs: int) -> None:
    """
    Perform the lockout loop, which is initialized when the user runs out of
    guesses.
    """

    out: str                                # String being drawn
    tiles: List[pyrogue.Tile]               # Tile string being drawn

    for i in range(secs):
        out = "                                                   "
        tiles = pyrogue.get_tstr(out, bg=config_fg_color, fg=(0, 0, 0))
        pyrogue.draw_tstr(tiles, LOCKOUT_COL, LOCKOUT_ROW)
        out = "BYPASS ROUTINE INITIALIZED. TIME REMAINING: {} sec.".\
            format(config_lockout_time-i)
        tiles = pyrogue.get_tstr(out, bg=config_fg_color, fg=(0, 0, 0))
        pyrogue.draw_tstr(tiles, LOCKOUT_COL, LOCKOUT_ROW)
        pyrogue.update()
        time.sleep(1.0)
    
    out = "                                                   "
    tiles = pyrogue.get_tstr(out)
    pyrogue.draw_tstr(tiles, LOCKOUT_COL, LOCKOUT_ROW)
    out = "{} Guesses Remaining".format(config_guess_ct)
    tiles = pyrogue.get_tstr(out, fg=config_fg_color)
    pyrogue.draw_tstr(tiles, 1, 4)
    pyrogue.update()

def move_cursor(cursor: int, dir: Literal["U", "D", "L", "R"], \
        tiles: List[pyrogue.Tile]) -> int:
    """
    Move the cursor on the screen.

    `cursor` is the index of the data-character-string/tile-list that
    corresponds with the on screen cursor.

    `dir` indicates which direction to move the cursor.
    
    Returns the change that should be applied to the stored cursor value.
    """

    ret: int                        # Return Data
    new_cursor: int                 # New cursor position
    invert_cursor: bool             # Whether or not to invert the old cursor
    new_delta: int                  # Temp. cursor delta for scanning
    pos: Tuple[int, int]            # Position to invert

    # Determine the return value, which is the change to `cursor:
    if dir == "U":
        ret = -12
    elif dir == "D":
        ret = 12
    elif dir == "L":
        ret = -1
    elif dir == "R":
        ret = 1
    else:
        raise ValueError('`dir` should be in ["U", "D", "L", "R"].')
    new_cursor = cursor+ret

    # Check for out of bounds:
    if (new_cursor <= 0) or (new_cursor >= len(tiles)):
        ret = 0
    else:
        invert_cursor = True

        # If the cursor is currently at a letter, we must uninvert the entire
        # word the letter belongs to:
        if (tiles[cursor].char in string.ascii_uppercase):

            # Remember that we don't need to re-uninvert the cursor later, 
            invert_cursor = False

            # Find the rightmost character of the word:
            new_delta = 0
            while True:
                if cursor+new_delta+1 >= len(tiles):
                    break
                if tiles[cursor+new_delta+1].char not in \
                        string.ascii_uppercase:
                    break
                new_delta += 1
            
            # Begin scanning left, inverting the tiles as we go, until we reach
            # the left end of the word.
            while True:
                pyrogue.invert_tile(tiles[cursor+new_delta])
                pos =get_data_pos(cursor+new_delta)
                pyrogue.draw_tile(tiles[cursor+new_delta], pos[0], pos[1])
                if cursor+new_delta-1 <= 0:
                    break
                if tiles[cursor+new_delta-1].char not in \
                        string.ascii_uppercase:
                    break
                new_delta -= 1

            # If the movement is horizontal, slide to the end of the word in
            # the correct direction:
            if ret in [1, -1]:
                step = ret
                while True:
                    if (cursor+ret < 0) or (cursor+ret >= len(tiles)):
                        break
                    if tiles[cursor+ret].char not in string.ascii_uppercase:
                        break
                    ret += step
                new_cursor = cursor+ret
            
        # Determine whether or not the destination character is a letter:
        if tiles[new_cursor].char in string.ascii_uppercase:

            # First, invert the original cursor, so that it appears uninverted:
            if invert_cursor:
                pyrogue.invert_tile(tiles[cursor])
                pos = get_data_pos(cursor)
                pyrogue.draw_tile(tiles[cursor], pos[0], pos[1])

            # Find the rightmost character of the word:
            new_delta = 0
            while True:
                if new_cursor+new_delta+1 >= len(tiles):
                    break
                if tiles[new_cursor+new_delta+1].char not in \
                        string.ascii_uppercase:
                    break
                new_delta += 1
            
            # Begin scanning left, inverting the tiles as we go, until we reach
            # the left end of the word.
            while True:
                pyrogue.invert_tile(tiles[new_cursor+new_delta])
                pos =get_data_pos(new_cursor+new_delta)
                pyrogue.draw_tile(tiles[new_cursor+new_delta], pos[0], pos[1])
                if new_cursor+new_delta-1 <= 0:
                    break
                if tiles[new_cursor+new_delta-1].char not in \
                        string.ascii_uppercase:
                    break
                new_delta -= 1
        else:

            # Move the cursor:
            if invert_cursor:
                pyrogue.invert_tile(tiles[cursor])
                pos = get_data_pos(cursor)
                pyrogue.draw_tile(tiles[cursor], pos[0], pos[1])
            pyrogue.invert_tile(tiles[new_cursor])
            pos = get_data_pos(new_cursor)
            pyrogue.draw_tile(tiles[new_cursor], pos[0], pos[1])
    return ret

def rand_chars() -> str:
    """
    Create a string with the random characters that will be drawn to the screen.
    """

    ret: str                    # Return data

    ret = ""
    for _ in range(CHARS_PER_ADDR*ADDR_CT):
        ret += random.choice("~`!@#$%^&*()_-+={[}]|\\:;\"'<,>.?/")
    return ret

def rand_word(word_len: int) -> str:
    """Get a random english word with the given length."""

    words: List[str]            # The entire dictionary
    ret: str                    # Return data

    with open("dictionary.txt") as fp:
        words = fp.read().split()
    ret = random.choice(words)
    while len(ret) != word_len:
        ret = random.choice(words)
    return ret

def scroll(guess_buf: List[str], lines: int) -> List[str]:
    """
    Scroll the guess section by the given number of lines.
    
    Return the updated guess buffer.
    """

    blank_tiles: List[pyrogue.Tile]             # Tile string for blank line
    ret: List[str]                              # Return data

    # Clear the guess section:
    blank_tiles = pyrogue.get_tstr("                   ")
    for i in range(GUESS_CT):
        pyrogue.draw_tstr(blank_tiles, GUESS_COLUMN, GUESS_ROW+i)

    # Update the buffer, and draw each line:
    ret = guess_buf[lines:]
    for i in range(len(ret)):
        draw_guess(ret[i], i)

    return ret

########################## M A I N    F U N C T I O N ##########################

def main():

    mode: str                           # Mode specified in argv
    parentwin: str                      # Parent window handle
    words: List[str]                    # Guess words
    ans: str                            # Answer
    chars: str                          # Data characters
    guesses: int                        # Current number of guesses left
    guessbuf: List[str]                 # Buffer of msgs. in guess pane
    data_tiles: List[pyrogue.Tile]      # Tile string of data chars
    drawpos: Tuple[int, int]            # Initial draw position of cursor
    running: bool                       # Continue main loop?
    cursor: int                         # Cursor position as index of chars
    curr_word: str                      # Word that the cursor is currently on
    out: str                            # Text to draw to guess panel

    # Parse the argument vector:
    if len(sys.argv) > 1:
        
        # The argument vector should contain a mode flag, and may also contain
        # an optional window handle. The window handle may be separated from
        # the mode flag by EITHER a space, or a colon.
        if len(sys.argv) == 2:
            if ":" in sys.argv[1]:
                mode = sys.argv[1].split(":")[0].lower()
                parentwin = sys.argv[2]
            else:
                mode = sys.argv[1].lower()
                parentwin = ""
        elif len(sys.argv) == 3:
            mode = sys.argv[1].lower()
            parentwin = sys.argv[2]
        else:
            raise TypeError(\
                "This script only accepts only 1 or 2 optional arguments.")
    else:
        mode = "/c"
        parentwin = ""
        
    # HANDLE CONFIGURATION MODE:
    if mode == "/c":
    
        # TODO Implement config mode

        win32api.MessageBox(0, "This screensaver does not currently have " + \
            "a configuration mode!", "Warning!")

    # HANDLE PREVIEW MODE:
    elif mode == "/p":

        # TODO Implement preview mode

        pass

    # HANDLE FULL-SCREEN MODE:
    elif mode == "/s":

        # Screen initialization stuff:
        pyrogue.init()
        pyrogue.set_mode(COLUMNS, ROWS, "tiles16.png", full=True)
        draw_borders()
        pyrogue.update()
        draw_default_txt()
        draw_addrs()

        # Generate the data characters, and the list of words. Then, insert the
        # words into the data characters.
        words = choose_words(config_word_len, config_word_ct)
        ans = random.choice(words).upper()
        chars = rand_chars()
        chars = insert_words(words, chars)
        guesses = config_guess_ct
        guessbuf = []

        # Create the data character tiles and draw them:
        data_tiles = pyrogue.get_tstr(chars, fg=config_fg_color)
        draw_data(data_tiles)
        pyrogue.update()

        # Cursor initialization:
        cursor = 0
        pyrogue.invert_tile(data_tiles[cursor])
        drawpos = get_data_pos(cursor)
        pyrogue.draw_tile(data_tiles[cursor], drawpos[0], drawpos[1])
        pyrogue.update()

        # Main loop:
        running = True
        while running:
            for ev in pyrogue.get_events():
                if ev.type == pyrogue.EVENT_KEYDOWN:

                    # Handle cursor movement:
                    if ev.key == pyrogue.KEY_LEFT:
                        if cursor <= 0:
                            continue
                        else:
                            cursor += move_cursor(cursor, "L", data_tiles)
                            pyrogue.update()
                    elif ev.key == pyrogue.KEY_RIGHT:
                        if cursor >= len(data_tiles)-1:
                            continue
                        else:
                            cursor += move_cursor(cursor, "R", data_tiles)
                            pyrogue.update()
                    elif ev.key == pyrogue.KEY_UP:
                        if (cursor - 12) < 0:
                            continue
                        else:
                            cursor += move_cursor(cursor, "U", data_tiles)
                            pyrogue.update()
                    elif ev.key == pyrogue.KEY_DOWN:
                        if (cursor + 12) >= len(data_tiles):
                            continue
                        else:
                            cursor += move_cursor(cursor, "D", data_tiles)
                            pyrogue.update()
                    elif ev.key == pyrogue.KEY_ENTER:
                        curr_word = get_cursor_word(cursor, chars)
                        if curr_word:

                            if len(guessbuf) >= GUESS_CT:
                                guessbuf = scroll(guessbuf, 1)
                            guessbuf.append(curr_word)
                            draw_guess(curr_word, len(guessbuf)-1)

                            # If the guess is incorrect, print "Entry Denied",
                            # and provide the number of matching characters:
                            if curr_word != ans:
                                guesses -= 1

                                guessstr = "{} Guesses Remaining".\
                                    format(guesses)
                                guesststr = pyrogue.get_tstr(guessstr, \
                                    fg=config_fg_color)
                                pyrogue.draw_tstr(guesststr, 1, 4)
                                if len(guessbuf) >= GUESS_CT:
                                    guessbuf = scroll(guessbuf, 1)
                                out = "Entry Denied"
                                guessbuf.append(out)
                                draw_guess(out, len(guessbuf)-1)
                                
                                if len(guessbuf) >= GUESS_CT:
                                    guessbuf = scroll(guessbuf, 1)
                                out = "{}/{} Correct".\
                                    format(get_char_matches(curr_word, ans), \
                                    config_word_len)
                                guessbuf.append(out)
                                draw_guess(out, len(guessbuf)-1)
                                pyrogue.update()
                                if guesses == 0:
                                    if len(guessbuf) >= GUESS_CT:
                                        guessbuf = scroll(guessbuf, 1)
                                    out = "Too many"
                                    guessbuf.append(out)
                                    draw_guess(out, len(guessbuf)-1)
                                        
                                    if len(guessbuf) >= GUESS_CT:
                                        guessbuf = scroll(guessbuf, 1)
                                    out = "failed attempts."
                                    guessbuf.append(out)
                                    draw_guess(out, len(guessbuf)-1)

                                    if len(guessbuf) >= GUESS_CT:
                                        guessbuf = scroll(guessbuf, 1)
                                    out = "Locking terminal."
                                    guessbuf.append(out)
                                    draw_guess(out, len(guessbuf)-1)
                                    pyrogue.update()

                                    time.sleep(2.0)
                                    lockout(config_lockout_time)
                                    guesses = config_guess_ct

                                    if len(guessbuf) >= GUESS_CT:
                                        guessbuf = scroll(guessbuf, 1)
                                    out = "Terminal unlocked."
                                    guessbuf.append(out)
                                    draw_guess(out, len(guessbuf)-1)
                                    pyrogue.update()
                            else:
                                if len(guessbuf) >= GUESS_CT:
                                    guessbuf = scroll(guessbuf, 1)
                                out = "Exact Match!"
                                guessbuf.append(out)
                                draw_guess(out, len(guessbuf)-1)

                                if len(guessbuf) >= GUESS_CT:
                                    guessbuf = scroll(guessbuf, 1)
                                out = "Please wait"
                                guessbuf.append(out)
                                draw_guess(out, len(guessbuf)-1)

                                if len(guessbuf) >= GUESS_CT:
                                    guessbuf = scroll(guessbuf, 1)
                                out = "while system"
                                guessbuf.append(out)
                                draw_guess(out, len(guessbuf)-1)

                                if len(guessbuf) >= GUESS_CT:
                                    guessbuf = scroll(guessbuf, 1)
                                out = "is accessed."
                                guessbuf.append(out)
                                draw_guess(out, len(guessbuf)-1)

                                pyrogue.update()
                                time.sleep(3.0)
                                running = False

                if ev.type == pyrogue.EVENT_QUIT:
                    running = False
    else:

        # Handle illegal mode flags:
        win32api.MessageBox(0, "Invalid mode flag {}".format(mode), "Warning!")

    pyrogue.quit()

if __name__ == "__main__":
    main()