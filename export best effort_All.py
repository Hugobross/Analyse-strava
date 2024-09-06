import requests
import pandas as pd
import time

#Pour éxécuter ce code bien veillez à changer les noms de ficheirs en fonction de l'athlète et le auth code



# Remplacez par vos propres informations
'''
CLIENT_ID = '129987'#Hugo Brossat
CLIENT_SECRET = 'fbd084d9fd15e03ba23c67fba1d1daf172d48e37'
REDIRECT_URI = 'http://localhost'
AUTH_CODE = 'a3635260cbc865ec50f7e6128d2cdca068d002ef'  # Remplacez par le code d'autorisation obtenu

CLIENT_ID = '132312',#Richard Brossat
CLIENT_SECRET = '6a9dd14107b9fe353d5bd26883226cf1fb8f97d3',
REDIRECT_URI = 'http://localhost',
AUTH_CODE = 'e30a708bd300ab6f84c514fd80e26039b69afe2f'  # Remplacez par le code d'autorisation obtenu

CLIENT_ID = '133435',#Gabriel Duval
CLIENT_SECRET = 'e0074c1cdc31dd05cd5180d77b8da4fa3a542403',
REDIRECT_URI = 'http://localhost',
AUTH_CODE = '22e8175bcc27df77b7cc6dd1cf7b1c57dcb79610'  # Remplacez par le code d'autorisation obtenu


CLIENT_ID = '133438',#Hugo Attali
CLIENT_SECRET = 'e36c1f1b74c84bc5efa4644e946bb10dbadde4c3',
REDIRECT_URI = 'http://localhost',
AUTH_CODE = 'bc90b03e1c8ef9855122b1b97e7265f2898fd787'  # Remplacez par le code d'autorisation obtenu


CLIENT_ID = '133564',#Antoine Giroud
CLIENT_SECRET = '858abda120970ef64b5a7c0f6169805e18119672',
REDIRECT_URI = 'http://localhost',
AUTH_CODE = '5ab52c62998c2943f16fa8bb566d5fe5b2f76d8a'

'''
CLIENT_ID = '133682',#Pierre Canard
CLIENT_SECRET = '1e0dbd054f9b344843bf0abeb6f7525d46fcc4a5',
REDIRECT_URI = 'http://localhost',
AUTH_CODE = '85e53e2e05f1efbbafc6fb136ac2b43f21157d46' 



# Échanger le code d'autorisation contre un token d'accès
token_response = requests.post(
    'https://www.strava.com/oauth/token',
    data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': AUTH_CODE,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
)

token_data = token_response.json()

if 'access_token' in token_data:
    access_token = token_data['access_token']
    print(f"Access Token: {access_token}")
    
    # URL pour récupérer toutes les activités de l'athlète
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    params = {
        'per_page': 50,  # Nombre d'activités par page (ajusté pour éviter les dépassements de limite)
        'page': 1         # Page de résultats
    }

    # Fonction pour gérer le backoff exponentiel en cas de rate limit
    def handle_rate_limit(response):
        if response.status_code == 429:  # 429 Too Many Requests
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            current_time = int(time.time())
            wait_time = reset_time - current_time
            if wait_time > 0:
                print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                time.sleep(wait_time + 1)  # Attendre un peu plus pour être sûr

    try:
        activities_data = []
        detailed_activities = []

        # Filtrer les meilleurs efforts spécifiés
        best_effort_names = ['5K', '10K', '15K', '20K','Half-Marathon','Marathon']
        

        # Récupérer toutes les activités de l'athlète
        while True:
            response = requests.get(activities_url, headers=headers, params=params)
            
            if response.status_code != 200:
                handle_rate_limit(response)
                if response.status_code != 200:
                    print(f"Erreur lors de la récupération des activités : {response.status_code}, {response.text}")
                    break

            data = response.json()
            if not data:
                break
            
            activities_data.extend(data)
            params['page'] += 1  # Passer à la page suivante

            # Récupérer les détails des activités par lots pour éviter les limitations de taux
            for activity in data:
                activity_id = activity['id']

                # URL pour récupérer les détails de cette activité
                activity_url = f'https://www.strava.com/api/v3/activities/{activity_id}'

                while True:
                    response = requests.get(activity_url, headers=headers)
                    if response.status_code == 200:
                        detailed_activity = response.json()
                        
                        # Ajouter les détails de l'activité et les meilleurs efforts à la liste
                        if 'best_efforts' in detailed_activity:
                            for effort in detailed_activity['best_efforts']:
                                if effort['name'] in best_effort_names:
                                    detailed_activities.append({
                                        'activity_id': activity_id,
                                        'athlete': effort['athlete'],
                                        'best_effort_name': effort['name'],
                                        'best_effort_elapsed_time': effort['elapsed_time'],
                                    })
                        break
                    elif response.status_code == 404:
                        print(f"Erreur 404 : Aucun détail trouvé pour l'activité '{activity['name']}'.")
                        break
                    else:
                        handle_rate_limit(response)
                        if response.status_code != 200:
                            print(f"Erreur lors de la récupération des détails pour l'activité '{activity['name']}' : {response.status_code}, {response.text}")
                            break

            # Pause pour éviter les limitations de taux après chaque lot
            print("Pause pour éviter les limitations de taux...")
            time.sleep(700)  # Ajustez le temps de pause si nécessaire

        # Créer un DataFrame à partir de la liste des activités détaillées et des meilleurs efforts
        df_detailed_activities = pd.DataFrame(detailed_activities)
        csv_effort = 'best_effort_PierreCanard.csv'
        df_detailed_activities.to_csv(csv_effort,encoding ='utf-8',index=False)
      

    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête : {e}")

else:
    print("Impossible d'obtenir un token d'accès.")
    
    
    
    
    
    
