#! /usr/bin/env python
# -*- coding:utf-8 -*-


class Protocole:
	#this class provides methods to send and receive data avoiding buffer issues
	#we format our data flow as follows : 
	#ID:data$ID:data$.....	
	
	#initialisation : on rentre en paramètres le caractère de fin d'un message
	#ainsi que le socket de communication à utiliser
	def __init__(self, socket, fin):
		self.fin = fin
		self.s = socket
		
	#envoie un message, avec l'identifiant passé en paramètres
	def envoi(self, ID, data):
		try:
			envoi = ID +":" + str(data) + self.fin
			self.s.sendall(envoi)

		except socket.error, e:
			print "erreur dans l'envoi par le protocole utilisant la socket: %s" % e
	
	#envoie une liste de la même manière
	def envoiListe(self, ID, data):
		self.envoi(ID, ','.join(data))
	
	#reçoit un message pour un identifiant donné, et le retourne
	#si rien ne correspond à l'ID rentré, renvoie "_".
	def rec(self, ID):
		try :
			data = self.s.recv(1024)
			data = data.split(':')
			if(ID in data):
				data = data[data.index(ID)+1]
				data = data.split(self.fin)[0]
				return data
			else:
				return '_'

		except socket.error, e:
			print "erreur dans la reception par le protocole utilisant la socket: %s" % e
			

	#reçoit une liste de la même manière
	def recListe(self, ID):	
		d = self.rec(ID)
		return d.split(',')
	
	#attend un message avec un ID donné
	def attente(self, ID):
		res = '_'
		while (res=='_'):
			res = self.rec(ID)
		return res
	
	#attend une liste de la même manière
	def attenteListe(self, ID):
		res = '_'
		while (res=='_'):
			res = self.recListe(ID)
		return res
