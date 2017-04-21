#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   globals.py by:
#   Cristian García <cristian99garcia@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

from gi.repository import Gdk


SELECTED_BOX = Gdk.Color(30000, 30000, 30000)
SPACE_BOX = Gdk.Color(0, 0, 0)
NORMAL_BOX = Gdk.Color(65535, 65535, 65535)
ENTER_BOX = Gdk.Color(60000, 60000, 60000)

KEY_RIGHT = 65361
KEY_UP = 65362
KEY_LEFT = 65363
KEY_DOWN = 65364
KEY_SPACE = 32

LETTERS = {}

for x in range(65, 91) + range(97, 123):
    LETTERS[x] = chr(x)

screen = Gdk.Screen.get_default()

DISPLAY_WITH = screen.width()
DISPLAY_HEIGHT = screen.height() - 20

CROSSWORDS_DIR = os.path.join(os.path.dirname(__file__), 'crosswords/en')


class State:
    EDITING = 0
    GAMING = 1
    GAME_OVER = 2


def get_letter_label_size():
    if DISPLAY_WITH >= 1200:
        return (DISPLAY_WITH - 1000) / 14

    else:
        return 10


def get_number_label_size():
    return DISPLAY_WITH / 120


def get_win_label_size():
    return DISPLAY_WITH / 20
