class CostError(ValueError): pass
#506 861 867 53
class Incrementor:
	
	def __init__(self):
		self.base = 0.0075
		self.bonus = 0
		
		self.base_cost = 5
		self.cost_ratio = 1.5
		self.amount = 0

		self.upgrade_rate = 0.75
		self.upgrade_base_cost = 10
		self.upgrade_cost_ratio = 1.3
		self.upgrade_level = 0

	def output(self):
		bonus =self.upgrade_rate * self.upgrade_level
		return (self.base + (self.base * bonus)) * self.amount

	def get_cost(self):
		return self.base_cost * (self.cost_ratio ** self.amount)

	def get_upgrade_cost(self):
		return self.upgrade_base_cost * (self.upgrade_cost_ratio ** self.upgrade_level)

class Accumulator:
	
	def __init__(self):
		self.amount = 0
		self.capacity = 100
		self.clicks = 0
		self.incrementor = Incrementor()
		
		# Per click generation
		self.pc = 1
		self.pc_bonus = 0.25
		self.pc_base_cost = 10
		self.pc_cost_ratio = 1.23
		self.pc_upgrade_level = 0
		
	def output(self):
		return self.pc + (self.pc_bonus * self.pc_bonus * self.pc * self.pc_upgrade_level)

	def generate_per_click(self):
		self.amount += self.output()
		self.clicks += 1
	
	def generate_per_tick(self):
		self.amount += self.incrementor.output()
	
	def get_incrementor(self):
		cost = self.incrementor.get_cost()
		if self.amount >= cost:
			self.incrementor.amount += 1
			self.amount -= cost
		else:
			raise CostError('You need %.2fE to buy another incrementor' % cost)
	
	def upgrade_incrementor(self):
		cost = self.incrementor.get_upgrade_cost()
		if self.amount >= cost:
			self.incrementor.upgrade_level += 1
			self.amount -= cost
		else:
			raise CostError('You need %.2fE to buy another level of this upgrade' % cost)

	def improve_click(self):
		cost = self.pc_base_cost * (self.pc_cost_ratio ** self.pc_upgrade_level)
		if self.amount >= cost:
			self.pc_upgrade_level += 1
			self.amount -= cost
		else:
			raise CostError('You need %.2fE to buy this upgrade' % cost)

class Time:
	TICK = 4
	def __init__(self):
		self.tick = 0
		self.seconds = 0
		self.days = 0
		self.years = 0
		self.cycles = 0

	def increase(self):
		self.tick += 1
		self.days = self.tick  // 10
		self.years = self.days // 365
		self.cycles = self.years // 4

	def get(self):
		return f'Day {self.days % 365} Year {self.years} Cycle {self.cycles}'
