#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   widgets.py by:
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
from gi.repository import Pango
from gi.repository import GObject

from sugar3.graphics import style
from sugar3.graphics.icon import Icon

import random
import globals as G
from ConfigParser import ConfigParser
from gettext import gettext as _


class Canvas(Gtk.HBox):

    __gsignals__ = {
        'change-state': (GObject.SIGNAL_RUN_FIRST, None, [int]),
        }

    def __init__(self, game_area, area_clue):
        Gtk.HBox.__init__(self)

        self.game_area = game_area
        self.area_clue = area_clue

        self.game_area.connect('box-selected', self.box_selected)

        self.pack_start(self.game_area, False, False, 10)
        self.pack_start(self.area_clue, True, True, 5)

    def key(self, key):
        if self.area_clue.horizontals.focus or self.area_clue.verticals.focus:
            return

        if key in G.LETTERS or key == G.KEY_SPACE:
            letter = chr(key)
            self.game_area.set_letter(letter.upper())

        else:
            if key in [G.KEY_UP, G.KEY_DOWN, G.KEY_LEFT, G.KEY_RIGHT]:
                self.game_area.move_selected_item(key)

    def box_selected(self, widget):
        self.area_clue.horizontals.focus = False
        self.area_clue.verticals.focus = False
        self.area_clue.horizontals.set_editable(False)
        self.area_clue.verticals.set_editable(False)

    def load_game(self, path):
        config = ConfigParser()
        config.read(path)
        game = ''

        if 'Horizontals' not in config.sections() and \
           'Verticals' not in config.sections():

            print 'Error trying load %s' % path
            return

        for x in range(1, 11):
            game += config.get('Game', str(x)) + '\n'

        self.game_area.set_game(game)
        self.area_clue.clean()

        for x in range(1, 101):
            if config.has_option('Horizontals', str(x)):
                self.area_clue.add_clue(
                    str(x) + ' - ' + config.get('Horizontals', str(x)), 0)

        for x in range(1, 101):
            if config.has_option('Verticals', str(x)):
                self.area_clue.add_clue(
                    str(x) + ' - ' + config.get('Verticals', str(x)), 1)

        self.emit('change-state', G.State.GAMING)

    def set_children(self, widget):
        self.remove(self.game_area)
        self.remove(self.area_clue)
        self.add(widget)

    def new_game(self):
        if self.game_area not in self.get_children():
            self.remove(self.get_children()[0])
            self.pack_start(self.game_area, False, False, 10)
            self.pack_start(self.area_clue, True, True, 0)
            self.show_all()

        self.game_area.new_game()
        self.area_clue.clean()

    def set_state(self, state):
        self.game_area.set_state(state)
        self.area_clue.set_state(state)


