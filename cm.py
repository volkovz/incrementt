from __future__ import print_function
import blessed
import os
import random
import time
import datetime
import shelve

from keycode import ENTER, LEFT, RIGHT, UP, DOWN
from threading import Thread

term = blessed.Terminal()
print(term.home+term.clear)

class Theme:
	
	accumulator_header = term.black_on_white
	accumulator_capacity = term.black_on_cadetblue4
	accumulator_sec = term.cadetblue4
	
	warning = term.blink_white_on_red
	
	selected_menu_entry = term.black_on_cadetblue4
	unselected_menu_entry = accumulator_sec
	
	entry_name = accumulator_header
	entry_description = term.cadetblue4_on_grey5
	item_cost = term.grey30
	
	selected_upgrade_entry = term.bold_white_on_darkslategrey
	unselected_upgrade_entry = term.darkslategrey
	
	upgrade_description = term.darkslategrey
	
	resource_tag = accumulator_capacity
	resource_value = accumulator_sec
	
	log_value = accumulator_sec
	
	buy_incrementor_label = 'BI'
	upgrade_incrementor_label = 'UI'
	expand_limits_label = 'EL'
	generate_ef_label = 'G.EF'
	ef_craftr_label = 'EF.C'
	
	
	@staticmethod
	def format_float(value):
		return '%.2f' % value

class GenericOperator:
	
	def __init__(self, amount, base_cost, cost_ratio, upgrade_base_cost, upgrade_cost_ratio):
		self.amount = amount
		self.base_cost = base_cost
		self.cost_ratio = cost_ratio
		self.upgrade_base_cost = upgrade_base_cost
		self.upgrade_cost_ratio = upgrade_cost_ratio
		self.upgrade_level = 0
		
	def __repr__(self):
		return  self.name
	
	def get_cost(self):
		return self.base_cost * (self.cost_ratio ** self.amount)
	
	def get_upgrade_cost(self):
		return self.upgrade_base_cost * (self.upgrade_cost_ratio ** self.upgrade_level)
		
class Accumulator:
	
	def __init__(self, menu):		
		self.amount = 0
		self.menu = menu		
		self.capacity = 25
		self.ef = ExpandingForce(self.menu)
		self.inc = Incrementor()
		self.mul = Multiplicator()
		
	def buy_incrementor(self):
		cost = self.inc.get_cost()
		if self.amount >= cost:
			self.inc.amount += 1
			self.amount -= cost
			self.inc.capacity = 5 * self.inc.amount
			self.menu.log = '+1 Incrementor'
		else:
			self.menu.log = f'You need {Theme.format_float(cost)}E to get another Incrementor'
	
	def upgrade_incrementor(self):
		cost = self.inc.get_upgrade_cost()
		if self.amount >= cost:
			if not self.inc.power:
				self.inc.power = 0.25
			self.inc.upgrade_level += 1
			self.amount -= cost
			self.menu.log = '+1 Tweak Level'
		else:
			self.menu.log = f'You need {Theme.format_float(cost)}E to upgrade the incrementor again'		
	
	def expand_limits(self):
		ef = self.ef.amount
		cost = self.ef.le_ratio * self.capacity
		if ef >= cost:
			self.capacity *= self.ef.expansion_rate
			self.ef.amount -= cost
			self.ef.residual_electricity += 1
			self.menu.log = 'Accumulator capacity expanded'
		else:
			self.menu.log = f'You need {Theme.format_float(cost)}EF to expand the current limits'
	
	def generate_ef(self):
		a = self.amount
		self.ef.amount += a * self.ef.craft_ratio
		self.amount -= a
				
	def run(self):
		if self.amount < self.capacity:
			self.menu.full_accumulator = ''
			self.amount += self.inc.output()
			if self.amount > self.capacity:
				self.amount = self.capacity
		else:
			self.menu.full_accumulator = '!!!'
			
	def __str__(self):
		return term.black_on_cadetblue4(term.center(str(self.amount)))

class ExpandingForce:
	
	def __init__(self, menu):
		self.amount = 0
		self.residual_electricity = 0
		self.expansion_rate = 1.25
		self.craft_ratio = 0.25
		self.cr_level = 0
		self.le_ratio = 2.5
		self.menu = menu
	
	def efcraft_ratio_cost(self):
		return 1 * (1.5 **  self.cr_level)
	
	def improve_ef_craft(self):
		cost = self.efcraft_ratio_cost()
		if self.residual_electricity >= cost:
			self.craft_ratio += 0.06
			self.cr_level += 1
			self.residual_electricity -= cost
			#self.menu.log = f'{cost} {self.residual_electricity}'
			self.menu.log = '+6%% EF craft ratio'
		else:
			self.menu.log = f'You need {Theme.format_float(cost)}RE to buy another level of this upgrade'
			
