import os
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

# Initialise le client OpenAI avec ta clé d'environnement
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Nouveau token GitHub pour les webhooks
GH_TOKEN = "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"

def analyze_code(code: str) -> str:
    """
    Analyse le code avec GPT-5-mini et renvoie un résumé :
    - bugs
    - améliorations
    - problèmes de sécurité
    - conseils de performance
    """
    prompt = f"""
You are an expert code reviewer.
Analyze the following code and provide:
- bugs
- improvements
- security issues
- performance tips

Code:
{code}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


@app.post("/webhook")
async def webhook(request: Request):
    """
    Point de réception du webhook GitHub pour les PR ouvertes.
    Analyse automatiquement les fichiers modifiés et poste un commentaire avec l'analyse.
    """
    payload = await request.json()

    # Vérifie si c'est un PR ouvert
    if payload.get("action") == "opened" and "pull_request" in payload:

        files_url = payload["pull_request"]["url"] + "/files"
        headers = {"Authorization": f"token {GH_TOKEN}"}

        files = requests.get(files_url, headers=headers).json()

        review_text = ""

        for f in files:
            # Ne traiter que les fichiers modifiés (patch)
            if f.get("patch"):
                review = analyze_code(f["patch"])
                review_text += f"\n### File: {f['filename']}\n{review}\n"

        # Poster le commentaire sur le PR
        comment_url = payload["pull_request"]["comments_url"]
        data = {"body": f"🤖 AI Code Review\n{review_text}"}
        requests.post(comment_url, headers=headers, json=data)

        print("AI review posted!")

    return {"status": "ok"}
