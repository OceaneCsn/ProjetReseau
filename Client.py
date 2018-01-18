#! /usr/bin/env python
# -*- coding:utf-8 -*-

from socket import *
from Protocole import *
from Joueur import *
import sys
import threading
import time
import signal

if(len(sys.argv) == 1):
	print "Erreur : veuillez renseigner l'adresse serveur auquel vous connecter pour la partie en argument."
	sys.exit()
	
#recupere l'adresse du serveur en parametres

adresse_serveur = str(sys.argv[1])
#print "Demande de connexion au serveur a l'adresse ", adresse_serveur, "."
socket = socket(AF_INET, SOCK_STREAM)

try:
	socket.connect((adresse_serveur,8000))
	print "Connecté au serveur à l'adresse ", adresse_serveur, ".\n"
except error:
	print "Echec de la connection. Etes vous sûr s'avoir lancé le serveur?\nFin du programme."
	sys.exit(1)

#creation du protocole de communication avec le serveur
p = Protocole(socket, '$')


print "Bienvenue dans votre partie de Loup Garou!\n "
time.sleep(1)
print "Veuillez rentrer votre pseudo pour la partie :\n"

#Saisie d'un pseudo disponible pour la partie
nomOK = "deja pris"
while(nomOK == "deja pris"):
	pseudo = str(raw_input())
	p.envoi("pseudo", pseudo)
	nomOK = p.rec("nomOK")
	if(nomOK == "deja pris"):
		print "Ce nom est déjà pris, veuillez en saisir un autre."
	p.envoi("validNom", "")


print "\nNous attendons que tous les joueurs regagnent la partie..."
joueurs = p.attenteListe("joueurs")

print "Tout le monde est la : ",joueurs
p.envoi("valid", '')
perso = p.rec("perso")

time.sleep(1)

print "Vous êtes un ",perso,".\n \n"
time.sleep(2)

#methode permettant d'attendre les messages reçus des autres joueurs lors du chat
def chat():
	while True:
		mess = p.attente("chat")
		if "fin du chat" in mess:
			leaver = mess.split('>')[0].split(' ')[0]
			if(leaver != pseudo):
				print "\n", leaver , "a quitté le chat.\n"
			break
		print "\n", mess, "\n"
		
#boucle principale du jeu
while True:

	print "\033[34m--------------------------------------------------------------------"
	print "---------------    La nuit tombe sur le village    -----------------"
	print "--------------------------------------------------------------------\n \n\033[0m"
	time.sleep(2)

	#methode décrivant le crime des loups garous pendant la nuit
	def NuitLoupGarou(p):
		p.envoi("loups",'')
		loups = p.recListe("listeLoups")
		print "Les loups garous s'éveillent et se reconnaissent. Il s'agit de : ", loups
		p.envoi("loupsreçus",'')
		vill = p.recListe("listeVillageois")
		print "Vous pouvez tuer auc choix: ", 
		for v in vill:
			print "_ ",v
		time.sleep(2)

		print "\033[36m\n\n---------------------------------------------------------------\n Début du chat \n\033[0m"
		print "Quittez le une fois la décision prise en tapant : fin du chat"
		#chat de délibération
		thread_chat_loup = threading.Thread(target = chat)
		thread_chat_loup.start()
		while True:
			message = str(raw_input())
			p.envoi("chat_rec", message)
			if "fin du chat" in message:
				break
		print "\033[36m\n\nFin du chat \n-----------------------------------------------------------------\033[0m"
		
		print "Attendons que les autres joueurs soient sortis du chat...\n"
		
		p.attente("chat_fini")
		
		print "Entrez le nom de la victime choisie"
		mort = str(raw_input())
		while (mort not in vill):
			print "Veuillez rentrer le nom d'une des personnes pouvant être tuée dans la liste ci dessus."
			mort = str(raw_input())
		p.envoi("mort", mort)
		
		
	#print'\nLa nuit tombe sur le village...'
	if(perso == "Loup Garou"):
		NuitLoupGarou(p)
		print "Les autres loups n'ont pas encore voté, attendons les!"
		infoMort = p.attenteListe("jour")

	#le joueur s'endort pendant que les loups choisissent une victime
	if(perso == "Villageois"):
		print "Vous dormez profondément."
		infoMort = p.attenteListe("jour")
		
	mort = infoMort[0]
	keepPlaying = infoMort[1]
	
	
	#on supprime le joueur tué
	for pl in joueurs:
		if(pl == mort):joueurs.remove(pl)
			

	print "\033[33m\n \n--------------------------------------------------------------------"
	print "---------------------    Le jour se lève    ------------------------"
	print "--------------------------------------------------------------------\n \n\033[0m"

		
	print "\nCette nuit, ",mort," a été dévoré(e)...\n"
	time.sleep(2)

	if(keepPlaying != "SansVainqueur"):
		if(keepPlaying == "LoupsVainqueurs"):
			print "\nLa partie est finie : les loups ont décimé le village!!!"
			break
		else:
			print "\nLa partie est finie : les villageois ont décimé les loups!!!"
			break


	#Fin du jeu pour le joueur tué par le(s) loup(s).
	if(mort==pseudo):
		print "Votre aventure s'arrête ici... \n"
		break

	else:
		print "Le village doit se mettre d'accord. La majorité du vote l'emportera.\n Parmis les joueurs ci dessous, lequel souhaitez vous voir mort?" 
		for j in joueurs:
			print "- ",j
		time.sleep(2)

		print "\033[36m\n\n---------------------------------------------------------------\n Début du chat \n\033[0m"
		print "Quittez le une fois la décision prise en tapant : fin du chat"
		#chat de délibération
		thread_chat = threading.Thread(target = chat)
		thread_chat.start()
		while True:
			message = str(raw_input())
			p.envoi("chat_rec", message)
			if "fin du chat" in message:
				break
		print "\033[36m\nFin du chat \n-----------------------------------------------------------------\033[0m"
		
		print "Attendons que les autres joueurs soient sortis du chat...\n"
		
		p.attente("chat_fini")
		
		print "Rentrez maintenant le nom de la personne que vous avez choisi de tuer : "
		vote = str(raw_input())
		while (vote not in joueurs):
			print "Veuillez rentrer le nom d'une des personnes pouvant être tuée dans la liste ci dessus."
			vote = str(raw_input())
		p.envoi("vote", vote)
		
		print "Nous attendons que tout le monde ait voté.\n "
		mortVote = p.attenteListe("mortVote")
		
		print "Le village a décidé de tuer ", mortVote[0],". Il s'agissait d'un ", mortVote[1]," !"
		time.sleep(1)

		keepPlaying = mortVote[2]
			
		if(keepPlaying != "SansVainqueur"):
			if(keepPlaying == "LoupsVainqueurs"):
				print "\nLa partie est finie : les loups ont décimé le village!!!"
				break
			else:
				print "\nLa partie est finie : les villageois ont décimé les loups!!!"
				break

		if(mortVote[0]==pseudo):
			print "Votre aventure s'arrête ici... \n"
			break
			
			
print " Vous allez être déconnecté du serveur. A bientôt pour une nouvelle partie!"
socket.close()
#print "\033[31mThis is blue\033[0m"


	






