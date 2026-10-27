
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    scopes=SCOPES,
)

credentials = flow.run_local_server(
    host="localhost",
    port=0,
    access_type="offline",
    prompt="consent",
)

with open("token.json", "w", encoding="utf-8") as f:
    f.write(credentials.to_json())

print("Nouvelle autorisation enregistrée dans token.json")
print("Expiration :", credentials.expiry)
print("Refresh token disponible :", bool(credentials.refresh_token))
