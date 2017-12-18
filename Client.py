#! /usr/bin/env python
# -*- coding:utf-8 -*-



from socket import *
from Protocole import *
from Joueur import *
import sys

	
#recupere l'adresse du serveur en parametres

print "Bienvenue dans votre partie de Loup Garou!\n "
adresse_serveur = str(sys.argv[1])
#print "Demande de connexion au serveur a l'adresse ", adresse_serveur, "."
socket = socket(AF_INET, SOCK_STREAM)
socket.connect((adresse_serveur,8000))
print "Connecte au serveur à l'adresse ", adresse_serveur, ".\n"

#creation du protocole de communication avec le serveur
p = Protocole(socket, '$')
	
print "Veuillez rentrer votre pseudo pour la partie :\n"
pseudo = str(raw_input())
p.envoi("pseudo", pseudo)

#joueurs = '_'
print "Nous attendons que tous les joueurs regagnent la partie..."
#while (joueurs=='_'):
#	joueurs = p.recListe("joueurs")

joueurs = p.attenteListe("joueurs")

print "Tout le monde est la : ",joueurs
p.envoi("valid", '')
perso = p.rec("perso")
print "Vous êtes un ",perso,".\n \n"

while True:

	print "--------------------------------------------------------------------"
	print "---------------    La nuit tombe sur le village    -----------------"
	print "--------------------------------------------------------------------\n \n"


	#methode décrivant le crime des loups garous pendant la nuit
	def NuitLoupGarou(p):
		p.envoi("loups",'')
		loups = p.recListe("listeLoups")
		print "Les loups garous s'éveillent et se reconnaissent. Il s'agit de : ", loups
		p.envoi("loupsreçus",'')
		vill = p.recListe("listeVillageois")
		print "Vous pouvez tuer", vill
		print "Entrez le nom de la victime"
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
			

	print "\n \n--------------------------------------------------------------------"
	print "---------------------    Le jour se lève    ------------------------"
	print "--------------------------------------------------------------------\n \n"

		
	print "\nCette nuit, ",mort," a été dévoré(e)...\n"
	
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
		print joueurs

		vote = str(raw_input())
		while (vote not in joueurs):
			print "Veuillez rentrer le nom d'une des personnes pouvant être tuée dans la liste ci dessus."
			vote = str(raw_input())
		p.envoi("vote", vote)
		
		print "Nous attendons que tout le monde ait voté et délibéré...\n "
		mortVote = p.attenteListe("mortVote")
		
		print "Le village a décidé de tuer ", mortVote[0],". Il s'agissait d'un ", mortVote[1]," !"
	

print " Vous allez être déconnecté du serveur. A bientôt pour une nouvelle partie!"
socket.close()
#print "\033[31mThis is blue\033[0m"


	






