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


def NuitLoupGarou(p):
	p.envoi("loups",'')
	loups = p.recListe("listeLoups")
	print "Vous êtes loup avec ", loups
	p.envoi("loupsreçus",'')
	
	print "Vous pouvez tuer", p.recListe("listeVillageois")
	print "Entrez le nom de la victime"
	mort = str(raw_input())
	p.envoi("mort", mort)

	
	
print'\nLa nuit tombe sur le village...'
if(perso == "Loup Garou"):
	NuitLoupGarou(p)
	mort = p.attente("jour")
	
if(perso == "Villageois"):
	print "Vous dormez profondément."
	mort = p.attente("jour")
	
#print "\033[31mThis is blue\033[0m"


	






