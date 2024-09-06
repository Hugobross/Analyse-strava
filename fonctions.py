#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 15:14:57 2024

@author: brossathugo
"""
import requests
import pandas as pd
import re

 # Fonction pour supprimer les accents, apostrophes et smileys d'une chaîne en utilisant regex
def remove_special_chars(input_str):
  # Définition des correspondances de caractères spéciaux avec leur forme sans caractères spéciaux
      special_chars = {
      'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
      'à': 'a', 'â': 'a', 'ä': 'a',
      'ô': 'o', 'ö': 'o',
      'û': 'u', 'ü': 'u',
      'î': 'i', 'ï': 'i',
      'ç': 'c'
  }
  
  # Utilisation de regex pour remplacer les caractères spéciaux par leur équivalent non spécial
      return re.sub(r'[éèêëàâäôöûüîïç]', lambda m: special_chars[m.group(0)], input_str)
  
  
def remove_emojis(text):
  # Utiliser une expression régulière pour supprimer les emojis
      emoji_pattern = re.compile("["
                             u"\U0001F600-\U0001F64F"  # Emojis généraux
                             u"\U0001F300-\U0001F5FF"  # Autres symboles et pictogrammes
                             u"\U0001F680-\U0001F6FF"  # Transport et symboles de map
                             u"\U0001F1E0-\U0001F1FF"  # Drapeaux (iOS)
                             u"\U00002500-\U00002BEF"  # Symboles chinois
                             u"\U00002702-\U000027B0"
                             u"\U00002702-\U000027B0"
                             u"\U000024C2-\U0001F251"
                             u"\U0001f926-\U0001f937"
                             u"\U00010000-\U0010ffff"
                             u"\u2640-\u2642"
                             u"\u2600-\u2B55"
                             u"\u200d"
                             u"\u23cf"
                             u"\u23e9"
                             u"\u231a"
                             u"\ufe0f"  # Modification de variante
                             u"\u3030"
                             "]+", flags=re.UNICODE)
      return emoji_pattern.sub(r'', text)
  
def remove_apostrophes(text):
  # Liste des différents types d'apostrophes
      apostrophes = ["'", "’", "‘", "‛", "`", "´"]
      for apostrophe in apostrophes:
          text = text.replace(apostrophe, "")
      return text
  
    
# Fonction pour extraire latitude et longitude en vérifiant la validité des données
def extract_coordinates(latlng):
    
    
    
    if isinstance(latlng, list) and len(latlng) == 2:
        return latlng[0], latlng[1]
    return None, None



def get_location_data_nominatim(lat, lon):
    if lat is None or lon is None:
        return None, None, None
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {
            'User-Agent': 'MyScript/1.0 (contact@example.com)'  
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        try:
            data = response.json()
            if 'address' in data:
                address = data['address']
                country = address.get('country', None)
                state = address.get('state', None)
                city = address.get('city', None) or address.get('town', None) or address.get('village', None)
                return country, state, city
            else:
                return None, None, None
        except ValueError as e:
            print(f"Erreur de décodage JSON pour {lat}, {lon}: {e}")
            return None, None, None
    except requests.RequestException as e:
        print(f"Erreur lors de l'appel API pour {lat}, {lon}: {e}")
        return None, None, None
    
    
# Fonction pour obtenir les données géographiques pour chaque ligne du DataFrame
def fetch_geographical_data(df):
    ids = []
    country_list = []
    state_list = []
    city_list = []
    
    for _, row in df.iterrows():
        ids.append(row['id'])
        lat = row['Latitude']
        lon = row['Longitude']
        if lat is not None and lon is not None:
            country, state, city = get_location_data_nominatim(lat, lon)
            country_list.append(country)
            state_list.append(state)
            city_list.append(city)
        else:
            country_list.append(None)
            state_list.append(None)
            city_list.append(None)
    
    df_geo = pd.DataFrame({
        'id': ids,
        'Latitude': df['Latitude'],
        'Longitude': df['Longitude'],
        'Country': country_list,
        'State': state_list,
        'City': city_list
    })
    return df_geo
