
from socket import *
from Protocole import *
from Joueur import *
import sys

adresse_serveur = str(sys.argv[1])
print "Demande de connexion"
socket = socket(AF_INET, SOCK_STREAM)
socket.connect((adresse_serveur,8000))
print "Connecte au serveur"
p = Protocole(socket, '$')

p.envoi("pseudo", "Imane")
a = '_'
while (p.recListe("joueurs")=='_'):
	a = p.recListe("joueurs")
#	print a
	
	
print a
