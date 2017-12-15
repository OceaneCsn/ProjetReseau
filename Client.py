#! /usr/bin/env python
# -*- coding:utf-8 -*-



from socket import *
from Protocole import *
from Joueur import *
import sys

	
#recupere l'adresse du serveur en parametres

print "Bienvenue dans votre partie de Loup Garou! "
adresse_serveur = str(sys.argv[1])
print "Demande de connexion au serveur a l'adresse ", adresse_serveur, "."
socket = socket(AF_INET, SOCK_STREAM)
socket.connect((adresse_serveur,8000))
print "Connecte au serveur."

#creation du protocole de communication avec le serveur
p = Protocole(socket, '$')
	
print "Veuillez rentrer votre pseudo pour la partie :"
pseudo = str(raw_input())
p.envoi("pseudo", pseudo)
joueurs = '_'
print "Nous attendons que tous les joueurs regagnent la partie..."
while (joueurs=='_'):
	joueurs = p.recListe("joueurs")
	
print "Tout le monde est la : ",joueurs
p.envoi("valid", '')
perso = p.rec("perso")
print "Vous êtes un ",perso

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

	
	
print'\nLa nuit tombe sur le village...'
if(perso == "Loup Garou"):
	NuitLoupGarou(p)
	mort = p.attente("jour")

#le joueur s'endort pendant que les loups choisissent une victime
if(perso == "Villageois"):
	print "Vous dormez profondément."
	mort = p.attente("jour")

#on supprime le joueur tué
for pl in joueurs:
		if(pl == mort):joueurs.remove(pl)
	
print "\nCette nuit, ",mort," a été dévoré(e)..\n."

#Fin du jeu pour le joueur tué par le(s) loup(s).
if(mort==pseudo):
	print "Votre aventure s'arrête ici... A bientôt pour une nouvelle partie!\n"
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
	

#print "\033[31mThis is blue\033[0m"


	






