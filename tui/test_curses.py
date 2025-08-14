#!/usr/bin/env python
import curses
from curses.textpad import Textbox, rectangle


def msg_input(stdscr):
    stdscr.addstr(0, 0, "Enter IM message: (hit Ctrl-G to send)")

    editwin = curses.newwin(5, 30, 2, 1)
    rectangle(stdscr, 1, 0, 1 + 5 + 1, 1 + 30 + 1)
    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()

    stdscr.clear()
    stdscr.addstr(0, 0, message)
    return message


if __name__ == "__main__":
    msg = curses.wrapper(msg_input)
    print(msg)
