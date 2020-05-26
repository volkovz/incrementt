from keycode import UP, DOWN, LEFT, RIGHT, ENTER, SPACE
from threading import Thread
from blessed import Terminal

import tkinter
import accumulator
import math
import random
import time
import sys

class Theme:
	frame_bg_1 = '#000000'
	
	color1 = '#FFFFFF' # White
	color2 = '#000000' # Black
	color3 = '#FFDE00' # Yellow
	
	font1 = 'Sans'
				 #FG      BG
	themes = {1: (color1, color2),
			  2: (color1, color3),
			  3: (color2, color1),
			  4: (color2, color3),
			  5: (color3, color1),
			  6: (color3, color2),
			 }

class GenericWidget:

	def set_font(self, name =None, size =None, style =None):
		fname, fsize, fstyle = self['font'].split()
		if name: fname = name
		if size: fsize = size
		if style: fstyle = style
		self['font'] = fname, fsize, fstyle

	def set_theme(self, t):
		try:
			fg, bg = Theme.themes[t]
			self['fg'] = fg
			self['bg'] = bg
			widget_name = str(self.__class__).split('.')[-1][0:-2]
			print(f'Widget {widget_name} set to Theme {t}')
		except KeyError:
			raise ValueError(f'invalid theme {t}')

class Frame(tkinter.Frame, GenericWidget):

	def __init__(self, root =None, **config):
		super().__init__(root, **config)
		self['border'] = 1
		self['relief'] = tkinter.RAISED
		self['bg'] = Theme.frame_bg_1
		self.pack()

class Button(tkinter.Button, GenericWidget):

	def __init__(self, root =None, **config):
		super().__init__(root, **config)
		self['font'] = Theme.font1, 7, 'bold'
		self.pack()

class Label(tkinter.Label, GenericWidget):

	def __init__(self, root =None, **config):
		super().__init__(root, **config)
		self['font'] = Theme.font1, 7, 'bold'
		self.pack() 

class MainWindow:

	def __init__(self, root =None):
		self.acc = accumulator.Accumulator()
		self.time = accumulator.Time()
		self.root = root

		self.upper_frame = Frame(self.root) # UPPER FRAME
		self.upper_frame.pack(side = tkinter.TOP, fill = 'x')
		self.lower_frame = Frame(self.root) # LOWER FRAME
		self.lower_frame.pack(side = tkinter.BOTTOM, fill = 'x')

		self.gen_frame = Frame(self.upper_frame)
		self.gen_frame.pack(side = tkinter.LEFT)

		self.gen = Button(self.gen_frame)
		self.gen['text'] = 'E!'
		self.gen.set_font(name = 'sans', size = 50)
		self.gen.set_theme(6)
		self.gen['command'] = self.change_theme
		self.gen['command'] = self.on_click
		self.gen.pack(side = tkinter.TOP, fill = 'x', padx = 2)

		self.info_frame = Frame(self.upper_frame)
		self.info_frame['bg'] = Theme.color3
		self.info_frame.pack(side = tkinter.RIGHT, fill = 'both', expand = True)

		info_theme = 4
		info_relief = tkinter.GROOVE
		info_border = 1
		info_font = Theme.font1, 8, 'bold' 

		self.perclick = Label(self.info_frame)
		self.perclick['text'] = f'Electricity per click: {self.acc.output():.2f}E'
		self.perclick['relief'] = info_relief
		self.perclick['border'] = info_border
		self.perclick.set_theme(info_theme)
		self.perclick.set_font(name = info_font[0], size = info_font[1], style = info_font[2])
		self.perclick.pack(side = tkinter.TOP, anchor = 'w', fill = 'y', expand = True)

		self.persec = Label(self.info_frame)
		self.persec['text'] = f'Electricity per second: {self.acc.incrementor.output() * 4:.2f}E'
		self.persec['relief'] = info_relief
		self.persec['border'] = info_border
		self.persec.set_theme(info_theme)
		self.persec.set_font(name = info_font[0], size = info_font[1], style = info_font[2])
		self.persec.pack(side = tkinter.TOP, anchor = 'w', fill = 'y', expand = True)

		self.accumulated = Label(self.info_frame)
		self.accumulated['text'] = f'Accumulated Electricity: {self.acc.amount:.2f}E'
		self.accumulated['relief'] = info_relief
		self.accumulated['border'] = info_border
		self.accumulated.set_font(name = info_font[0], size = info_font[1], style = info_font[2])
		self.accumulated.set_theme(info_theme)
		self.accumulated.pack(side = tkinter.TOP, anchor = 'w', fill = 'y', expand = True)

	def change_theme(self):
		theme = random.randint(1, 6)
		self.perclick.set_theme(theme)
		self.persec.set_theme(theme)
		self.accumulated.set_theme(theme)

	def update_header(self):

	def on_click

root = tkinter.Tk()
main = MainWindow(root)
root.mainloop()