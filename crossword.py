#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   crossword.py by:
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

from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.activity import activity
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import _create_activity_icon as ActivityIcon

from ConfigParser import RawConfigParser

import globals as G
from gettext import gettext as _

from widgets import GameArea
from widgets import AreaOfClue
from widgets import Canvas
from widgets import WinCanvas
from widgets import FileChooser


class CrossWordActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle, False)

        self.state = G.State.EDITING
        self.advices = 5

        self.game_area = GameArea()
        self.area_clue = AreaOfClue()
        self.canvas_area = Canvas(self.game_area, self.area_clue)
        self.win_canvas = WinCanvas()

        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.set_toolbar_box(self.make_toolbarbox())

        self.canvas_area.connect('change-state', self.state_changed)
        self.game_area.connect('end-game', self.end_game)
        self.win_canvas.connect('new-game', self.new_game)
        self.connect('key-press-event', self._key_press_cb)

        self.set_canvas(self.canvas_area)
        self.show_all()

    def _key_press_cb(self, widget, event):
        self.canvas_area.key(event.keyval)

    def state_changed(self, widget, state):
        self.state = state
        self.canvas_area.set_state(self.state)
        self.button_advice.set_sensitive(
            state == G.State.GAMING and self.advices)

    def end_game(self, *args):
        self.button_new.set_sensitive(True)
        self.button_save.set_sensitive(False)
        self.button_open.set_sensitive(True)
        self.button_advice.set_sensitive(False)

        self.state_changed(None, G.State.GAME_OVER)
        self.canvas_area.set_children(self.win_canvas)

    def make_toolbarbox(self):
        def make_separator(expand=False):
            separator = Gtk.SeparatorToolItem()
            if expand:
                separator.props.draw = False
                separator.set_expand(True)

            return separator

        toolbar_box = ToolbarBox()
        activity_button = ToolButton()
        self.button_new = ToolButton('new-game')
        self.button_save = ToolButton(Gtk.STOCK_SAVE)
        self.button_open = ToolButton(Gtk.STOCK_OPEN)
        self.button_advice = ToolButton(Gtk.STOCK_ADD)
        stop_button = ToolButton('activity-stop')

        self.button_new.connect('clicked', self.new_game)
        self.button_save.connect('clicked', self.save_game)
        self.button_open.connect('clicked', self.open_game)
        self.button_advice.connect('clicked', self.new_advice)
        stop_button.connect('clicked', self._exit)

        activity_button.set_icon_widget(ActivityIcon(None))
        activity_button.set_tooltip(self.get_title())
        self.button_new.set_tooltip(_('New game'))
        self.button_new.props.accelerator = '<Ctrl>N'
        self.button_save.set_tooltip(_('Save game'))
        self.button_save.props.accelerator = '<Ctrl>S'
        self.button_open.set_tooltip(_('Open game'))
        self.button_open.props.accelerator = '<Ctrl>O'
        self.button_advice.set_tooltip(_('New hint\nYou have %d hints.' % (5)))
        self.button_advice.props.accelerator = '<Ctrl>A'
        self.button_advice.set_sensitive(False)
        stop_button.props.accelerator = '<Ctrl>Q'

        toolbar_box.toolbar.insert(activity_button, -1)
        toolbar_box.toolbar.insert(make_separator(), -1)
        toolbar_box.toolbar.insert(self.button_new, -1)
        toolbar_box.toolbar.insert(self.button_save, -1)
        toolbar_box.toolbar.insert(self.button_open, -1)
        toolbar_box.toolbar.insert(make_separator(), -1)
        toolbar_box.toolbar.insert(self.button_advice, -1)
        toolbar_box.toolbar.insert(make_separator(True), -1)
        toolbar_box.toolbar.insert(stop_button, -1)

        return toolbar_box

    def new_advice(self, *args):
        self.advices -= 1

        if self.advices:
            text = 'New hint\nYou have: %d hints.' % (self.advices)
            text += 's' if self.advices > 1 else ''
            self.button_advice.set_tooltip(_(text))
            self.game_area.show_an_advice()

        else:
            self.advices = 0
            self.button_advice.set_sensitive(False)
            self.button_advice.set_tooltip(
                _('New hint\nYou have: %d hints.' % (0)))

    def open_game(self, *args):
        def _post_open(widet, chooser):
            self.advices = 5

            self.canvas_area.load_game(chooser.get_filename())
            self.button_save.set_sensitive(False)
            self.button_advice.set_sensitive(True)
            self.button_advice.set_tooltip(
                _('New hint\nYou have %d hints.' % (5)))
            chooser.destroy()

        chooser = FileChooser('open', self)
        button_cancel = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        button_ok = Gtk.Button.new_from_stock(Gtk.STOCK_OPEN)

        button_cancel.connect('clicked', chooser._destroy)
        button_ok.connect('clicked', _post_open, chooser)

        chooser.set_buttons([button_cancel, button_ok])
        chooser.show_all()

    def new_game(self, *args):
        self.state = G.State.EDITING
        self.canvas_area.new_game()
        self.canvas.set_state(G.State.EDITING)
        self.button_save.set_sensitive(True)
        self.button_advice.set_sensitive(False)

    def save_game(self, *args):
        def _save(widget, chooser):
            config = RawConfigParser()
            horizontals = self.area_clue.get_horizontals()
            verticals = self.area_clue.get_verticals()
            path = chooser.get_filename()
            path += '.cwg' if not path.endswith('.cwg') else ''
            game = self.game_area.get_actual_game()

            config.add_section('Horizontals')

            for x in horizontals:
                config.set('Horizontals', str(x), horizontals[x])

            config.add_section('Verticals')

            for x in verticals:
                config.set('Verticals', str(x), horizontals[x])

            config.add_section('Game')

            for x in range(1, 11):
                config.set('Game', str(x), game.split('\n')[x-1])

            with open(path, 'wb') as configfile:
                config.write(configfile)

            chooser._destroy()

        chooser = FileChooser('save', self)
        button_cancel = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        button_ok = Gtk.Button.new_from_stock(Gtk.STOCK_SAVE)

        button_cancel.connect('clicked', chooser._destroy)
        button_ok.connect('clicked', _save, chooser)

        chooser.set_buttons([button_cancel, button_ok])
        chooser.show_all()

    def _exit(self, *args):
        self.close()
