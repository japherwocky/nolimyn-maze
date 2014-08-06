class Prompt:
	default = '<%(hp)s/%(maxhp)shp %(mp)s/%(maxmp)smp %(mv)s/%(maxmv)smv %(atkq)s %(atk)s>'
	def __init__(self, ch, string=False):
		self.string = string if string else self.default
		self.ch = ch

	def __str__(self):
		return self.string

	def __call__(self, string=False):
		if not string: self.ch.Write(self.string % self.ch.body.stats)
		else: self.ch.Write(string % self.ch.body.stats) #maybe we call a different method for this?

#TODO: customizable prompts :)