class AreaOfClue(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.state = G.State.EDITING
        self.horizontals = Gtk.TextView()
        self.horizontals.focus = False
        self.horizontals.text = ''
        self.verticals = Gtk.TextView()
        self.verticals.focus = False
        self.verticals.text = ''

        self.horizontals.connect('focus-in-event', self.focus_in)
        self.horizontals.connect('focus-out-event', self.focus_out)
        self.verticals.connect('focus-in-event', self.focus_in)
        self.verticals.connect('focus-out-event', self.focus_out)

        frame1 = Gtk.Frame()
        label1 = Gtk.Label('Horizontals')
        scrolled1 = Gtk.ScrolledWindow()
        frame2 = Gtk.Frame()
        label2 = Gtk.Label('Verticals')
        scrolled2 = Gtk.ScrolledWindow()

        self.horizontals.modify_font(Pango.FontDescription('13'))
        self.horizontals.set_wrap_mode(Gtk.WrapMode.WORD)
        self.verticals.set_wrap_mode(Gtk.WrapMode.WORD)
        self.verticals.modify_font(Pango.FontDescription('13'))
        label1.modify_font(Pango.FontDescription('bold 15'))
        label2.modify_font(Pango.FontDescription('bold 15'))
        frame1.set_label_widget(label1)
        frame2.set_label_widget(label2)
        self.set_margin_left(50)

        scrolled1.add(self.horizontals)
        scrolled2.add(self.verticals)
        frame1.add(scrolled1)
        frame2.add(scrolled2)
        self.pack_start(frame1, True, True, 10)
        self.pack_start(frame2, True, True, 10)

        self.show_all()

    def focus_in(self, widget, event):
        if self.state != G.State.GAMING:
            widget.focus = True
            widget.set_editable(True)

    def focus_out(self, widget, event):
        widget.focus = False
        widget.set_editable(False)

    def get_buffer_text(self, _buffer):
        i1, i2 = _buffer.get_bounds()
        return _buffer.get_text(i1, i2, 0)

    def get_horizontals_text(self):
        return self.get_buffer_text(self.horizontals.get_buffer())

    def get_verticals_text(self):
        return self.get_buffer_text(self.verticals.get_buffer())

    def add_clue(self, clue, orientation):
        if orientation == 0:
            text = self.get_horizontals_text()

            if text is not None:
                text += clue + '\n'
                self.horizontals.get_buffer().set_text(text)

        elif orientation == 1:
            text = self.get_verticals_text()

            if text is not None:
                text += clue + '\n'
                self.verticals.get_buffer().set_text(text)

    def clean(self):
        self.horizontals.get_buffer().set_text('')
        self.verticals.get_buffer().set_text('')

    def set_editable(self, editable):
        self.horizontals.set_editable(editable)
        self.verticals.set_editable(editable)

    def get_horizontals(self):
        horizontals = {}

        for x in self.get_verticals_text().split('\n'):
            for n in range(1, 101):
                if x.startswith(str(n) + ' - '):
                    horizontals[n] = x
                    break

        return horizontals

    def get_verticals(self):
        verticals = {}

        for x in self.get_verticals_text().split('\n'):
            for n in range(1, 101):
                if x.startswith(str(n) + ' - '):
                    verticals[n] = x
                    break

        return verticals

    def set_state(self, state):
        self.state = state
        self.set_editable(self.state == G.State.EDITING)


class LetterBox(Gtk.EventBox):

    __gsignals__ = {
        'select': (GObject.SIGNAL_RUN_FIRST, None, []),
        'letter-changed': (GObject.SIGNAL_RUN_FIRST, None, [str]),
        }

    def __init__(self, letter=None):
        Gtk.EventBox.__init__(self)

        self.letter = letter
        self.final_letter = None
        self.actual_color = G.NORMAL_BOX
        self.space = False
        self.selected = False
        self.editable = True
        self.visible_beginning = False

        self.vbox = Gtk.VBox()
        self.number_label = Gtk.Label()

        self.update()

        self.set_size_request(
            50, G.get_letter_label_size() * 2 + G.get_number_label_size())
        self.number_label.modify_font(
            Pango.FontDescription(str(G.get_number_label_size())))

        self.connect('button-press-event', self._button_press_cb)
        self.connect('enter-notify-event', self._enter_cb)
        self.connect('leave-notify-event', self._leave_cb)

        self.vbox.pack_start(self.number_label, False, False, 0)
        self.add(self.vbox)
        self.show_all()

    def _button_press_cb(self, widget, event):
        if event.button == 1:
            self.emit('select')

    def _enter_cb(self, *args):
        self.modify_bg(Gtk.StateType.NORMAL, G.ENTER_BOX)

    def _leave_cb(self, *args):
        self.modify_bg(Gtk.StateType.NORMAL, self.actual_color)

    def set_letter(self, letter):
        if self.editable or letter == ' ':
            self.letter = letter
            self.emit('letter-changed', letter)
            self.update()

    def set_editable(self, editable):
        self.editable = editable and not self.visible_beginning

    def get_letter(self):
        return self.letter

    def update(self, *args):
        if self.vbox.get_children()[1:]:
            # Fist child is the number label
            self.vbox.remove(self.vbox.get_children()[1])

        if self.letter:
            if self.letter != ' ':
                label = Gtk.Label(self.letter)
                label.modify_font(Pango.FontDescription(
                    'bold %d' % G.get_letter_label_size()))
                self.vbox.add(label)
                self.set_space(False)

            elif self.letter == ' ':
                self.set_space(True)

        else:
            self.actual_color = G.NORMAL_BOX
            self.space = False
            self.editable = True
            self.visible_beginning = False

        self.modify_bg(Gtk.StateType.NORMAL, self.actual_color)
        self.show_all()

    def select(self):
        self.selected = True
        self.actual_color = G.SELECTED_BOX
        self.modify_bg(Gtk.StateType.NORMAL, self.actual_color)

    def unselect(self):
        self.selected = False

        if self.space:
            self.actual_color = G.SPACE_BOX

        elif not self.space:
            self.actual_color = G.NORMAL_BOX

        self.modify_bg(Gtk.StateType.NORMAL, self.actual_color)

    def set_space(self, space):
        self.space = space
        if self.space:
            self.actual_color = G.SPACE_BOX
            self.modify_bg(Gtk.StateType.NORMAL, self.actual_color)

        self.show_all()


class GameArea(Gtk.Grid):

    __gsignals__ = {
        'end-game': (GObject.SIGNAL_RUN_FIRST, None, []),
        'box-selected': (GObject.SIGNAL_RUN_FIRST, None, []),
        }

    def __init__(self):
        Gtk.Grid.__init__(self)

        self.boxes = []
        self.state = G.State.EDITING
        self.selected_box = None
        self.actual_game = None
        self.finally_game = None

        space = 5
        self.set_row_spacing(space)
        self.set_column_spacing(space)
        self.set_margin_left(space)
        self.set_margin_top(space)
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))

        self.new_game()

    def set_state(self, state):
        self.state = state

    def new_game(self):
        while self.boxes:
            box = self.boxes[0]
            self.boxes.remove(box)
            box.destroy()

        rol = 1
        col = 1

        for x in range(1, 101):
            if x % 10 == 1:
                rol += 1
                col = 1

            box = LetterBox('')
            box.number_label.set_label(str(x))
            box.connect('select', self.select_box)
            box.connect('letter-changed', self.game_changed)

            self.attach(box, col, rol, 1, 1)
            self.boxes.append(box)

            col += 1

        self.select_box(self.boxes[0])
        self.show_all()

    def game_changed(self, *args):
        if self.finally_game:
            self.actual_game = self.get_actual_game()

            while self.actual_game.endswith('\n'):
                self.actual_game = self.actual_game[:-1]

            while self.finally_game.endswith('\n'):
                self.finally_game = self.finally_game[:-1]

            if self.actual_game == self.finally_game:
                self.emit('end-game')

    def get_actual_game(self):
        string = ''
        _string = ''
        for x in self.boxes:
            letter = x.get_letter()
            if letter == ' ' or not letter:
                letter = '/'

            if len(string.split('\n')[-1].replace(' ', '')) == 10:
                string += '\n'

            string += letter + ' '

        for x in string.split('\n'):
            if x.endswith(' '):
                x = x[:-1]

            _string += x + '\n'

        if _string[-1] == '\n':
            _string = _string[:-1]

        return _string

    def set_game(self, string):
        self.new_game()
        actual_box = 0

        for line in string.split('\n'):
            for letter in line.split(' '):
                if not letter:
                    continue

                if letter == '/':
                    letter = ' '

                self.boxes[actual_box].set_editable(True)
                self.boxes[actual_box].visible_beginning = False
                self.boxes[actual_box].final_letter = letter
                self.boxes[actual_box].space = False

                if not random.randint(0, 2) or letter == ' ':
                    # One chance in three possibilities
                    self.boxes[actual_box].set_letter(letter)
                    self.boxes[actual_box].visible_beginning = True
                    self.boxes[actual_box].set_editable(False)

                else:
                    self.boxes[actual_box].set_letter('')

                actual_box += 1

        self.finally_game = ''

        for x in string.split('\n'):
            if x.endswith(' '):
                x = x[:-1]

            self.finally_game += x + '\n'

    def show_an_advice(self):
        availables = []

        for x in self.boxes:
            if x.visible_beginning:
                continue

            if not x.editable:
                continue

            if x.letter == x.final_letter:
                continue

            availables.append(x)

        if availables:
            item = random.choice(availables)
            item.visible_beginning = True
            item.set_letter(item.final_letter)
            item.set_editable(False)
            self.select_box(item)

    def select_box(self, box):
        if self.selected_box:
            self.selected_box.unselect()

        self.selected_box = box
        box.select()
        self.emit('box-selected')

    def select_next_box(self):
        if self.selected_box != self.boxes[-1]:
            self.select_box(
                self.boxes[self.boxes.index(self.selected_box) + 1])

        else:
            self.select_box(self.boxes[0])

    def set_letter(self, letter):
        self.selected_box.set_letter(letter)
        self.select_next_box()

    def move_selected_item(self, key):
        selected = self.boxes.index(self.selected_box)
        new_select = 0

        if key == G.KEY_UP:
            new_select = selected - (10 if selected > 9 else -90)

        elif key == G.KEY_DOWN:
            new_select = selected + (10 if selected < 90 else -90)

        elif key == G.KEY_RIGHT:
            new_select = selected - (1 if selected > 0 else -99)

        elif key == G.KEY_LEFT:
            new_select = selected + (1 if selected < 99 else -99)

        self.select_box(self.boxes[new_select])


