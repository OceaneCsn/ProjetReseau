import random as rd 

class Joueur :
	
	def __init__(self, name, personage):
		
		self.name = name
		self.perso = personage
		self.state = "vivant"
	
	def __eq__(self,nom):
		if (nom == self.name):
			return True 
		else: 
			return False
