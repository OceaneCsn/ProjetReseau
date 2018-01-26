#! /usr/bin/env python
# -*- coding:utf-8 -*-

from socket import *
from Protocole import *
from Joueur import *
import sys
import threading
import time
import signal


#verifie qu'une adresse a bien été entrée en argument, sinon, quitte le programme.
if(len(sys.argv) == 1):
	print "Erreur : veuillez renseigner l'adresse serveur auquel vous connecter pour la partie en argument."
	sys.exit()
	
#recupere l'adresse du serveur en parametres
adresse_serveur = str(sys.argv[1])

socket = socket(AF_INET, SOCK_STREAM)

#connection au serveur 
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

print "Tout le monde est là! Vous jouez avec :"
for j in joueurs:
	print "- ",j
p.envoi("valid", '')
perso = p.rec("perso")

time.sleep(1)

print "\nVous êtes un ",perso,".\n \n"
time.sleep(2)

#methode permettant d'attendre les messages reçus des autres joueurs lors du chat
#(sera utilisée plus tard dans le code)
def chat():
	while True:
		#reception du message issu d'un autre thread
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

	#methode organisant le crime des loups garous pendant la nuit...
	def NuitLoupGarou(p):
		p.envoi("loups",'')
		loups = p.recListe("listeLoups")
		p.envoi("loupsreçus",'')
		vill = p.recListe("listeVillageois")
		if(len(loups) > 1):
			print "Les loups garous s'éveillent et se reconnaissent. Il s'agit de :\n",
			for l in loups:
				print "- ",l
			print "Vous pouvez tuer au choix:\n", 
			for v in vill:
				print "- ",v
			time.sleep(2)
			
			#chat de délibération
			print "\033[36m\n\n---------------------------------------------------------------\n Début du chat entre loups garous\n\033[0m"
			print "Quittez le une fois la décision prise en tapant : fin du chat"
			thread_chat_loup = threading.Thread(target = chat)
			thread_chat_loup.start()
			while True:
				message = str(raw_input())
				p.envoi("chat_rec", message)
				if "fin du chat" in message:
					break
			print "\033[36m\n\n Fin du chat \n-----------------------------------------------------------------\033[0m"
			
			print "Très bien! Attendons simplement que les autres joueurs soient sortis du chat.\n"
			
			p.attente("chat_fini")
			
			print "A l'issue de vos délibérations, veuillez entrez le nom de la victime choisie.\n"
			mort = str(raw_input())
			
		else:
			print "Vous êtes le seul loup garou. Qui décidez vous d'égroger cette nuit?\n" 
			for v in vill:
				print "- ",v
			mort = str(raw_input())
			
			
		while (mort not in vill):
			print "Veuillez rentrer le nom d'une des personnes pouvant être tuée dans la liste ci dessus."
			mort = str(raw_input())
		p.envoi("mort", mort)
		

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
		print "\033[91m\n \n--------------------------------------------------------------------"
		print "------------------   Votre aventure s'arrête ici...  --------------"
		print "--------------------------------------------------------------------\n \n\033[0m"
		
		break

	else:
		print "Le village doit se mettre d'accord. \nParmis les joueurs ci dessous, lequel souhaitez vous voir mort?" 
		for j in joueurs:
			print "- ",j
		time.sleep(2)

		print "\033[36m\n\n---------------------------------------------------------------\n Début du chat avec tous les joueurs \n\033[0m"
		print "Quittez le une fois la décision prise en tapant : fin du chat"
		
		#chat de délibération
		thread_chat = threading.Thread(target = chat)
		thread_chat.start()
		while True:
			message = str(raw_input())
			p.envoi("chat_rec", message)
			if "fin du chat" in message:
				break
		print "\033[36m\n Fin du chat \n-----------------------------------------------------------------\033[0m"
		
		print "Attendons que les autres joueurs soient sortis du chat...\n"
		
		p.attente("chat_fini")
		
		#on récupère le nom de la personne désignée
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
		
		#on vérifie si on a atteint une issue du jeu, ou si on repart pour un tour.
		keepPlaying = mortVote[2]
			
		if(keepPlaying != "SansVainqueur"):
			if(keepPlaying == "LoupsVainqueurs"):
				
				print "\033[91m\n \n--------------------------------------------------------------------"
				print "----   La partie est finie : les loups ont décimé le village!!!  ---"
				print "--------------------------------------------------------------------\n \n\033[0m"
				break
			else:
				print "\033[93m\n \n--------------------------------------------------------------------"
				print "--------   La partie est finie : les loups ont été décimés!!!  ------"
				print "--------------------------------------------------------------------\n \n\033[0m"
				break

		if(mortVote[0]==pseudo):
			
			print "\033[91m\n \n--------------------------------------------------------------------"
			print "------------------   Votre aventure s'arrête ici...  --------------"
			print "--------------------------------------------------------------------\n \n\033[0m"
			break
			
			
print "\nVous allez être déconnecté du serveur. A bientôt pour une nouvelle partie!\n"
socket.close()


	






