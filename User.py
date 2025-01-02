class User:
	def __init__(self, id_user = None, name = None, username = None, age = None, interest = None, count = 0):
		self.id_user = id_user
		self.name = name
		self.username = username
		self.age = age
		self.interest = interest
		self.count = count
	def __str__(self):
		return f"{self.id_user}  {self.name}  {self.username}  {self.age} {self.interest}"