class Incrementor(GenericOperator):
	
	def __init__(self):
		super().__init__(1, 2, 1.35, 0.250, 1.45) #AMOUNT BASE_COST COST_RATIO UPGRADE_BASE_COST UPGRADE_COST_RATIO
		self.name = 'Incrementor'
		self.base = 0.0085
		self.power = 0
		self.storag = 0
		self.capacity = 5 * self.amount
		
	def output(self):
		power = 1 + (self.power * self.upgrade_level)
		return (self.base * self.amount) * power
	
class Multiplicator(GenericOperator):
	
	def __init__(self):
		self.name = 'Multiplicator'
		self.amount = 1
		self.base = 10000#1.0/10**5
		self.bonus = 0
		self.base
	#	super().__init__('Multiplicator', 1, 1/100000.0, 0, 2, 1.5)
	
	def get_mod(self):
		base = self.base + (self.base * (1 + self.power))
		return base * self.amount

class Menu:
	
	def __init__(self):
		self.entries = ['BI', 'UI']
		self.uentries = ['Incrementor Internal Storage']
		self.uindex = 0
		self.index = 0
		self.log = ''
		self.full_accumulator = ''
		
		self.entry_description = ''
		self.item_cost = ''
		self.entry_name = ''
		
		self.upgrade_description = ''
		self.upgrade_cost = ''
		
	def __getitem__(self, index):
		return self.entries[index]
	
	def append(self, value):
		self.entries.append(value)	
	
	def new_entry(self, value, condition, pos =-1):
		if condition and value not in self:
			if pos == -1:
				self.append(value)
			else:
				self.entries.insert(pos, value)
	
	def get_selected(self):
		return self.entries[self.index]
	
	def get_selected_upgrade(self):
		return self.uentries[self.uindex]
	
	def upper(self):
		if len(self.uentries) > 0:
			self.uindex = (self.uindex - 1) % (len(self.uentries))
	
	def lower(self):
		if len(self.uentries) > 0:
			self.uindex = (self.uindex +1) % (len(self.uentries))
			
	def next(self):
		self.index = (self.index + 1) % len(self.entries)
		
	def previous(self):
		self.index = (self.index - 1) % len(self.entries)
	
	def set_description(self, acc, upgrade =False):
		selected = self.get_selected()
		selected_upgrade = self.get_selected_upgrade()
		format_float = Theme.format_float
		cost = 'Cost: %s%s'
		
		if selected == 'BI':
			self.entry_name = 'Buy Incrementor'
			self.entry_description = 'Every Incrementor increases the amount of Electricity generated by the Accumulator'
			self.item_cost = cost  % (format_float(acc.inc.get_cost()), 'E')
		
		elif selected == Theme.buy_incrementor_label:
			self.entry_name = 'Upgrade Incrementor'
			self.entry_description = 'Upgrade Incrementor power to generate more Electricty per second' 
			self.item_cost = cost % (format_float(acc.inc.get_upgrade_cost()), 'E')
		
		elif selected == Theme.upgrade_incrementor_label:
			self.entry_name = 'Expand Limits'
			self.entry_description = 'Use Expanding Force to expand the Accumulator beyond its current limit'
			self.item_cost = '%s // This process will also generate Residual Electricity' % (cost % (format_float(acc.ef.le_ratio * acc.capacity), 'EF'))
		
		elif selected == Theme.generate_ef_label:
			self.entry_name = 'Generate Expanding Force'
			self.entry_description = 'Craft Expanding Force using Electricity'
			self.item_cost = '1E crafts %sEF' % (format_float(1 * acc.ef.craft_ratio))
		
		elif selected == Theme.ef_craftr_label:
			self.entry_name = 'EF Craft Effectiviness'
			self.entry_description = 'Improve Expanding Force craft ratio'
			self.item_cost = ''
		
		if selected_upgrade == 'Incrementor Internal Storage':
			self.upgrade_description = 'Incrementors will now have a small space to store E when the Accumulator reach its limit'
			self.upgrade_cost = ''
			
def key_detecting(menu, acc):
	with term.cbreak():
		while True:
			key = term.inkey()
			if key.is_sequence:
				if key.code == LEFT:
					menu.previous()
				elif key.code == RIGHT:
					menu.next()
				elif key.code == ENTER:
					selected = menu.get_selected()
					if selected == 'BI':
						acc.buy_incrementor()
					elif selected == 'UI':
						acc.upgrade_incrementor()
					elif selected == 'EL':
						acc.expand_limits()
					elif selected == 'G.EF':
						acc.generate_ef()
					elif selected == 'EF.C':
						acc.ef.improve_ef_craft()
				elif key.code == UP:
					menu.upper()
				elif key.code == DOWN:
					menu.lower()

