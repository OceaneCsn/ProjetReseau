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
verrou = threading.Lock() 


morts = []
votes = []

def majorite(votes):
	scores = dict()
	for joueur in votes:
		if (joueur not in scores.keys()):scores[joueur] = 0
		scores[joueur] += 1
	return max(scores, key=scores.get)
	
	
		
#Methode lancee pour chaque client, deroule le jeu
def partie():
	
	#definition des variables globales
	global cptJoueurs
	global verrou
	global morts
	global votes
	
	newSocket, address = comSocket.accept()
	p = Protocole(newSocket, '$')
	nomJoueur =  p.rec("pseudo")
	players[cptJoueurs].name = nomJoueur
	perso = players[cptJoueurs].perso
	cptJoueurs += 1
	
	#on attend que tous les clients aient rejoint la partie
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

	while True:
##################################### Le nuit tombe ###################################

		#récupère les choix de victime des loups garous
		
		if(perso=="Loup Garou"):
			p.rec("loups")
			p.envoiListe("listeLoups", Loups)
			p.rec("loupsrecus")
			p.envoiListe("listeVillageois", Villageois)
			morts.append(p.attente("mort"))
			
		#on attend que tous les loups aient voté	
		while True:
			if(len(morts)==len(Loups)):break
		
		#on supprime la personne tuée de la liste des joueurs
		for pl in players:
			if(pl.name == majorite(morts)):players.remove(pl)
		Villageois.remove(majorite(morts))
		
		#on stoppe la boucle du  jeu si il ne reste plus qu'un type de personage
		if(not Villageois):
			print "\nLa partie est finie : les loups ont décimé le village!!!"
			p.envoiListe("jour", [majorite(morts),"LoupsVainqueurs"])
			break
		
		if(not Loups):
			print "\nLa partie est finie : les villageois ont décimé les loups garous!!!"
			p.envoiListe("jour", [majorite(morts),"VillageVainqueur"])
			break
		
		#sinon, on envoie la personne tuée et le jeu continue
		p.envoiListe("jour", [majorite(morts), "SansVainqueur"])
			
		
		#arrete la fonction threadée pour le joueur ayant été tué
		if(majorite(morts)==nomJoueur):
			print "le joueur ",majorite(morts), " est exclu de la partie."
			return 0
		
		
	###################################### Le jour se lève #################################


		#reception des votes pour le mort désigné par le conseil du village
		
		votes = []
		print "avantWhile pour ", nomJoueur
		while(len(votes)<len(players)):
			#verrou?
			verrou.acquire()
			votes.append(p.attente("vote"))
			verrou.release()
			print " vote de ", nomJoueur," taille de votes :", len(votes)
		
		print "je sors de l'attente des votes"
		mortVote = majorite(votes)
		persoMort = ""
		for pl in players:
			if (pl.name==mortVote): persoMort = pl.perso
		if(persoMort == "Loup Garou"): Loups.remove(mortVote)
		else:Villegeois.remove(mortVote)
		
		p.envoiListe("mortVote", [mortVote,persoMort])
		


#main code

for joueur in xrange(0,nb_joueurs):
	
	thread=threading.Thread(target=partie)
	thread.start()
	threads.append(thread)

comSocket.close()
