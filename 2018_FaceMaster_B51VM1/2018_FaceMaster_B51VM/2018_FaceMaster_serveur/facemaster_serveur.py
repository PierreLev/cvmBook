# -*- encoding: utf-8 -*-

#import Pyro4
from xmlrpc.server import SimpleXMLRPCServer

import xmlrpc.client

import os,os.path
from threading import Timer
import sys
import socket
import time
import random


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("gmail.com",80))
monip=s.getsockname()[0]
print("MON IP SERVEUR",monip)
s.close()

#daemon = Pyro4.core.Daemon(host=monip,port=9999) 
daemon= SimpleXMLRPCServer((monip,9999))

class Client(object):
    def __init__(self,nom):
        self.nom=nom
        self.cadreCourant=0
        self.cadreEnAttenteMax=0
        self.actionsEnAttentes={}
        
class ModeleService(object):
    def __init__(self,parent,rdseed):
        self.parent=parent
        self.modulesdisponibles={"projet":"fm_projet",
                                 "sql":"fm_sql",
                                 "totoro":"fm_totoro",
                                 "spiderman":"fm_spiderman",
                                 "inscription":"fm_inscription"}
        self.etatJeu=0
        self.rdseed=rdseed
        self.cadreCourant=0
        self.cadreFutur=2
        self.clients={}
        self.cadreDelta={}
        
    def creerclient(self,nom):
        if self.etatJeu==0:  # si le jeu n'est pas partie sinon voir else
            if nom in self.clients.keys(): # on assure un nom unique
                return [0,"Erreur de nom"]
            # tout va bien on cree le client et lui retourne la seed pour le random
            c=Client(nom)
            self.cadreDelta[nom]=0
            self.clients[nom]=c
            return [1,"Bienvenue",list(self.modulesdisponibles.keys())]
        else:
            return [0,"Simulation deja en cours"]
            
class ControleurServeur(object):
    def __init__(self):
        rand=random.randrange(1000)+1000
        #self.checkping=0
        self.delaitimeout=25   # delai de 5 secondes
        self.modele=ModeleService(self,rand)
        
    def testPyro(self):
        return 42
        
    def loginauserveur(self,nom):
        rep=self.modele.creerclient(nom)
        return rep

    def requetemodule(self,mod):
        if mod in self.modele.modulesdisponibles.keys():
            cwd=os.getcwd()
            #print(mod,os.getcwd())
            if os.path.exists(cwd+"/fm_modules/"):
                dirmod=cwd+"/fm_modules/"+self.modele.modulesdisponibles[mod]+"/"
                if os.path.exists(dirmod):
                    #print("TROUVE")
                    listefichiers=[]
                    for i in os.listdir(dirmod):
                        if os.path.isfile(dirmod+i):
                            val=["fichier",i]
                        else:
                            val=["dossier",i]
                            
                        listefichiers.append(val)
                    return [mod,dirmod,listefichiers]
            
            
            
    def requetefichier(self,lieu):
        fiche=open(lieu,"rb")
        contenub=fiche.read()
        fiche.close()
        return xmlrpc.client.Binary(contenub)
            
    
    def verifiecontinuation(self):
        t=int(time.time())
        if (t-self.checkping) > self.delaitimeout: 
            self.fermer()
        else:
            tim=Timer(1,self.verifiecontinuation)
            tim.start()
        
    def quitter(self):
        t=Timer(1,self.fermer)
        t.start()
        return "ferme"
    
    def jequitte(self,nom):
        del self.modele.clients[nom]
        del self.modele.cadreDelta[nom]
        if not self.modele.clients:
            self.quitter()
        return 1
    
    def fermer(self):
        print("FERMETURE DU SERVEUR")
        daemon.shutdown()

controleurServeur=ControleurServeur()
daemon.register_instance(controleurServeur)  
 
print("Serveur XML-RPC actif")
daemon.serve_forever()