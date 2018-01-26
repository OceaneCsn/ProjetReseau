import random as rd 

#classe de joueur
#peu fournie, elle est surtout la fondation pour une application plus
#compliquee, et ou un joueur devrait pouvoir effectuer des actions
#plus complexes
#elle pourra etre developpee lors des pistes d'amelioration.

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
