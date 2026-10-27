import requests
import json

# 1. Charger le token
with open("token.json", "r", encoding="utf-8") as f:
    token_data = json.load(f)

access_token = token_data["token"]

# 2. Endpoint
url = "https://health.googleapis.com/v4/users/me/dataTypes/exercise/dataPoints:reconcile"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

# 3. Récupération de toutes les pages
all_points = []
page_token = None
page_num = 0

while True:
    params = {"pageSize": 25}   # augmente si l'API l'autorise (ex. 100)
    if page_token:
        params["pageToken"] = page_token

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Erreur HTTP :", response.status_code)
        print(response.text)
        break

    data = response.json()
    points = data.get("dataPoints", [])
    all_points.extend(points)

    page_num += 1
    print(f"Page {page_num} : {len(points)} séances (total : {len(all_points)})")

    page_token = data.get("nextPageToken")
    if not page_token:
        break

# 4. Sauvegarde
with open("./data/exercise_all.json", "w", encoding="utf-8") as f:
    json.dump({"dataPoints": all_points}, f, indent=2, ensure_ascii=False)

print(f"\nTerminé : {len(all_points)} séances sauvegardées dans exercise_all.json")