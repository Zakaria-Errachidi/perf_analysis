import base64
import hashlib
import secrets
import urllib.parse
import webbrowser

import requests


# ============================================================
# 1. CONFIGURATION
# ============================================================

CLIENT_ID = "ioePNZUmZ8UqNVXofUG0WptDBFGVLZbaUAziUCYd"
CLIENT_SECRET = "Ljl4j90d4zpRJhvmYlp9NVgkA4hB2VycgKCYR2DBVgY5sOIjdTaJ264kO9cpttWiZsZqm8BCRfZG6dUpdrS6ze0aERz8yOfHtDOsezfVLmsSkp5VQHdxPnfNMs0kBkwA"

REDIRECT_URI = "https://localhost:8000/callback"


# ============================================================
# 2. GENERER LE CODE VERIFIER + CODE CHALLENGE
# ============================================================

# PKCE verifier
code_verifier = secrets.token_urlsafe(64)

# SHA256 du verifier
challenge_bytes = hashlib.sha256(
    code_verifier.encode("utf-8")
).digest()

# Base64 URL-safe
code_challenge = (
    base64.urlsafe_b64encode(challenge_bytes)
    .decode("utf-8")
    .rstrip("=")
)


print("CODE_VERIFIER généré.")
print("CODE_CHALLENGE généré.")


# ============================================================
# 3. CONSTRUIRE L'URL D'AUTORISATION FOOTBAR
# ============================================================

params = {
    "response_type": "code",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
}

authorization_url = (
    "https://api.footbar.com/oauth/authorize/?"
    + urllib.parse.urlencode(params)
)

print("\n==============================================")
print("OUVRE CETTE URL DANS TON NAVIGATEUR :")
print("==============================================\n")
print(authorization_url)

# Ouvre automatiquement le navigateur
webbrowser.open(authorization_url)


# ============================================================
# 4. ATTENDRE QUE TU AUTORISES L'APPLICATION
# ============================================================

print("\n")
print("1. Une page Footbar devrait être ouverte.")
print("2. Connecte-toi si nécessaire.")
print("3. Clique sur Autoriser.")
print()
print("Après l'autorisation, Footbar va te rediriger vers :")
print(REDIRECT_URI)
print()
print("Copie l'URL complète affichée dans ton navigateur.")
print()


callback_url = input("Colle ici l'URL complète : ").strip()


# ============================================================
# 5. RECUPERER LE CODE
# ============================================================

parsed_url = urllib.parse.urlparse(callback_url)

query_params = urllib.parse.parse_qs(parsed_url.query)

if "error" in query_params:
    print("\nERREUR Footbar :")
    print(query_params)
    raise SystemExit

if "code" not in query_params:
    print("\nImpossible de trouver le code dans l'URL.")
    print("URL reçue :", callback_url)
    raise SystemExit

code = query_params["code"][0]

print("\nAuthorization code récupéré.")


# ============================================================
# 6. ECHANGER LE CODE CONTRE LES TOKENS
# ============================================================

token_url = "https://api.footbar.com/oauth/token/"

token_data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": code,
    "code_verifier": code_verifier,
    "grant_type": "authorization_code",
    "scope": "read",
}

response = requests.post(
    token_url,
    data=token_data,
    headers={
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
    },
)

print("\nHTTP status :", response.status_code)

if not response.ok:
    print("\nErreur lors de l'obtention du token :")
    print(response.text)
    raise SystemExit


tokens = response.json()


# ============================================================
# 7. RECUPERER LES TOKENS
# ============================================================

access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

user_id = tokens["user"]["id"]

print("\n==============================================")
print("AUTHENTIFICATION REUSSIE !")
print("==============================================")

print("User ID :", user_id)
print("Access token obtenu :", access_token[:10] + "...")
print("Refresh token obtenu :", refresh_token[:10] + "...")


# ============================================================
# 8. TESTER L'API FOOTBAR
# ============================================================

print("\nTest de l'API Footbar...")


session_url = (
    "https://api.footbar.com/v1/session/list/"
)

api_response = requests.get(
    session_url,
    headers={
        "Authorization": f"Bearer {access_token}"
    },
)

print("HTTP status :", api_response.status_code)

if api_response.ok:

    print("\n==============================================")
    print("SESSIONS RECUPEREES !")
    print("==============================================")

    print(api_response.text)

else:

    print("\nErreur lors de la récupération des sessions :")
    print(api_response.text)


# ============================================================
# 9. SAUVEGARDER LES TOKENS
# ============================================================

with open("footbar_tokens.txt", "w", encoding="utf-8") as f:

    f.write(f"ACCESS_TOKEN={access_token}\n")
    f.write(f"REFRESH_TOKEN={refresh_token}\n")
    f.write(f"USER_ID={user_id}\n")

