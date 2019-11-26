class bid:
	#Face- the resulting number on the die (1-6)
	#quantity- predicted count of said face (max 15 with 3 players all rolling the same number on all of their dice)
	def __init__(self, face, quantity):
		self.face = face
		self.quantity = quantity

	def toString(self):
		return "BID: more than %d %ds\n"  %(self.quantity, self.face)