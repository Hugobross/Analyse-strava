#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 15:00:26 2024

@author: brossathugo
"""

import requests
import pandas as pd
import re
import fonctions as f


#HugoBrossatUrl : https://www.strava.com/oauth/authorize?client_id=129987&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=force
#RichardBrossatUrl : https://www.strava.com/oauth/authorize?client_id=132312&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=force
#GabrielDuvalUrl : https://www.strava.com/oauth/authorize?client_id=133435&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=force
#HugoAttaliUrl : https://www.strava.com/oauth/authorize?client_id=133438&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=force
#AntoineGiroudUrl: https://www.strava.com/oauth/authorize?client_id=133564&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=force
#PFUrl: https://www.strava.com/oauth/authorize?client_id=133682&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=force
 
# Liste des informations d'authentification pour chaque athlète
athletes_info = [
    {
       'CLIENT_ID' : '129987',#Hugo Brossat
       'CLIENT_SECRET' : 'fbd084d9fd15e03ba23c67fba1d1daf172d48e37',
       'REDIRECT_URI' : 'http://localhost',
       'AUTH_CODE' : 'da789634eec7883a90afc426f541b327b3887fd4'  # Remplacez par le code d'autorisation obtenu
    },
    {
   'CLIENT_ID' : '132312',#Richard Brossat
   'CLIENT_SECRET' : '6a9dd14107b9fe353d5bd26883226cf1fb8f97d3',
   'REDIRECT_URI' : 'http://localhost',
   'AUTH_CODE' : '8d864068762c139d7d22d4296c13a78184ccde67'  # Remplacez par le code d'autorisation obtenu
   },
   {
   'CLIENT_ID' : '133435',#Gabriel Duval
   'CLIENT_SECRET' : 'e0074c1cdc31dd05cd5180d77b8da4fa3a542403',
   'REDIRECT_URI' : 'http://localhost',
   'AUTH_CODE' : '3a27b286d9170f2396c9f14959b3d03bf46c1743'  # Remplacez par le code d'autorisation obtenu
   },
   {
   'CLIENT_ID' : '133438',#Hugo Attali
   'CLIENT_SECRET' : 'e36c1f1b74c84bc5efa4644e946bb10dbadde4c3',
   'REDIRECT_URI' : 'http://localhost',
   'AUTH_CODE' : '66e0e4e25be53ab7f3533f7ce7d9ba3fdecfcf01'  # Remplacez par le code d'autorisation obtenu
   },
   {
   'CLIENT_ID' : '133564',#Antoine Giroud
   'CLIENT_SECRET' : '858abda120970ef64b5a7c0f6169805e18119672',
   'REDIRECT_URI' : 'http://localhost',
   'AUTH_CODE' : 'de4e3957397d21332a2012cfd5c1db4d1eca19af'  # Remplacez par le code d'autorisation obtenu
   },
   {
   'CLIENT_ID' : '133682',#Pierre Canard
   'CLIENT_SECRET' : '1e0dbd054f9b344843bf0abeb6f7525d46fcc4a5',
   'REDIRECT_URI' : 'http://localhost',
   'AUTH_CODE' : '4386bbf764d92ee11a8e4517d669c4b8216e2e9d'  # Remplacez par le code d'autorisation obtenu
   }
    # Ajoutez autant d'athlètes que nécessaire
]   

    
# Liste pour stocker les DataFrames de chaque athlète

all_activities_dfs = []
all_profile_dfs = []
all_geo_dfs = []

for athlete_info in athletes_info:
    # Échanger le code d'autorisation contre un token d'accès
    token_response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
        'client_id': athlete_info['CLIENT_ID'],
            'client_secret': athlete_info['CLIENT_SECRET'],
            'code': athlete_info['AUTH_CODE'],
            'grant_type': 'authorization_code',
            'redirect_uri': athlete_info['REDIRECT_URI']
        }
    )

    token_data = token_response.json()

    if 'access_token' in token_data:
        access_token = token_data['access_token']
        print(f"Access Token: {access_token}")
        
        # Récupérer les données de profil
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get('https://www.strava.com/api/v3/athlete', headers=headers)
        profile_data = profile_response.json()
        athlete_id = profile_data['id']
        
        # Étape 4 : Récupérer tous les records personnels (PRs)
        prs_response = requests.get(f'https://www.strava.com/api/v3/athletes/39710442/koms', headers=headers)
        prs_data = prs_response.json()
       
        # Création du DataFrame avec les informations de profil
        df_profile = pd.DataFrame({
            'athlete_id': [profile_data.get('id', '')],
            'Nom complet': [profile_data.get('firstname', '') + ' ' + profile_data.get('lastname', '')],
            'Ville': [profile_data.get('city', '')],
            'Sexe': [profile_data.get('sex', '')],
            'Nombre de followers': [profile_data.get('follower_count', '')],
            'Nombre de suivis': [profile_data.get('friend_count', '')],
            'Date dinscription': [profile_data.get('created_at', '')],
            'Date de derniere mise a jour': [profile_data.get('updated_at', '')]
        })
        
        #Ajout de chaque athlete
        all_profile_dfs.append(df_profile)
        # Concaténer tous les DataFrames de profile
        df_all_profile = pd.concat(all_profile_dfs, ignore_index=True)
     
        # Récupérer plus d'activités avec des informations détaillées
        headers = {'Authorization': f'Bearer {access_token}'}
        activities_url = 'https://www.strava.com/api/v3/athlete/activities'
        params = {
            'per_page': 100,  # Nombre d'activités par page (maximum 100)
            'page': 1        # Page de résultats
        }
        activities_data = []
        while True:
            response = requests.get(activities_url, headers=headers, params=params)
            data = response.json()
            if not data:
                break
            activities_data.extend(data)
            params['page'] += 1  # Passer à la page suivante
        

        print("Mes Activités:")
        for activity in activities_data:
            activity_info = (
                f"Nom: {activity['name']}\n"
                f"Distance: {activity['distance']} mètres\n"
                f"Durée: {activity['moving_time']} secondes\n"
                f"Type: {activity['type']}\n"
                f"Date: {activity['start_date']}\n"
                f"Date: {activity['athlete']}\n"
                "-------------------"
            )
            print(activity_info)
        
        # Conversion en DataFrame
        df_activities = pd.DataFrame(activities_data)
      

    
        #ajout de chaque athlete
        all_activities_dfs.append(df_activities)
        # Concaténer tous les DataFrames d'activités
        df_all_activities = pd.concat(all_activities_dfs, ignore_index=True)
    
 
   # Premier nettoyage de données  
df_all_activities['name'] = df_all_activities['name'].apply(f.remove_special_chars)#suppreesion accents
df_all_activities['name'] = df_all_activities['name'].apply(f.remove_emojis)
df_all_activities['name'] = df_all_activities['name'].apply(f.remove_apostrophes)
df_all_activities = df_all_activities.drop('map', axis=1)
   

   #Appliquer la fonction pour extraire les coordonnées geo
df_all_activities['Latitude'], df_all_activities['Longitude'] = zip(*df_all_activities['start_latlng'].apply(f.extract_coordinates))
df_geo = df_all_activities[['id', 'Latitude','Longitude']]
df_geo = df_geo.dropna(subset=['Latitude', 'Longitude'])
df_geo = df_geo[(df_geo['Latitude'].notnull()) & (df_geo['Longitude'].notnull())]



#fonction appliquée pour joindre data geo et strava
df_geographical = f.fetch_geographical_data(df_geo)
    
#ajout de chaque athlete
all_geo_dfs.append(df_geographical)
    
# Concaténer tous les DataFrames geo
df_all_geo = pd.concat(all_geo_dfs, ignore_index=True)
    
    
    
 #Création des fichiers csv
csv_profile = 'profil_strava.csv'
df_all_profile.to_csv(csv_profile,encoding ='utf-8',index=True)
csv_activities = 'activites_strava.csv'
df_all_activities.to_csv(csv_activities,encoding ='utf-8',index=True)
csv_geo = 'geo_strava.csv'
df_all_geo.to_csv(csv_geo,encoding ='utf-8',index=True)
