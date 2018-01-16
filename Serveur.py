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

if(len(sys.argv) == 1):
	print "Erreur : veuillez renseigner le nombre de joueurs en argument."
	sys.exit()
	
nb_joueurs = int(sys.argv[1])
personages = ["Loup Garou", "Villageois"]
players = []
cptJoueurs = 0
sockJoueurs = {}

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
	global effaceur
	global nouveau_message
	global joueur_out

					
					
	#joueur qui effacera les listes globales pour éviter les conflits
	effaceur = "personne"
	
	#établissement de la connexion
	newSocket, address = comSocket.accept()
	p = Protocole(newSocket, '$')
	
	#méthode permettant aux joueurs de communiquer entre eux 
	nouveau_message = ""
	def chat():
		dernier_message = nouveau_message
		while True:
			if(dernier_message != nouveau_message):
				p.envoi("chat", nouveau_message)
				dernier_message = nouveau_message
				if("fin du chat" in nouveau_message):
					break
      
	
	#on crée le joueur correspondant au nom rentré par le client
	#en vérifiant qu'il n'est pas déjà pris par un autre joueur
	nomOK = "deja pris"
	while(nomOK == "deja pris"):
		nomJoueur =  p.rec("pseudo")
		if(nomJoueur in [pl.name for pl in players]):
			p.envoi("nomOK", "deja pris")
			p.rec("validNom")
		else:
			nomOK = "ok"
			p.envoi("nomOK", "ok")
			p.rec("validNom")
	
	sockJoueurs[nomJoueur] = p
	players[cptJoueurs].name = nomJoueur
	perso = players[cptJoueurs].perso
	cptJoueurs += 1
	
	#on attend que tous les clients aient rejoint la partie
	if(cptJoueurs < nb_joueurs):
		while True:
			if(cptJoueurs == nb_joueurs):break
	
	print sockJoueurs
	
	#envoi de la liste de tous les joueurs
	p.envoiListe("joueurs",[pl.name for pl in players])
	p.rec("valid")
	p.envoi("perso", perso)
	
	#création des listes de personnages
	Loups = []
	for pl in players:
		if(pl.perso=="Loup Garou"):
			Loups.append(pl.name)
			
	Villageois = []	
	for pl in players:
		if(pl.perso!="Loup Garou"):
			Villageois.append(pl.name)


	#boucle principale su jeu
	while True:
##################################### Le nuit tombe ###################################
		
		#on nettoie les listes pour la désignation des morts
		if(effaceur == "personne"):
			effaceur = nomJoueur
			del morts[:]

		#on récupère les choix de victime des loups garous
		if(perso=="Loup Garou"):
			p.rec("loups")
			p.envoiListe("listeLoups", Loups)
			p.rec("loupsrecus")
			p.envoiListe("listeVillageois", Villageois)
			
			#le chat pour délibérer
			joueur_out = 0
			nouveau_message = ""
			message = ""
			thread_chat_loup = threading.Thread(target = chat)
			thread_chat_loup.start()
			
			print "loups avant chat : ", Loups
			while True:
				m = p.attente("chat_rec")
				nouveau_message = nomJoueur + " > " + m	
				if ("fin du chat" in m):
					joueur_out += 1
					break	
			print "joueur_out", joueur_out, "len loups : ",len(Loups)
			while True:
				if(joueur_out >= len(Loups)):
					break
			p.envoi("chat_fini","ok")
			
			
			morts.append(p.attente("mort"))
			
		#on attend que tous les loups aient voté	
		while True:
			if(len(morts)==len(Loups)):break
		
		if(effaceur == "personne"):
			effaceur = nomJoueur
			print "c'est ", nomJoueur, "qui efface"
			del votes[:]
		
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


		
		#tous les joueurs restants se parlent pout décider qui tuer
		joueur_out = 0
		nouveau_message = ""
		message = ""
		thread_chat = threading.Thread(target = chat)
		thread_chat.start()
		
		while True:
			m = p.attente("chat_rec")
			nouveau_message = nomJoueur + " > " + m	
			if ("fin du chat" in m):
				joueur_out += 1
				break	
		
		while True:
			if(joueur_out >= len(players)):
				break
		p.envoi("chat_fini","ok")
		
		#reception des votes pour le mort désigné par le conseil du village
		votes.append(p.attente("vote"))
		while True:
			if (len(votes)==len(players)):break

		mortVote = majorite(votes)
		persoMort = ""
		
		#on supprime le mort des listes de joueurs
		for pl in players:
			if (pl.name==mortVote): persoMort = pl.perso
		if(persoMort == "Loup Garou"): Loups.remove(mortVote)
		else:Villageois.remove(mortVote)
		
		print "liste des loups : ",Loups
		#on détermine si le jeu continue ou si il y a des vainqueurs
		issue = "SansVainqueur"
		
		if(not Villageois):
			print "\nLa partie est finie : les loups ont décimé le village!!!"
			issue = "LoupsVainqueurs"
			p.envoiListe("mortVote", [mortVote, persoMort, issue])
			break
		
		if(not Loups):
			print "\nLa partie est finie : les villageois ont décimé les loups garous!!!"
			issue = "VillageVanqueur"
			p.envoiListe("mortVote", [mortVote, persoMort, issue])
			break
			
		p.envoiListe("mortVote", [mortVote, persoMort, issue])
		
		#fin de la fonction threadée pour le joueur mort
		if(majorite(votes)==nomJoueur):
			print "le joueur ",majorite(votes), " est exclu de la partie."
			return 0
		
		effaceur = "personne"
		
			
		
#main code

for joueur in xrange(0,nb_joueurs):
	
	thread=threading.Thread(target=partie)
	thread.start()
	threads.append(thread)

comSocket.close()
