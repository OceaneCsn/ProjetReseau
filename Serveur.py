
from Protocole import *
from Joueur import *
import time
import socket
import threading
import sys
import random as rd 

#initialisation de la partie
nb_joueurs = int(sys.argv[1])
personages = ["Loup garou", "Villageois"]
players = []

for i in xrange(0,nb_joueurs):
	perso = "Villageois"
	if(i<int(nb_joueurs/2)):
		perso = personages[0]
	players.append(Joueur("no one", perso))
	
	
def partie():
	global cptJoueurs
	newSocket, address = comSocket.accept()
	p = Protocole(newSocket, '$')
	nomJoueur =  p.rec("pseudo")
	
	players[cptJoueurs].name = nomJoueur
	cptJoueurs += 1
	if(cptJoueurs < nb_joueurs):
		while True:
			if(cptJoueurs == nb_joueurs):break
			
	
	#envoi de la liste de tous les joueurs
	p.envoiListe("joueurs",[p.name for p in players])


#on melange aleatoirement les joueurs
rd.shuffle(players)
cptJoueurs = 0
threads = []

#ouverture de la communication
comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
comSocket.bind(('',8000))
comSocket.listen(nb_joueurs)

for joueur in xrange(0,nb_joueurs):
	
	thread=threading.Thread(target=partie)
	thread.start()
	threads.append(thread)


