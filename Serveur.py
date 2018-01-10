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
	global chat_is_over

					
					
	#joueur qui effacera les listes globales pour éviter les conflits
	effaceur = "personne"
	
	#établissement de la connexion
	newSocket, address = comSocket.accept()
	p = Protocole(newSocket, '$')
	
	
	
	chat_is_over=0
	nouveau_message = ""
	def chat():
		print "je passe dans la méthode chat!"
		dernier_message = nouveau_message
		while True:
			#print "dm : ", dernier_message, "nm : ", nouveau_message
			if(dernier_message != nouveau_message):
				print "nouveau message a changé chez", nomJoueur, "!\n"
				#for prot in sockJoueurs.values():
				p.envoi("chat", nouveau_message)
				print "envoi en broadcast ", nouveau_message
				dernier_message = nouveau_message
				if("fin du chat" in nouveau_message):
					chat_is_over = 1
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
			
			#faire le chat pour délibérer!
			
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


		#reception des votes pour le mort désigné par le conseil du village
		
		
		chat_is_over = 0
		nouveau_message = ""
		message = ""
		thread_chat = threading.Thread(target = chat)
		thread_chat.start()
		while (chat_is_over !=1):
			m = p.attente("chat_rec")
			nouveau_message = nomJoueur + " > " + m
			print "j'ai reçu ", m
			#p.envoi("chat_envoi", nouveau_message)
			#print "j'envoie au client initiateur : ", nouveau_message
			
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
			print "le joueur ",majorite(morts), " est exclu de la partie."
			return 0
		
		effaceur = "personne"
		
			
		
#main code

for joueur in xrange(0,nb_joueurs):
	
	thread=threading.Thread(target=partie)
	thread.start()
	threads.append(thread)

comSocket.close()
