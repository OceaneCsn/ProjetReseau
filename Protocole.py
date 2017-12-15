#! /usr/bin/env python
# -*- coding:utf-8 -*-


class Protocole:
	#this class provides methods to send and receive data avoiding buffer issues
	#we format our data flow as follows : 
	#ID:data$ID:data$.....	
	
	def __init__(self, socket, fin):
		self.fin = fin
		self.s = socket
		
		
	def envoi(self, ID, data):
		try:
			envoi = ID +":" + str(data) + self.fin
			self.s.sendall(envoi)
			#print "envoi : ",envoi
			
		except socket.error, e:
			print "erreur dans l'envoi par le protocole utilisant la socket: %s" % e
	

	def envoiListe(self, ID, data):
		self.envoi(ID, ','.join(data))
		
	def rec(self, ID):
		try :
			data = self.s.recv(1024)
			#print "recu : ",data
			data = data.split(':')
			if(ID in data):
				data = data[data.index(ID)+1]
				data = data.split(self.fin)[0]
				return data
			else:
				#print "L'identifiant ", ID, " n'etait pas present dans l'echange"
				return '_'

		except socket.error, e:
			print "erreur dans la reception par le protocole utilisant la socket: %s" % e
			


	def recListe(self, ID):	
		d = self.rec(ID)
		#print "liste recue : ",d
		return d.split(',')
		
	def attente(self, ID):
		res = '_'
		while (res=='_'):
			res = self.rec(ID)
		return res

	def attenteListe(self, ID):
		res = '_'
		while (res=='_'):
			res = self.recListe(ID)
		return res
