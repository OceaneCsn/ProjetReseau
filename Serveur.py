#! /usr/bin/env python
# -*- coding:utf-8 -*-

from Protocole import *
from Joueur import *
import time
import socket
import threading
import sys
import random as rd 


#initialisation de la partie et de la communication
#def initialisation():
	
nb_joueurs = int(sys.argv[1])
personages = ["Loup Garou", "Villageois"]
players = []
cptJoueurs = 0

#print "\033[31mThis is blue\033[0m"
#ouverture de la communication pour le nombre donne de joueurs
comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
comSocket.bind(('',8000))
comSocket.listen(nb_joueurs)
print "En attente des ", nb_joueurs, " connexions."

#attribution des personnages aux joueurs (la moitie de loups garou)
for i in xrange(0,nb_joueurs):
	perso = "Villageois"
	if(i<int(nb_joueurs/2)):
		perso = personages[0]
	players.append(Joueur("no one", perso))
#on melange aleatoirement les joueurs
rd.shuffle(players)
threads = []
		
#Methode lancee pour chaque client, deroule le jeu
def partie():
	global cptJoueurs
	newSocket, address = comSocket.accept()
	p = Protocole(newSocket, '$')
	nomJoueur =  p.rec("pseudo")
	players[cptJoueurs].name = nomJoueur
	perso = players[cptJoueurs].perso
	cptJoueurs += 1
	if(cptJoueurs < nb_joueurs):
		while True:
			if(cptJoueurs == nb_joueurs):break
			

	#envoi de la liste de tous les joueurs
	p.envoiListe("joueurs",[pl.name for pl in players])
	p.rec("valid")
	p.envoi("perso", perso)
	
	Loups = []
	for pl in players:
		if(pl.perso=="Loup Garou"):
			Loups.append(pl.name)
			
	Villageois = []	
	for pl in players:
		if(pl.perso!="Loup Garou"):
			Villageois.append(pl.name)
	
	global mort
	if(perso=="Loup Garou"):
		p.rec("loups")
		p.envoiListe("listeLoups", Loups)
		p.rec("loupsrecus")
		p.envoiListe("listeVillageois", Villageois)
		mort.append(p.rec("mort"))
		
	while True:
		if(len(mort)==len(Loups)):break
	
	
	players = filter(lambda x: x.name!=mort, players)
	p.envoi("jour", mort)
		#for pl in players:
			#if(pl == nom) players.remove(pl)
		
		

	
	
		

#main code

for joueur in xrange(0,nb_joueurs):
	
	thread=threading.Thread(target=partie)
	thread.start()
	threads.append(thread)


