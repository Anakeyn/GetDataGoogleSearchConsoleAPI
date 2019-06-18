# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 18:39:18 2019

@author: Pierre
"""
##########################################################################
# GetDataGoogleSearchConsoleAPI
# Auteur : Pierre Rouarch - Licence GPL 3
# Lectures de données dans Google Search Console API 
# voir sur le site de Google Developers :
# https://developers.google.com/webmaster-tools/search-console-api-original/v3/quickstart/quickstart-python
#####################################################################################
#Attention dans la littérature Google l'API s'appelle aussi 
#Google Search Analytics API ce qui peut amener une confusion avec 
#Google Web Analytics API !!!!!
###################################################################
# On démarre ici 
###################################################################
#Chargement des bibliothèques générales utiles
import pandas as pd  #pour les Dataframes ou tableaux de données
import datetime 
import os

print(os.getcwd())  #verif
#mon répertoire sur ma machine - nécessaire quand on fait tourner le programme 
#par morceaux dans Spyder.
#myPath = "C:/Users/Pierre/MyPath"
#os.chdir(myPath) #modification du path
#print(os.getcwd()) #verif


####### "Fourni" par Google #############################################

"""Hello Search Console Reporting API V3."""

import argparse
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools



SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest')

#les mauvais codes : utiliser les votres cela sont faux 
#Pour méthode avec IDs
MYCLIENTID="123456789-aaaaaaaaaaaaaaaaaaaaa.apps.googleusercontent.com"
MYCLIENTSECRET="123456789aaaaaaaaaaaaaaaaaa"
#pour méthode avec .json 
CLIENT_SECRETS_PATH = 'client_secret_123456789-aaaaaaaaaaaaaaaaaaaaa.apps.googleusercontent.com.json' # Path to client_secrets.json file.





# Parse command-line arguments.
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])
flags = parser.parse_args([])

#Méthode 1
# Créer un objet flow pour connection oAuth MYCLIENTID ou MYCLIENTSECRET
flow = client.OAuth2WebServerFlow(client_id=MYCLIENTID,
                           client_secret=MYCLIENTSECRET,
                           scope=SCOPES)

#Méthode 2
# Créer un objet flow avec le fichier .json pour connection oAuth
flow = client.flow_from_clientsecrets(
    CLIENT_SECRETS_PATH, scope=SCOPES,
    message=tools.message_if_missing(CLIENT_SECRETS_PATH))


# Prepare credentials, and authorize HTTP object with them.
# If the credentials don't exist or are invalid run through the native client
# flow. The Storage object will ensure that if successful the good
# credentials will get written back to a file.
storage = file.Storage('searchconsolereporting.dat')
credentials = storage.get()
#Attention ici si le fichier searchconsolereporting.dat le 
#programme ou une fenetre web et vous devez vous connecter
#avec votre compte google
if credentials is None or credentials.invalid:
  credentials = tools.run_flow(flow, storage, flags)
http = credentials.authorize(http=httplib2.Http())

#pour moi on verifie si https://www.networking-morbihan.com/ 
#est bien dans la liste des sites.
#creation du service (à reprendre plus bas)
webmasters_service = build('webmasters', 'v3', http=http)


# Retrieve list of properties in account
site_list = webmasters_service.sites().list().execute()
# Filter for verified websites
verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
                       if s['permissionLevel'] != 'siteUnverifiedUser'
                          and s['siteUrl'][:4] == 'http']
# Printing the URLs of all websites you are verified for.
for site_url in verified_sites_urls:
  print( site_url)

#C'est ok pour moi 
#https://www.networking-morbihan.com/
#http://www.networking-morbihan.com/
###### /Google

###############################################################################
#RECUPERATION DES DONNEES Pages/Mots-Clés/positions DANS Google Search Console
###############################################################################
######################################################################################
# Test MODELE "INTERNE"
# Pour l'instant on va travailer uniquement sur le site et voir si l'on peut 
# construire un "modèle interne" pour cela on va prendre un écart d'un mois
# ici on prend le dernier mois échu : mai 2019
#######################################################################################
#préparation de la requête
myStrDelai = "1M"  #1 mois
#Finalement on prend les dates du mois de mai
myStrStartDate = "2019-05-01"  #1er mai
myStrEndDate = "2019-05-31" #31 mai

mySiteUrl = "https://www.networking-morbihan.com/"
myRequest = {
  'startDate': myStrStartDate,    #date la plus éloignée
  'endDate': myStrEndDate,      #date la plus proche
  'dimensions': ['query','page'],      # on a besoin des couples requêtes , URL
  'searchType': 'web',
  'rowLimit': '5000'         #Peut aller jusqu'à 25000 si on a besoin de plus 
                              # on fait  varier (non utilisé ici)  le paramètre 'startRow':
}

response =  webmasters_service.searchanalytics().query(siteUrl=mySiteUrl, body=myRequest).execute()

#transformation de la réponse (dict) en DataFrame
dfGSC = pd.DataFrame.from_dict(response['rows'], orient='columns')

dfGSC.info()
dfGSC.dtypes
dfGSC.count()  # 514 enregistrements pour le mois de mai 2019
#split keys en query et page
dfGSC[["query", "page"]] = pd.DataFrame(dfGSC["keys"].values.tolist())
dfGSC['query']
dfGSC[ "page"]
dfGSC =  dfGSC.drop(columns=['keys'])  #on vire Keys qui ne nous sert pas 

dfGSC.info()

dfGSC.head(n=20)
#on sauvegarde en csv pour voir ce qu'il y a dedans
dfGSC.to_csv("dfGSC-MAI.csv", sep=";", index=False)  #séparateur ; 


#On Sauvegarde en json pour la suite comme flat file (mieux que .csv)
dfGSC.to_json("dfGSC-MAI.json")  #séparateur ; 




##########################################################################
# MERCI pour votre attention !
##########################################################################
#on reste dans l'IDE
#if __name__ == '__main__':
#  main()