class WinCanvas(Gtk.VBox):

    __gsignals__ = {
        'new-game': (GObject.SIGNAL_RUN_FIRST, None, [])
        }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        alignment = Gtk.Alignment.new(0.5, 0.5, 0.1, 0.1)
        label = Gtk.Label(_('Congratulations!!!\nYou win!'))
        button_box = Gtk.HButtonBox()
        button = Gtk.Button(_('New game'))
        box = Gtk.VBox()
        button.props.image = Icon(icon_name='new-game',
                                  pixel_size=style.SMALL_ICON_SIZE)

        label.modify_font(
            Pango.FontDescription('Bold %s' % G.get_win_label_size()))
        button_box.set_layout(Gtk.ButtonBoxStyle.CENTER)

        button.connect('clicked', lambda w: self.emit('new-game'))

        button_box.pack_start(button, True, False, 0)
        box.pack_start(label, True, False, 0)
        box.pack_start(button_box, False, True, 0)
        alignment.add(box)
        self.add(alignment)
        self.show_all()


class FileChooser(Gtk.FileChooserDialog):

    def __init__(self, mode, parent):
        if mode == 'save':
            tittle = 'Save game'
            action = Gtk.FileChooserAction.SAVE

        elif mode == 'open':
            tittle = 'Open game'
            action = Gtk.FileChooserAction.OPEN

        Gtk.FileChooserDialog.__init__(self, tittle, parent=parent)

        _filter = Gtk.FileFilter()

        _filter.set_name('CrossWord game')
        _filter.add_pattern('*.cwg')  # CrossWordGame
        self.add_filter(_filter)
        self.set_do_overwrite_confirmation(mode == 'save')
        self.set_select_multiple(False)
        self.set_action(action)
        self.set_modal(True)
        self.set_current_folder(G.CROSSWORDS_DIR)

    def set_buttons(self, _list):
        buttonbox = self.get_children()[0].get_children()[1]

        for x in _list:
            buttonbox.add(x)

    def _destroy(self, widget=None):
        self.destroy()