print("\nTokens sauvegardés dans footbar_tokens.txt")
print("NE PARTAGE PAS ce fichier.")


# ============================================================
# 10. RECUPERER LA LISTE DE TOUTES LES SESSIONS
# ============================================================

print("\n==============================================")
print("RECUPERATION DE LA LISTE DES SESSIONS")
print("==============================================")

session_list_url = (
    "https://api.footbar.com/v1/session/list/"
)

list_response = requests.get(
    session_list_url,
    headers={
        "Authorization": f"Bearer {access_token}"
    },
)

print("HTTP status :", list_response.status_code)

if not list_response.ok:
    print("\nErreur lors de la récupération des sessions :")
    print(list_response.text)
    raise SystemExit


sessions_data = list_response.json()

print("\nNombre total de sessions disponibles :", sessions_data["count"])


# ============================================================
# 11. CHARGER LE FICHIER RAW EXISTANT
# ============================================================

import json
import os

RAW_FILE = "./data/footbar_raw.json"

# Liste qui contiendra toutes les données déjà sauvegardées
existing_sessions = []

if os.path.exists(RAW_FILE):

    print("\nFichier RAW existant trouvé.")

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        existing_sessions = json.load(f)

    print(
        "Nombre de sessions déjà sauvegardées :",
        len(existing_sessions)
    )

else:

    print("\nAucun fichier RAW trouvé.")
    print("Création d'un nouveau fichier.")

    existing_sessions = []


# ============================================================
# 12. IDENTIFIER LES SESSIONS DEJA RECUPEREES
# ============================================================

existing_session_ids = set()

for item in existing_sessions:
    # Cas 1 : une réponse API complète contenant "results"
    if "results" in item:
        for session in item["results"]:
            if "id" in session:
                existing_session_ids.add(session["id"])

    # Cas 2 : une session directement enregistrée
    elif "id" in item:
        existing_session_ids.add(item["id"])

print("\nIDs déjà présents dans le fichier RAW :")

for session_id in sorted(existing_session_ids):
    print("-", session_id)

# ============================================================
# 13. IDENTIFIER UNIQUEMENT LES NOUVELLES SESSIONS
# ============================================================

sessions = sessions_data["results"]

new_sessions = [
    session
    for session in sessions
    if session["id"] not in existing_session_ids
]

print("\n==============================================")
print("DETECTION DES NOUVELLES SESSIONS")
print("==============================================")

print(
    "\nNombre de nouvelles sessions :",
    len(new_sessions)
)

if new_sessions:

    print("\nNouvelles sessions détectées :")

    for session in new_sessions:

        print(
            "-",
            session["id"],
            "|",
            session.get("start_date"),
            "|",
            session.get("title")
        )

else:

    print("\nAucune nouvelle session.")
    print("Aucune requête /session/detail/ ne sera effectuée.")


# ============================================================
# 14. RECUPERER LE DETAIL UNIQUEMENT DES NOUVELLES SESSIONS
# ============================================================

print("\n==============================================")
print("RECUPERATION DES NOUVEAUX DETAILS")
print("==============================================")

session_detail_url = (
    "https://api.footbar.com/v1/session/detail/"
)

new_session_details = []

for session in new_sessions:

    session_id = session["id"]

    print(
        f"\nRécupération de la session {session_id}..."
    )

    detail_response = requests.get(
        session_detail_url,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params={
            "id": session_id
        },
    )

    print(
        "HTTP status :",
        detail_response.status_code
    )

    if detail_response.ok:

        detail_data = detail_response.json()

        new_session_details.append(detail_data)

        print("✓ Session récupérée")

    else:

        print("✗ Erreur")
        print(detail_response.text)


# ============================================================
# 15. AJOUTER LES NOUVELLES SESSIONS AUX ANCIENNES
# ============================================================

if new_session_details:

    existing_sessions.extend(new_session_details)

    print("\n==============================================")
    print("NOUVELLES DONNEES AJOUTEES")
    print("==============================================")

    print(
        "\nNombre de nouvelles sessions ajoutées :",
        len(new_session_details)
    )

else:

    print("\nAucune nouvelle donnée à ajouter.")


# ============================================================
# 16. SAUVEGARDER LE FICHIER RAW
# ============================================================

with open(RAW_FILE, "w", encoding="utf-8") as f:

    json.dump(
        existing_sessions,
        f,
        ensure_ascii=False,
        indent=4
    )

print("\n==============================================")
print("DONNEES RAW SAUVEGARDEES")
print("==============================================")

print(
    f"\nFichier utilisé : {RAW_FILE}"
)

print(
    "Nombre total de sessions dans le fichier :",
    len(existing_sessions)
)