def run_generator(acc, menu, clock):
	runtime = 0
	while True:
		
		menu.new_entry(Theme.expand_limits_label, get_pct(acc.amount, acc.capacity) >= 95)
		menu.new_entry(Theme.generate_ef_label, acc.inc.amount >= 5)
		menu.new_entry(Theme.ef_craftr_label, acc.ef.residual_electricity >= 1)
		
		acc.run()
		clock.tick += 1
		menu.set_description(acc)
		time.sleep(1/clock.TICK)			

class Clock:
	TICK = 4
	
	def __init__(self):
		self.tick = 0
		self.seconds = self.tick / 4
		self.minutes = self.seconds / 60
		self.hours = self.seconds / 60
		self.days = self.hours / 24
	
	def get_time(self):
		return datetime.deltatime(self.seconds)
	
def print_pair(x, y):
	x1 = Theme.resource_tag(' %s ' % x)
	if x in ('EF', 'RE'):
		y = Theme.resource_value(' %s ' %Theme.format_float(y))
	else:
		y = Theme.resource_value(' %s ' % y)
	return x1 + y

def get_pct(fraction, total):
	pct = (fraction / total) * 100
	return pct

def pct_bar(fraction, total):
	pct = get_pct(fraction, total)
	if pct < 25:
		color = term.on_yellow
	elif 25 <= pct < 50:
		color = term.on_orange
	elif 50 <= pct < 75:
		color = term.on_orangered
	elif pct >= 75:
		color = term.on_red
	w = term.width / 100
	return (color(' ') * int(pct*w))

def get_location(row):
	return term.width - (term.width - row)

def format_time(s):
	t = str(datetime.timedelta(seconds=round(s))).split(':')
	f = 'h', 'm', 's'
	return ' '.join([t[x]+f[x] for x in range(len(t)) if t[x] != '0'])
	
def run():
	clock = Clock()
	menu = Menu()
	acc = Accumulator(menu)
	kb_detecting =Thread(target = key_detecting, args = (menu, acc))
	generator = Thread(target = run_generator, args = (acc, menu, clock))
	kb_detecting.start()
	generator.start()
	
	while True:
		H = term.height
		
		# Header
		with term.location(y = get_location(0)):
			acc_pct = get_pct(acc.amount, acc.capacity)
			acc_bar = pct_bar(acc.amount, acc.capacity) 
			outsec= acc.inc.output() * 4 # Incrementor output/sec
		
			#acc.inc.base = 100
			e_per_sec = f'running @ +{Theme.format_float(outsec)} Electricty per second'
			e_storage = f'Accumulator capacity: {Theme.format_float(acc.amount)}E / {Theme.format_float(acc.capacity)}E'
			header = f' Accumulator {e_per_sec}'
		
			print(Theme.accumulator_header(term.center(header))) #1
			
			if acc_pct == 100.00:
				print(Theme.warning(term.center('!! Accumulator reached its full capacity !!'))) #2
			else:
				print(acc_bar) #2
			
			filltime = acc.capacity / outsec
			print(Theme.accumulator_capacity(term.center(e_storage))) #3
		
		# Resources
		with term.location(y = get_location(4)):
			res = [print_pair('INC', acc.inc.amount),
				   print_pair('UPG', acc.inc.upgrade_level),
				  ]
			
			if (acc.inc.output() * 4) >= 0.50: res.append(print_pair('EF', acc.ef.amount))
			if Theme.generate_ef_label in menu: res.append(print_pair('RE', acc.ef.residual_electricity))
			print(term.center(' '.join(res))) #4
		
		# Name, description and cost of menu entry
		with term.location(y = get_location(8)):
			print(Theme.entry_name(term.center(menu.entry_name)))
			print(Theme.entry_description(term.center(menu.entry_description)))
			print(Theme.item_cost(term.center(menu.item_cost)))
		
		# Menu listing
		with term.location(y = get_location(12)):
			m = []
			for entry in menu:
				if entry == menu.get_selected():
					m.append(Theme.selected_menu_entry(' ' + entry + ' '))
				else:
					m.append(Theme.unselected_menu_entry(' ' + entry + ' '))
			print(term.center(''.join(m)))

		# Log
		with term.location(y = get_location(15)):
			print(Theme.log_value(term.center(menu.log)))
		
		time.sleep(0.09)
		os.system('clear')
	
with term.hidden_cursor():
	run()

