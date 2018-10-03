# -*- coding: utf-8 -*-

import os,os.path
import sys

import Pyro4
from xmlrpc.client import ServerProxy

import socket
from subprocess import Popen 
import math
from facemaster_modele import *
from facemaster_vue import *
from helper import Helper as hlp
from IdMaker import Id

class Controleur():
    def __init__(self):
        print("IN CONTROLEUR")
        self.createurId=Id
        self.modele=None
        self.serveur=None
        self.monip=self.trouverIP()
        self.vue=Vue(self,self.monip)
        self.vue.root.mainloop()
        
    def trouverIP(self): # fonction pour trouver le IP en 'pignant' gmail
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # on cree un socket
        s.connect(("gmail.com",80))    # on envoie le ping
        monip=s.getsockname()[0] # on analyse la reponse qui contient l'IP en position 0 
        s.close() # ferme le socket
        return monip
    
    def loginclient(self,ipserveur,nom):
        if ipserveur and nom:
            ad="PYRO:controleurServeur@"+ipserveur+":9999" # construire la chaine de connection
            self.serveur=Pyro4.core.Proxy(ad) # se connecter au serveur
            ad="http://"+ipserveur+":9999"
            self.serveur=ServerProxy(ad)
            self.monnom=nom
            rep=self.serveur.loginauserveur(self.monnom)    # on averti le serveur de nous inscrire
            print("reponse du serveur",rep)
            self.vue.chargercentral(rep[2])
            
                    
    def requetemodule(self,mod):
        rep=self.serveur.requetemodule(mod)
        if rep:
            print(rep[0])
            cwd=os.getcwd()
            lieuApp="/fm_"+rep[0]
            lieu=cwd+lieuApp
            print(lieu)
            if not os.path.exists(lieu):
                os.mkdir(lieu) #plante s'il exist deja
            reso=rep[1]
            print(rep[1])
            for i in rep[2]:
                if i[0]=="fichier":
                    nom=reso+i[1]
                    rep=self.serveur.requetefichier(nom)
                    fiche=open(lieu+"/"+i[1],"wb")
                    fiche.write(rep.data)
                    fiche.close()
            chaineappli="."+lieuApp+lieuApp+".py"

            self.pid = Popen(["C:\\Python 3.6.5\\Python.exe", chaineappli,self.monnom],shell=0) 
            print(chaineappli)
            print(self.monnom)
         
                
        else:
            print("RIEN")
            
    
    def inscription(self):
        self.serveur.requetemodule
            
    def fermerprocessus(self):
        self.pid.kill()
        
    def connecteservice(self,rep):  # initalisation locale de la simulation, creation du modele, generation des assets et suppression du layout de lobby
        if rep[1][0][0]=="connecte":
            #print("REP",rep)
            self.modele=Modele(self,rep[1][0][1],rep[1][0][2]) # on cree le modele
            self.vue.afficherinitpartie(self.modele)

            
    def fermefenetre(self):
        if self.serveur:
            self.serveur.jequitte(self.monnom)
        self.vue.root.destroy()
        
        
if __name__=="__main__":
    c=Controleur()
    print("End FaceMaster")